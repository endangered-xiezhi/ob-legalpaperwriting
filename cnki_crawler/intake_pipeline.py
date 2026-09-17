"""知网数据处理与流水线助手 (CNKI Intake Pipeline)

负责：
1. 详情页与 EndNote 官方导出字段的标准化解析；
2. 生成统一稳定的全局文献记录 ID；
3. 输出高保真 JSON 元数据清单；
4. 利用 PyMuPDF (fitz) 提取带 [[PDF_PAGE:n]] 标记的分页 TXT 与页码映射索引；
5. 可选联动 Obsidian 知识库生成/增量更新待审核论文卡片。
"""

from __future__ import annotations

import hashlib
import html
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

STUB_MARKER = "<!-- LEXTRACE:GENERATED-STUB -->"
PRIVATE_USE = re.compile(r"[\ue000-\uf8ff]")


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def safe_filename(value: str, fallback: str = "未命名论文") -> str:
    value = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "", clean_text(value))
    value = value.rstrip(". ")
    return value[:150] or fallback


def clean_single_author(raw: str) -> str:
    """清理知网作者姓名中的机构/身份角标、数字、逗号及上标符号。"""
    raw = clean_text(raw)
    # 纯上标/数字/标点符号（例如 "1,", "1,2", "¹²", "1"），直接舍弃
    if re.fullmatch(r"[\d\s,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰\(\)\[\]（）*#]+", raw):
        return ""
    # 剥离末尾的机构/身份脚注标记，如 "(1)", "[1]", "1,", "1,2,", "1", "¹²" 等
    cleaned = re.sub(r"[\(（\[【]\s*[\d,，、\s]+\s*[\)）\]】]$", "", raw)
    cleaned = re.sub(r"[\s\d,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰*#]+$", "", cleaned)
    # 剥离前导标点或序号（如 "1. 张三"）
    cleaned = re.sub(r"^[\s\d,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰*#]+", "", cleaned)
    return cleaned.strip()


def normalize_authors(value: Any) -> list[str]:
    """统一规范作者姓名列表：拆分多作者、去除机构角标、去重并保序。"""
    if isinstance(value, str):
        raw_items = re.split(r"[;,；，、\n/]+", value)
    elif isinstance(value, list):
        raw_items = [item.get("name", "") if isinstance(item, dict) else item for item in value]
    else:
        raw_items = []
    
    authors: list[str] = []
    for item in raw_items:
        # 若单个 item 内含有逗号分隔（如 "俞祺, 俞祺1,"）
        sub_items = re.split(r"[,，、;；/]+", str(item)) if ("," in str(item) or "，" in str(item)) else [str(item)]
        for sub in sub_items:
            name = clean_single_author(sub)
            if name and name not in authors:
                authors.append(name)
    return authors


def parse_endnote(raw: str) -> dict[str, Any]:
    """解析知网 GetExport 接口返回的标准 EndNote 字段。"""
    if not raw:
        return {}
    text = html.unescape(re.sub(r"<br\s*/?>", "\n", raw, flags=re.I))
    text = re.sub(r"<[^>]+>", "", text)
    fields: dict[str, list[str]] = {}
    for line in text.splitlines():
        match = re.match(r"^%([A-Za-z0-9@])\s*(.*)$", line.strip())
        if match:
            fields.setdefault(match.group(1).upper(), []).append(clean_text(match.group(2)))

    date_value = next(iter(fields.get("D", [])), "")
    year_match = re.search(r"(?:19|20)\d{2}", date_value)
    keywords: list[str] = []
    for value in fields.get("K", []):
        keywords.extend(part for part in re.split(r"[;；,，]+", value) if clean_text(part))
    return {
        "title": next(iter(fields.get("T", [])), ""),
        "authors": normalize_authors(fields.get("A", [])),
        "journal": next(iter(fields.get("J", [])), ""),
        "year": year_match.group(0) if year_match else "",
        "volume": next(iter(fields.get("V", [])), ""),
        "issue": next(iter(fields.get("N", [])), ""),
        "page_range": next(iter(fields.get("P", [])), "").replace("–", "-"),
        "keywords": [clean_text(item) for item in keywords if clean_text(item)],
        "abstract": " ".join(fields.get("X", [])),
        "doi": next(iter(fields.get("R", [])), "").removeprefix("doi:").strip(),
        "url": next(iter(fields.get("U", [])), ""),
        "issn": next(iter(fields.get("@", [])), ""),
    }


def parse_publication_info(value: str) -> dict[str, str]:
    """从详情页的发表信息文本中正则提取年、卷、期、页码。"""
    value = clean_text(value)
    result = {"year": "", "volume": "", "issue": "", "page_range": ""}
    year = re.search(r"(?:19|20)\d{2}", value)
    if year:
        result["year"] = year.group(0)
    volume = re.search(r"(?:第\s*)?(\d+)\s*卷", value)
    if volume:
        result["volume"] = volume.group(1)
    issue = re.search(r"(?:第\s*)?(\d+)\s*期", value) or re.search(r"\((\d+)\)", value)
    if issue:
        result["issue"] = issue.group(1).lstrip("0") or "0"
    pages = (
        re.search(r"(?:页码[：:]\s*|[：:,，\s]第?\s*)(\d+)\s*[-–—]\s*(\d+)\s*页?", value)
        or re.search(r"(\d+)\s*[-–—]\s*(\d+)", value)
    )
    if pages:
        result["page_range"] = f"{pages.group(1)}-{pages.group(2)}"
    return result


def merge_metadata(*sources: dict[str, Any]) -> dict[str, Any]:
    """将检索行、详情页与 EndNote 导出的多源元数据高保真合并。"""
    merged: dict[str, Any] = {}
    for source in sources:
        for key, value in source.items():
            if value in (None, "", [], {}):
                continue
            if key in {"authors", "keywords", "affiliations"}:
                existing = merged.get(key, [])
                combined = list(existing) if isinstance(existing, list) else []
                for item in value if isinstance(value, list) else [value]:
                    if item not in combined:
                        combined.append(item)
                merged[key] = combined
            elif isinstance(value, str):
                merged[key] = clean_text(value)
            else:
                merged[key] = value
    merged["authors"] = normalize_authors(merged.get("authors", []))
    merged.update({
        key: value
        for key, value in parse_publication_info(merged.get("publication_info", "")).items()
        if value and not merged.get(key)
    })
    merged["record_id"] = record_id(merged)
    return merged


def record_id(metadata: dict[str, Any]) -> str:
    """生成稳定、具备全局唯一性的文献记录标识。"""
    cnki_id = clean_text(metadata.get("cnki_id") or metadata.get("filename") or metadata.get("export_id"))
    if cnki_id:
        compact = re.sub(r"[^A-Za-z0-9_-]", "", cnki_id)
        return f"CNKI-{compact}"[:96]
    doi = clean_text(metadata.get("doi")).lower()
    if doi:
        return "DOI-" + hashlib.sha256(doi.encode("utf-8")).hexdigest()[:16]
    identity = "|".join([
        clean_text(metadata.get("title")).lower(),
        "|".join(normalize_authors(metadata.get("authors", []))).lower(),
        clean_text(metadata.get("year")),
    ])
    return "LTX-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


def citation_template(metadata: dict[str, Any]) -> str:
    """根据《法学引注手册（2019）》标准生成引注占位样板。"""
    authors = "、".join(normalize_authors(metadata.get("authors", []))) or "作者待核"
    title = clean_text(metadata.get("title")) or "题名待核"
    journal = clean_text(metadata.get("journal")) or "刊物待核"
    year = clean_text(metadata.get("year")) or "年份待核"
    issue = clean_text(metadata.get("issue")) or "期号待核"
    return f"{authors}：《{title}》，载《{journal}》{year}年第{issue}期，第{{pinpoint_page}}页。"


def missing_fields(metadata: dict[str, Any]) -> list[str]:
    labels = {
        "title": "题名",
        "authors": "作者",
        "journal": "刊物",
        "year": "年份",
        "issue": "期号",
        "page_range": "起止页",
    }
    return [label for key, label in labels.items() if not metadata.get(key)]


def yaml_scalar(value: Any) -> str:
    if value is None:
        return '""'
    return json.dumps(str(value), ensure_ascii=False)


def yaml_list(key: str, values: list[Any]) -> list[str]:
    lines = [f"{key}:"]
    if not values:
        return [f"{key}: []"]
    lines.extend(f"  - {yaml_scalar(value)}" for value in values)
    return lines


def render_frontmatter(metadata: dict[str, Any], created_at: str) -> str:
    missing = missing_fields(metadata)
    metadata_status = "ready" if not missing else "partial"
    citation_status = "metadata_ready" if not missing else "blocked"
    warnings: list[str] = []
    if missing:
        warnings.append("缺失引注字段：" + "、".join(missing))
    if clean_text(metadata.get("ingest_warning")):
        warnings.append(clean_text(metadata["ingest_warning"]))
    warning = "；".join(warnings)
    # 计算规范的 PDF 内部双链名称
    pdf_source = clean_text(metadata.get('pdf_path') or metadata.get('source_pdf') or '')
    if pdf_source:
        pdf_file = Path(pdf_source).name
    else:
        stem = safe_filename(clean_text(metadata.get('title') or ''))
        suffix = str(metadata.get('record_id', ''))[-8:]
        pdf_file = f"{stem}__{suffix}.pdf" if stem else ""
    pdf_link = f"[[{pdf_file}]]" if pdf_file else ""

    lines = [
        "---",
        "schema_version: 2",
        f"record_id: {yaml_scalar(metadata['record_id'])}",
        'record_status: "intake"',
        f"metadata_status: {yaml_scalar(metadata_status)}",
        'screening_status: "pending"',
        'analysis_status: "not_started"',
        'relation_status: "not_started"',
        f"citation_status: {yaml_scalar(citation_status)}",
        f"title: {yaml_scalar(metadata.get('title', ''))}",
        *yaml_list("author", normalize_authors(metadata.get("authors", []))),
        f"year: {yaml_scalar(metadata.get('year', ''))}",
        f"journal: {yaml_scalar(metadata.get('journal', ''))}",
        f"volume: {yaml_scalar(metadata.get('volume', ''))}",
        f"issue: {yaml_scalar(metadata.get('issue', ''))}",
        f"page_range: {yaml_scalar(metadata.get('page_range', ''))}",
        f"doi: {yaml_scalar(metadata.get('doi', ''))}",
        f"issn: {yaml_scalar(metadata.get('issn', ''))}",
        f"cnki_id: {yaml_scalar(metadata.get('cnki_id', ''))}",
        *yaml_list("original_keywords", metadata.get("keywords", []) if isinstance(metadata.get("keywords"), list) else []),
        *yaml_list("author_affiliation", metadata.get("affiliations", []) if isinstance(metadata.get("affiliations"), list) else []),
        'primary_domain: ""',
        f"source_url: {yaml_scalar(metadata.get('detail_url') or metadata.get('url', ''))}",
        f"source_pdf: {yaml_scalar(pdf_file)}",
        f"pdf_link: {yaml_scalar(pdf_link)}",
        f"source_txt: {yaml_scalar(metadata.get('txt_path', ''))}",
        f"page_index_path: {yaml_scalar(metadata.get('page_index_path', ''))}",
        f"cnki_citation_count: {yaml_scalar(metadata.get('citation_count', ''))}",
        f"cnki_download_count: {yaml_scalar(metadata.get('download_count', ''))}",
        f"citation_template: {yaml_scalar(citation_template(metadata))}",
        'metadata_provenance: "cnki_detail_and_export"',
        'review_status: "intake_pending"',
        f"created_at: {yaml_scalar(created_at)}",
        f"updated_at: {yaml_scalar(now_iso())}",
        f"warning: {yaml_scalar(warning)}",
        "---",
    ]
    return "\n".join(lines)


def render_stub_body(metadata: dict[str, Any]) -> str:
    title = clean_text(metadata.get("title")) or "待核题名"
    abstract = clean_text(metadata.get("abstract"))
    keywords = "；".join(metadata.get("keywords", [])) if isinstance(metadata.get("keywords"), list) else ""
    pdf_source = clean_text(metadata.get('pdf_path') or metadata.get('source_pdf') or '')
    if pdf_source:
        pdf_file = Path(pdf_source).name
    else:
        stem = safe_filename(clean_text(metadata.get('title') or ''))
        suffix = str(metadata.get('record_id', ''))[-8:]
        pdf_file = f"{stem}__{suffix}.pdf" if stem else ""
    pdf_link = f"[[{pdf_file}]]" if pdf_file else "待关联"

    return f"""
{STUB_MARKER}

# {title}

> [!warning] 新采集样板
> 本页由知网采集器创建，尚未正式纳入论文库。元数据、观点、关系和引注均须人工审核。

> [!info] 📄 原文 PDF 深度定位与批注 (PDF++)
> - 原文双链：{pdf_link}
> - 联动技巧：配合已启用的 **PDF++** 插件，按住 `Option` (Mac) 点击上方双链即可右侧分屏对照阅读；在 PDF 中划词高亮即可一键复制带页码与选区的双向精准反链。

## 一、标题摘要初筛

- 筛选结论：待定
- 筛选理由：
- 与研究画像的相关性：

## 二、原文摘要

{abstract or '待采集或待核验。'}

## 三、原文关键词

{keywords or '待采集或待核验。'}

## 四、论文基本问题

<!-- AGENT:BEGIN research-question -->
待分析。
<!-- AGENT:END research-question -->

## 五、核心概念与规范依据

<!-- AGENT:BEGIN concepts -->
待分析。
<!-- AGENT:END concepts -->

## 六、全文结构化卡片

### 问题的提出

### 问题的分析

### 问题的解决

### 研究方法与适用边界

## 七、可核验观点卡

<!-- 每个观点必须绑定原文摘录、PDF页码、印刷页码和核验状态。 -->

## 八、文献关系

<!-- 区分直接引证、正文明确对话和系统构造的平行比较。 -->

## 九、引注

- 法学引注样板：`{citation_template(metadata)}`
- 具体观点页码：待核验

## 十、Agent处理记录

- 当前状态：尚未交给 Agent
""".strip() + "\n"


def find_existing_stub(stub_dir: Path, metadata: dict[str, Any]) -> Path | None:
    target_id = metadata["record_id"]
    doi = clean_text(metadata.get("doi")).lower()
    cnki_id = clean_text(metadata.get("cnki_id"))
    if not stub_dir.exists():
        return None
    for path in stub_dir.glob("*.md"):
        try:
            head = path.read_text(encoding="utf-8", errors="replace")[:12000]
        except OSError:
            continue
        if f"record_id: {yaml_scalar(target_id)}" in head:
            return path
        if doi and re.search(rf"^doi:\s*[\"']?{re.escape(doi)}[\"']?\s*$", head, re.I | re.M):
            return path
        if cnki_id and re.search(rf"^cnki_id:\s*[\"']?{re.escape(cnki_id)}[\"']?\s*$", head, re.M):
            return path
    return None


def upsert_obsidian_stub(metadata: dict[str, Any], stub_dir: Path, existing_path: Path | None = None) -> tuple[Path, bool]:
    """在指定 Obsidian 论文库目录创建或更新样板（绝不覆盖已完成人工核验的笔记）。"""
    try:
        stub_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.warning("创建 Obsidian 样板目录失败：%s", exc)
        return Path(), False

    metadata = merge_metadata(metadata)
    path = existing_path or find_existing_stub(stub_dir, metadata)
    created = path is None
    if path is None:
        stem = safe_filename(metadata.get("title", ""))
        path = stub_dir / f"{stem}.md"
        if path.exists():
            path = stub_dir / f"{stem}__{metadata['record_id'][-8:]}.md"
        created_at = now_iso()
        body = render_stub_body(metadata)
    else:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        if STUB_MARKER not in text or re.search(r'^record_status:\s*["\']?verified["\']?\s*$', text, re.M):
            return path, False
        end = text.find("\n---", 4) if text.startswith("---\n") else -1
        body = text[end + 4 :].lstrip("\n") if end >= 0 else render_stub_body(metadata)
        created_match = re.search(r'^created_at:\s*["\']?([^"\'\n]+)', text, re.M)
        created_at = clean_text(created_match.group(1)) if created_match else now_iso()
    content = render_frontmatter(metadata, created_at) + "\n\n" + body
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)

    # 自动多 Vault 镜像同步（用户实际 Obsidian 仓库、项目仓库与 Codex 备份）
    mirror_dirs = [
        Path.home() / "Downloads" / "Obsidian Vault" / "知识产权" / "论文库",
        Path(__file__).resolve().parent.parent / "vault" / "知识产权" / "论文库",
        Path("/Users/kansang/Documents/Codex/2026-08-08/h/vault/知识产权/论文库"),
    ]
    for mirror_dir in mirror_dirs:
        try:
            if mirror_dir.resolve() != path.parent.resolve() and mirror_dir.parent.exists():
                mirror_dir.mkdir(parents=True, exist_ok=True)
                mirror_file = mirror_dir / path.name
                mirror_tmp = mirror_file.with_suffix(mirror_file.suffix + ".tmp")
                mirror_tmp.write_text(content, encoding="utf-8")
                mirror_tmp.replace(mirror_file)
        except OSError:
            pass

    return path, created


def write_manifest(metadata: dict[str, Any], manifest_dir: Path) -> Path:
    """写入结构化 JSON 清单。"""
    manifest_dir.mkdir(parents=True, exist_ok=True)
    cleaned = {key: value for key, value in metadata.items() if not key.startswith("_")}
    cleaned["record_id"] = metadata.get("record_id") or record_id(metadata)
    cleaned["updated_at"] = now_iso()
    path = manifest_dir / f"{safe_filename(cleaned['record_id'])}.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
    return path


def _page_start(page_range: str) -> int | None:
    match = re.match(r"\s*(\d+)", clean_text(page_range))
    return int(match.group(1)) if match else None


def extract_paginated_text(pdf_path: Path, txt_path: Path, index_path: Path, page_range: str = "") -> dict[str, Any]:
    """利用 PyMuPDF 将 PDF 转换为带显式分页标柱的 TXT，并生成精确页码与字符偏移索引。"""
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import fitz
    except ImportError:
        logger.warning("未安装 PyMuPDF (fitz)，跳过文本分页提取。可通过 pip install PyMuPDF 安装。")
        return {
            "pdf_path": str(pdf_path),
            "txt_path": "",
            "page_count": 0,
            "page_mapping_status": "fitz_not_installed",
            "pages": [],
            "empty_text_pages": [],
            "ocr_required": False,
            "generated_at": now_iso(),
        }

    document = fitz.open(pdf_path)
    chunks: list[str] = []
    pages: list[dict[str, Any]] = []
    empty_pages: list[int] = []
    start_page = _page_start(page_range)
    offset = 0
    try:
        for index, page in enumerate(document):
            blocks = page.get_text("blocks", sort=True)
            page_text = "\n".join(block[4] for block in blocks if len(block) > 6 and block[6] == 0)
            page_text = PRIVATE_USE.sub("", page_text).strip()
            pdf_page = index + 1
            marker = f"[[PDF_PAGE:{pdf_page}]]"
            chunk = marker + "\n" + page_text + "\n"
            chunks.append(chunk)
            if not page_text:
                empty_pages.append(pdf_page)
            pages.append({
                "pdf_page": pdf_page,
                "printed_page_candidate": start_page + index if start_page is not None else None,
                "printed_page_verified": False,
                "char_start": offset,
                "char_end": offset + len(chunk),
            })
            offset += len(chunk) + 1
    finally:
        document.close()

    txt_path.write_text("\n".join(chunks), encoding="utf-8")
    payload = {
        "pdf_path": str(pdf_path),
        "txt_path": str(txt_path),
        "page_count": len(pages),
        "page_mapping_status": "candidate_from_article_range" if start_page is not None else "missing_printed_pages",
        "pages": pages,
        "empty_text_pages": empty_pages,
        "ocr_required": bool(empty_pages),
        "generated_at": now_iso(),
    }
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
