#!/usr/bin/env python3
"""Local bridge for LexTrace Obsidian intake and navigation.

Obsidian is the sole source of truth. This service exposes a derived index,
small note previews, Obsidian deep links and the CNKI launcher. Browsing stays
read-only; writes are limited to crawler-created intake stubs and screening.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shlex
import signal
import subprocess
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


HOST = "127.0.0.1"
PORT = int(os.environ.get("LEXTRACE_BRIDGE_PORT", "8765"))
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = BRIDGE_ROOT / "runtime"
PAPER_SCHEMA_PATH = BRIDGE_ROOT / "paper-schema.json"
def resolve_crawler_root() -> Path:
    env_crawler = os.environ.get("LEXTRACE_CNKI_ROOT")
    if env_crawler:
        candidate = Path(env_crawler).expanduser().resolve()
        if candidate.exists():
            return candidate
    project_crawler = (PROJECT_ROOT / "cnki_crawler").resolve()
    if project_crawler.exists():
        return project_crawler
    fallback = (Path.home() / "Downloads" / "复旦校内" / "大三下" / "ZhiWan_pdf").resolve()
    if fallback.exists():
        return fallback
    return project_crawler


def resolve_vault_root() -> Path:
    env_vault = os.environ.get("LEXTRACE_OBSIDIAN_VAULT")
    if env_vault:
        candidate = Path(env_vault).expanduser().resolve()
        if (candidate / "知识产权").exists():
            try:
                if any((candidate / "知识产权").iterdir()):
                    return candidate
            except OSError:
                pass
    user_vault = (Path.home() / "Downloads" / "Obsidian Vault").resolve()
    if (user_vault / "知识产权").exists():
        try:
            if any((user_vault / "知识产权").iterdir()):
                return user_vault
        except OSError:
            pass
    project_vault = (PROJECT_ROOT / "vault").resolve()
    if (project_vault / "知识产权").exists():
        return project_vault
    return project_vault


CRAWLER_ROOT = resolve_crawler_root()
VAULT_ROOT = resolve_vault_root()
KNOWLEDGE_ROOT = VAULT_ROOT / "知识产权"
OBSIDIAN_CONFIG_PATH = Path(
    os.environ.get(
        "LEXTRACE_OBSIDIAN_CONFIG",
        "~/Library/Application Support/obsidian/obsidian.json",
    )
).expanduser()
ALLOWED_ORIGINS = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}

CANONICAL_DOMAINS = [
    ("知识产权—著作权法", "知识产权/领域/01_著作权法.md"),
    ("专利法", "知识产权/领域/02_专利法.md"),
    ("商标法", "知识产权/领域/03_商标法.md"),
    ("知产相关反不正当竞争", "知识产权/领域/04_知产相关反不正当竞争.md"),
    ("纯反不正当竞争", "知识产权/领域/05_纯反不正当竞争.md"),
    ("数据法、个人信息与算法治理", "知识产权/领域/06_数据法、个人信息与算法治理.md"),
    ("其他知识产权与综合治理", "知识产权/领域/07_其他知识产权与综合治理.md"),
]
CANONICAL_DOMAIN_NAMES = {name for name, _ in CANONICAL_DOMAINS}
QUICK_LINKS = [
    ("研究导航", "知识产权/00_知识产权研究导航.md", "领域、争议与论文的动态入口"),
    ("法规与典型案例", "知识产权/法律法规与典型案例/README.md", "50部知产法规/司法解释与395篇权威案例"),
    ("论文总览", "知识产权/00_知识产权论文总览.md", "全库结构与统计口径"),
    ("近五年趋势", "知识产权/研究趋势/近五年研究趋势总览.md", "库内研究问题的年度演变"),
    ("年度索引", "知识产权/研究趋势/年度论文索引.md", "按发表年份进入论文"),
    ("学者索引", "知识产权/研究趋势/学者观点索引.md", "按作者查找观点与对话"),
    ("整理 SOP", "知识产权/研究趋势/法学论文整理SOP_Agent通用执行手册.md", "新材料整理、核验与入库规范"),
]
RULEBOOK_HUBS = [
    ("商标法及案例库", "知识产权/法律法规与典型案例/商标/商标.md", "商标法87条、行政法规、解释与典型案例"),
    ("专利法及案例库", "知识产权/法律法规与典型案例/专利/专利.md", "专利法82条、实施细则、解释与典型案例"),
    ("著作权法及案例库", "知识产权/法律法规与典型案例/著作权/著作权.md", "著作权法67条、实施条例、解释与典型案例"),
    ("通用规则及案例库", "知识产权/法律法规与典型案例/知识产权通用规则/知识产权通用规则.md", "管辖、证据、保全、惩罚性赔偿等跨域规则"),
    ("植物新品种", "知识产权/法律法规与典型案例/植物新品种/植物新品种.md", "条例49条、司法解释与典型案例"),
    ("最高法审判参考", "知识产权/法律法规与典型案例/_审判参考/法答网精选答问-第33批·知识产权司法保护专题（2025-12-05）.md", "最高法法答网精选答问知识产权司法保护专题"),
]
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")
HEADING = re.compile(r"^(#{1,4})\s*(.+?)\s*$", re.MULTILINE)


def clean_journals(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value[:100]:
        if not isinstance(item, str):
            continue
        name = re.sub(r"[\x00-\x1f]", "", item).strip()
        if 1 <= len(name) <= 80 and name not in result:
            result.append(name)
    return result


def clean_short_text(value: Any, *, maximum: int = 500) -> str:
    text = re.sub(r"[\x00-\x1f]", " ", str(value or "")).strip()
    return re.sub(r"\s+", " ", text)[:maximum]


def safe_knowledge_path(value: Any, *, must_exist: bool = True) -> Path:
    relative = str(value or "").strip().lstrip("/")
    candidate = (VAULT_ROOT / relative).resolve()
    root = KNOWLEDGE_ROOT.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("只允许读取知识产权目录中的笔记")
    if must_exist and not candidate.exists():
        raise ValueError("未找到指定的Obsidian笔记")
    return candidate


def obsidian_vault_identifier() -> str:
    """Return Obsidian's registered vault ID, falling back to the folder name."""
    override = os.environ.get("LEXTRACE_OBSIDIAN_VAULT_ID", "").strip()
    if override:
        return override
    try:
        config = json.loads(OBSIDIAN_CONFIG_PATH.read_text(encoding="utf-8"))
        user_vault_path = (Path.home() / "Downloads" / "Obsidian Vault").resolve()
        for vault_id, entry in config.get("vaults", {}).items():
            registered = Path(str(entry.get("path") or "")).expanduser().resolve()
            if registered == VAULT_ROOT.resolve() or registered == user_vault_path:
                return str(vault_id)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    return VAULT_ROOT.name


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result: dict[str, Any] = {}
    current_list: str | None = None
    for line in text[4:end].splitlines():
        if re.match(r"^\s*-\s+", line) and current_list:
            result.setdefault(current_list, []).append(line.split("-", 1)[1].strip().strip("'\""))
            continue
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not match:
            current_list = None
            continue
        key, raw = match.groups()
        raw = raw.strip()
        if not raw:
            result[key] = []
            current_list = key
        elif raw == "[]":
            result[key] = []
            current_list = None
        else:
            result[key] = raw.strip("'\"")
            current_list = None
    return result


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    return text[end + 4 :] if end >= 0 else text


def list_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [] if value in (None, "") else [str(value)]


def clean_single_author(raw: str) -> str:
    raw = clean_short_text(raw, maximum=100)
    if re.fullmatch(r"[\d\s,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰\(\)\[\]（）*#]+", raw):
        return ""
    cleaned = re.sub(r"[\(（\[【]\s*[\d,，、\s]+\s*[\)）\]】]$", "", raw)
    cleaned = re.sub(r"[\s\d,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰*#]+$", "", cleaned)
    cleaned = re.sub(r"^[\s\d,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰*#]+", "", cleaned)
    return cleaned.strip()


def normalize_authors(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_items = re.split(r"[;,；，、\n/]+", value)
    elif isinstance(value, list):
        raw_items = [item.get("name", "") if isinstance(item, dict) else item for item in value]
    else:
        raw_items = []
    authors = []
    for item in raw_items:
        sub_items = re.split(r"[,，、;；/]+", str(item)) if ("," in str(item) or "，" in str(item)) else [str(item)]
        for sub in sub_items:
            name = clean_single_author(sub)
            if name and name not in authors:
                authors.append(name)
    return authors


def plain_text(value: str) -> str:
    value = re.sub(r"```.*?```", " ", value, flags=re.DOTALL)
    value = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda match: match.group(2) or match.group(1), value)
    value = re.sub(r"[`*_>#=|~-]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def extract_summary(body: str) -> str:
    for heading in ("原文摘要", "一句话主旨", "通俗摘要"):
        match = re.search(rf"^##\s*{re.escape(heading)}\s*$\n(.*?)(?=^##\s|\Z)", body, flags=re.MULTILINE | re.DOTALL)
        if match:
            summary = plain_text(match.group(1))
            if summary:
                return summary[:650]
    return plain_text(body)[:360]


def markdown_paths() -> list[Path]:
    if not KNOWLEDGE_ROOT.exists():
        return []
    return [
        path
        for path in sorted(KNOWLEDGE_ROOT.rglob("*.md"))
        if not any(part.startswith(".") for part in path.relative_to(VAULT_ROOT).parts)
    ]


def vault_version() -> dict[str, Any]:
    paths = markdown_paths()
    max_modified = 0
    total_size = 0
    for path in paths:
        try:
            stat = path.stat()
        except OSError:
            continue
        max_modified = max(max_modified, stat.st_mtime_ns)
        total_size += stat.st_size
    raw = f"{len(paths)}:{max_modified}:{total_size}".encode("utf-8")
    return {
        "version": hashlib.sha256(raw).hexdigest()[:20],
        "count": len(paths),
        "maxModifiedNs": max_modified,
    }


def is_navigation_excluded(relative: str) -> bool:
    parts = Path(relative).parts
    return "_archive" in parts or "_reading_logs" in parts or "交接文档" in parts


IP_PATTERNS = [
    r"知识产权", r"专利", r"商标", r"著作权", r"版权", r"商业秘密", r"反不正当竞争",
    r"独创性", r"合理使用", r"优先权", r"作品", r"知产", r"NFT", r"WAPI", r"NPE",
    r"算法治理", r"数据法", r"数据权益", r"大模型", r"人工智能生成", r"地理标志",
    r"商业标识", r"域名", r"植物新品种", r"集成电路", r"开源", r"商业诋毁",
    r"信息网络传播权", r"标准必要专利", r"FRAND", r"网络侵权", r"避风港",
]
IP_REGEX = re.compile("|".join(IP_PATTERNS), re.I)
IP_JOURNALS = {
    "知识产权", "版权理论与实务", "中国版权", "中华商标", "北大知识产权评论",
    "中国科技法律评论", "电子知识产权", "知识产权研究",
}


def detect_discipline(metadata: dict[str, Any], title: str, body: str) -> tuple[str, str]:
    domain = str(metadata.get("primary_domain") or "").strip()
    if domain:
        if domain in CANONICAL_DOMAIN_NAMES or any(
            k in domain for k in ("著作权", "专利", "商标", "知产", "不正当竞争", "数据法", "算法", "知识产权")
        ):
            return "ip", "知识产权法"
        return "other", "其他部门法"
    journal = str(metadata.get("journal") or "").strip()
    if journal in IP_JOURNALS:
        return "ip", "知识产权法"
    keywords = " ".join(list_value(metadata.get("original_keywords")) or [])
    probe_text = f"{title} {journal} {keywords} {body[:600]}"
    if IP_REGEX.search(title) or IP_REGEX.search(probe_text):
        return "ip", "知识产权法"
    return "other", "其他部门法"


def note_record(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    metadata = parse_frontmatter(text)
    body = strip_frontmatter(text).strip()
    heading = HEADING.search(body)
    resolved_path = path.resolve()
    resolved_vault = VAULT_ROOT.resolve()
    relative = resolved_path.relative_to(resolved_vault).as_posix()
    title = str(metadata.get("title") or (heading.group(2) if heading else path.stem)).strip()
    links: list[dict[str, str]] = []
    seen_targets: set[str] = set()
    for target, label in WIKI_LINK.findall(body):
        target = target.strip().rstrip("\\")
        if target and target not in seen_targets:
            links.append({"target": target, "label": (label or target).strip()})
            seen_targets.add(target)
    headings = [
        {"level": len(level), "text": heading_text.strip(" #")}
        for level, heading_text in HEADING.findall(body)
    ][:45]
    stat = path.stat()
    authors = normalize_authors(list_value(metadata.get("author")))
    warning = str(metadata.get("warning") or "").strip()
    domain = str(metadata.get("primary_domain") or "").strip()
    record_status = str(metadata.get("record_status") or "").strip()
    is_paper = relative.startswith("知识产权/论文库/")
    has_source = bool(metadata.get("source_pdf") or metadata.get("source_txt"))
    required = all([
        metadata.get("title"),
        authors,
        metadata.get("year"),
        metadata.get("journal"),
        domain,
        has_source,
        metadata.get("review_status"),
    ])
    legacy_formal = bool(is_paper and required and not warning)
    is_formal = bool(
        is_paper
        and not warning
        and (record_status == "verified" or (not record_status and legacy_formal))
    )
    discipline, discipline_label = detect_discipline(metadata, title, body)
    return {
        "path": relative,
        "title": title,
        "folder": resolved_path.parent.relative_to(resolved_vault).as_posix(),
        "type": str(metadata.get("type") or ("论文" if is_paper else "笔记")),
        "authors": authors,
        "year": str(metadata.get("year") or ""),
        "journal": str(metadata.get("journal") or ""),
        "domain": domain,
        "discipline": discipline,
        "disciplineLabel": discipline_label,
        "status": str(metadata.get("review_status") or record_status or metadata.get("status") or ""),
        "recordStatus": record_status or ("legacy_verified" if legacy_formal else "legacy_pending"),
        "metadataStatus": str(metadata.get("metadata_status") or ""),
        "screeningStatus": str(metadata.get("screening_status") or ""),
        "analysisStatus": str(metadata.get("analysis_status") or ""),
        "relationStatus": str(metadata.get("relation_status") or ""),
        "citationStatus": str(metadata.get("citation_status") or ""),
        "recordId": str(metadata.get("record_id") or ""),
        "issue": str(metadata.get("issue") or ""),
        "volume": str(metadata.get("volume") or ""),
        "pageRange": str(metadata.get("page_range") or ""),
        "doi": str(metadata.get("doi") or ""),
        "cnkiId": str(metadata.get("cnki_id") or ""),
        "sourcePdf": str(metadata.get("source_pdf") or ""),
        "pdfLink": str(metadata.get("pdf_link") or ""),
        "warning": warning,
        "topics": list_value(metadata.get("trend_topics")),
        "paths": list_value(metadata.get("research_paths")),
        "summary": extract_summary(body),
        "modified": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="minutes"),
        "links": links[:100],
        "headings": headings,
        "isPaper": is_paper,
        "isFormal": is_formal,
        "isExcluded": record_status == "excluded",
        "isIntake": record_status in {"intake", "agent_draft"},
        "isCanonicalDomain": domain in CANONICAL_DOMAIN_NAMES,
    }


_last_metadata_sync_time = 0.0


def sync_crawler_metadata_stubs() -> int:
    """自动扫描各爬虫元数据目录，将尚未生成 Obsidian 笔记的文献自动转换为样板笔记，并保持双仓库同步。"""
    try:
        sys.path.insert(0, str(CRAWLER_ROOT))
        import intake_pipeline  # type: ignore
    except Exception as exc:
        return 0

    candidate_metadata_dirs = [
        CRAWLER_ROOT / "metadata",
        PROJECT_ROOT / "cnki_crawler" / "metadata",
        Path("/Users/kansang/Documents/Codex/2026-08-08/h/cnki_crawler/metadata"),
        Path("/Users/kansang/Downloads/claude 使用专用/cnki_crawler/metadata"),
    ]

    target_vault_dirs = [
        KNOWLEDGE_ROOT / "论文库",
    ]
    user_vault_paper = (Path.home() / "Downloads" / "Obsidian Vault" / "知识产权" / "论文库").resolve()
    if user_vault_paper.exists() and user_vault_paper != (KNOWLEDGE_ROOT / "论文库").resolve():
        target_vault_dirs.append(user_vault_paper)
    project_vault_paper = (PROJECT_ROOT / "vault" / "知识产权" / "论文库").resolve()
    if project_vault_paper.exists() and project_vault_paper != (KNOWLEDGE_ROOT / "论文库").resolve():
        target_vault_dirs.append(project_vault_paper)

    synced_count = 0
    seen_files: set[str] = set()
    for meta_dir in candidate_metadata_dirs:
        if not meta_dir.exists():
            continue
        try:
            json_files = list(meta_dir.glob("*.json"))
        except OSError:
            continue
        for json_path in json_files:
            if json_path.name in seen_files:
                continue
            seen_files.add(json_path.name)
            try:
                data = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
                if not data.get("title"):
                    continue
                merged = intake_pipeline.merge_metadata(data)
                for target_dir in target_vault_dirs:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    existing = intake_pipeline.find_existing_stub(target_dir, merged)
                    if not existing:
                        stub_path, created = intake_pipeline.upsert_obsidian_stub(data, target_dir)
                        if created:
                            synced_count += 1
            except Exception:
                continue
    if synced_count > 0:
        print(f"[LexTrace] 自动同步：已将 {synced_count} 篇新抓取知网文献转写为 Obsidian 样板卡片。")
    return synced_count


def ensure_crawler_stubs_synced() -> int:
    global _last_metadata_sync_time
    now = datetime.now().timestamp()
    if now - _last_metadata_sync_time < 3.0:
        return 0
    _last_metadata_sync_time = now
    return sync_crawler_metadata_stubs()


def scan_vault() -> list[dict[str, Any]]:
    ensure_crawler_stubs_synced()
    records = []
    for path in markdown_paths():
        try:
            records.append(note_record(path))
        except OSError:
            continue
    return records


def navigation_payload() -> dict[str, Any]:
    records = scan_vault()
    by_path = {record["path"]: record for record in records}
    papers = [
        record for record in records
        if record["isPaper"] and not record["isExcluded"] and not is_navigation_excluded(record["path"])
    ]
    formal = [record for record in papers if record["isFormal"]]
    pending = [record for record in papers if not record["isFormal"]]
    intake = [record for record in papers if record["isIntake"]]
    excluded = [record for record in records if record["isPaper"] and record["isExcluded"]]
    inbox = [record for record in records if record["path"].startswith("知识产权/_智能体待审核/")]
    unclassified = [record for record in papers if record["domain"] and not record["isCanonicalDomain"]]
    domains = []
    for name, path in CANONICAL_DOMAINS:
        domain_note = by_path.get(path)
        domains.append({
            "name": name,
            "path": path,
            "count": sum(1 for paper in formal if paper["domain"] == name),
            "summary": domain_note["summary"] if domain_note else "",
        })
    controversies = [
        record for record in records
        if record["folder"] == "知识产权/研究趋势/争议专题"
    ]
    research_paths = [
        record for record in records
        if record["folder"] == "知识产权/清华研究路径" and not record["title"].startswith("清华知识产权研究路径总览")
    ]
    rules_and_cases = [
        record for record in records
        if record["path"].startswith("知识产权/法律法规与典型案例/")
    ]
    searchable = [record for record in records if not is_navigation_excluded(record["path"])]
    version = vault_version()
    return {
        "ok": True,
        "vaultName": VAULT_ROOT.name,
        "vaultRoot": str(VAULT_ROOT),
        "vaultId": obsidian_vault_identifier(),
        "scope": "知识产权",
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "version": version["version"],
        "stats": {
            "notes": len(searchable),
            "papers": len(papers),
            "formal": len(formal),
            "pending": len(pending) + len(inbox),
            "intake": len(intake),
            "excluded": len(excluded),
            "unclassified": len(unclassified),
            "domains": len(domains),
            "rulesAndCases": len(rules_and_cases),
        },
        "quickLinks": [
            {"title": title, "path": path, "caption": caption}
            for title, path, caption in QUICK_LINKS if path in by_path
        ],
        "rulebookHubs": [
            {"title": title, "path": path, "caption": caption}
            for title, path, caption in RULEBOOK_HUBS if path in by_path
        ],
        "domains": domains,
        "controversies": sorted(controversies, key=lambda record: record["title"]),
        "researchPaths": sorted(research_paths, key=lambda record: record["title"]),
        "recent": sorted(formal, key=lambda record: record["modified"], reverse=True)[:20],
        "pending": sorted(pending + inbox, key=lambda record: record["modified"], reverse=True)[:100],
        "intake": sorted(intake, key=lambda record: record["modified"], reverse=True)[:500],
        "unclassified": sorted(unclassified, key=lambda record: record["modified"], reverse=True)[:100],
        "searchNotes": searchable,
    }


def resolve_note_links(note: dict[str, Any], records: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_without_suffix = {str(Path(record["path"]).with_suffix("")): record["path"] for record in records}
    by_stem: dict[str, str] = {}
    by_title: dict[str, str] = {}
    for record in records:
        by_stem.setdefault(Path(record["path"]).stem, record["path"])
        by_title.setdefault(record["title"], record["path"])
    parent = Path(note["path"]).parent
    resolved = []
    for link in note["links"]:
        target = link["target"].strip().removesuffix(".md")
        candidates = [target, str(parent / target)]
        path = next((by_without_suffix[candidate] for candidate in candidates if candidate in by_without_suffix), "")
        if not path:
            path = by_stem.get(Path(target).name, by_title.get(target, ""))
        resolved.append({**link, "path": path})
    return resolved


def note_payload(relative: str) -> dict[str, Any]:
    path = safe_knowledge_path(relative)
    if path.suffix.lower() != ".md":
        raise ValueError("只支持读取Markdown笔记")
    note = note_record(path)
    records = scan_vault()
    target_stem = path.stem
    target_without_suffix = path.resolve().relative_to(VAULT_ROOT.resolve()).with_suffix("").as_posix()
    backlinks = []
    for candidate in records:
        if candidate["path"] == note["path"]:
            continue
        if any(
            link["target"].removesuffix(".md").rstrip("/") in {target_stem, target_without_suffix}
            or link["target"].removesuffix(".md").rstrip("/").endswith("/" + target_stem)
            for link in candidate["links"]
        ):
            backlinks.append({"path": candidate["path"], "title": candidate["title"]})
    note["links"] = resolve_note_links(note, records)
    note["backlinks"] = backlinks[:100]
    note["localPath"] = str(path.resolve())
    return {"ok": True, "note": note}


def update_intake_screening(relative: str, decision: str, reason: str = "", domain: str = "") -> dict[str, Any]:
    if decision not in {"included", "excluded", "pending"}:
        raise ValueError("筛选结论必须是 included、excluded 或 pending")
    path = safe_knowledge_path(relative)
    if path.suffix.lower() != ".md":
        raise ValueError("只支持更新Markdown样板")
    text = path.read_text(encoding="utf-8", errors="replace")
    if "<!-- LEXTRACE:GENERATED-STUB -->" not in text:
        raise ValueError("只能更新由LexTrace创建的待审核样板")
    record_status = "excluded" if decision == "excluded" else "intake"
    updates: dict[str, Any] = {
        "screening_status": decision,
        "record_status": record_status,
        "screening_reason": clean_short_text(reason, maximum=500),
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if domain:
        updates["primary_domain"] = clean_short_text(domain, maximum=100)
    for key, value in updates.items():
        rendered = json.dumps(value, ensure_ascii=False)
        pattern = rf"^{re.escape(key)}:\s*.*$"
        if re.search(pattern, text, flags=re.MULTILINE):
            text = re.sub(pattern, lambda _: f"{key}: {rendered}", text, count=1, flags=re.MULTILINE)
        else:
            end = text.find("\n---", 4)
            if end < 0:
                raise ValueError("样板YAML格式不完整")
            text = text[:end] + f"\n{key}: {rendered}" + text[end:]
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)

    # 镜像同步至其他候选库（仅在非临时测试环境下）
    is_test_env = any(t in str(VAULT_ROOT).lower() for t in ("tmp", "temp", "pytest"))
    if not is_test_env:
        mirror_dirs = [
            Path.home() / "Downloads" / "Obsidian Vault" / "知识产权" / "论文库",
            PROJECT_ROOT / "vault" / "知识产权" / "论文库",
            Path("/Users/kansang/Documents/Codex/2026-08-08/h/vault/知识产权/论文库"),
        ]
        for mirror_dir in mirror_dirs:
            try:
                if mirror_dir.resolve() != path.parent.resolve() and mirror_dir.parent.exists():
                    mirror_dir.mkdir(parents=True, exist_ok=True)
                    mirror_file = mirror_dir / path.name
                    mirror_tmp = mirror_file.with_suffix(mirror_file.suffix + ".tmp")
                    mirror_tmp.write_text(text, encoding="utf-8")
                    mirror_tmp.replace(mirror_file)
            except OSError:
                pass

    return {"ok": True, "message": "筛选结论已写入样板", "recordStatus": record_status}


def render_legal_citation(relative: str, mode: str, pinpoint: str = "") -> dict[str, Any]:
    if mode not in {"direct", "paraphrase", "general", "short"}:
        raise ValueError("引注模式不正确")
    pinpoint = clean_short_text(pinpoint, maximum=30)
    if pinpoint and not re.fullmatch(r"\d+(?:\s*[-–—、,，]\s*\d+)*", pinpoint):
        raise ValueError("页码只能填写数字、连接号或逗号")
    path = safe_knowledge_path(relative)
    metadata = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    authors = list_value(metadata.get("author"))
    author_str = "、".join(authors) or ""
    title_str = str(metadata.get("title") or "").strip()
    journal_str = str(metadata.get("journal") or "").strip()
    year_str = str(metadata.get("year") or "").strip()
    issue_str = str(metadata.get("issue") or "").strip()

    if mode == "short":
        if not authors:
            return {"ok": False, "error": "引注字段待补：作者", "missing": ["作者"]}
        if not pinpoint:
            return {"ok": False, "error": "前引文须填写具体页码", "missing": ["具体页码"]}
        citation = f"{author_str}前引文，第{pinpoint}页。"
        short_citation = citation
    else:
        missing = []
        if not authors:
            missing.append("作者")
        if not title_str:
            missing.append("题名")
        if not journal_str:
            missing.append("刊物")
        if not year_str:
            missing.append("年份")
        if mode in {"direct", "paraphrase"} and not pinpoint:
            missing.append("具体页码")
        if missing:
            return {"ok": False, "error": "引注字段待补：" + "、".join(missing), "missing": missing}

        prefix = "参见" if mode == "paraphrase" else ""
        period_info = f"{year_str}年第{issue_str}期" if issue_str else f"{year_str}年"
        citation = f"{prefix}{author_str}：《{title_str}》，载《{journal_str}》{period_info}"
        if pinpoint:
            citation += f"，第{pinpoint}页"
        citation += "。"

        short_citation = f"{author_str}前引文"
        if pinpoint:
            short_citation += f"，第{pinpoint}页"
        short_citation += "。"

    cite_id = str(metadata.get("record_id") or hashlib.sha256(relative.encode("utf-8")).hexdigest()[:12])
    return {
        "ok": True,
        "citation": citation,
        "shortCitation": short_citation,
        "wordFootnote": citation,
        "obsidianMarker": f"[^{cite_id}]",
        "obsidianDefinition": f"[^{cite_id}]: {citation}",
        "markdownFootnote": f"[^{cite_id}]: {citation}",
        "verification": "metadata_ready" if not pinpoint else "pinpoint_unverified",
    }


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "LexTraceBridge/0.4"

    def log_message(self, message: str, *args: Any) -> None:
        print(f"[LexTrace] {self.address_string()} - {message % args}")

    def _origin_allowed(self) -> bool:
        origin = self.headers.get("Origin")
        if origin is None or origin in ALLOWED_ORIGINS:
            return True
        return bool(re.match(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$", origin))

    def _headers(self, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        origin = self.headers.get("Origin")
        if origin and self._origin_allowed():
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def _json(self, payload: dict[str, Any], status: int = 200) -> None:
        self._headers(status)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _read_payload(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        if content_length > 1_000_000:
            raise ValueError("请求内容过大")
        payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("请求格式错误")
        return payload

    def do_OPTIONS(self) -> None:  # noqa: N802
        if not self._origin_allowed():
            self._json({"error": "origin not allowed"}, 403)
            return
        self._headers(204)

    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            if parsed.path == "/api/health":
                self._json({
                    "ok": True,
                    "crawlerFound": (CRAWLER_ROOT / "pdf_downloader.py").exists(),
                    "vaultFound": KNOWLEDGE_ROOT.exists(),
                    "obsidianVaultId": obsidian_vault_identifier(),
                    "readOnly": False,
                    "readOnlyMirror": True,
                    "writeScope": ["cnki_intake_stub", "intake_screening_status"],
                })
            elif parsed.path == "/api/vault/version":
                self._json({"ok": True, **vault_version()})
            elif parsed.path in {"/api/vault/navigation", "/api/vault/index"}:
                self._json(navigation_payload())
            elif parsed.path == "/api/intake/items":
                navigation = navigation_payload()
                self._json({
                    "ok": True,
                    "version": navigation["version"],
                    "items": navigation["intake"],
                    "stats": navigation["stats"],
                })
            elif parsed.path == "/api/intake/schema":
                schema = json.loads(PAPER_SCHEMA_PATH.read_text(encoding="utf-8"))
                self._json({"ok": True, **schema})
            elif parsed.path == "/api/vault/note":
                self._json(note_payload(query.get("path", [""])[0]))
            elif parsed.path == "/api/intake/sync":
                count = sync_crawler_metadata_stubs()
                self._json({"ok": True, "synced": count})
            elif parsed.path == "/api/cnki/status":
                self._json(self._get_cnki_status())
            else:
                self._json({"error": "not found"}, 404)
        except ValueError as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:
            self._json({"error": f"读取本地知识库失败：{exc}"}, 500)

    def do_POST(self) -> None:  # noqa: N802
        if not self._origin_allowed():
            self._json({"error": "origin not allowed"}, 403)
            return
        try:
            payload = self._read_payload()
            if self.path == "/api/cnki/start":
                self._start_cnki(payload)
            elif self.path == "/api/cnki/stop":
                self._stop_cnki()
            elif self.path == "/api/obsidian/open":
                self._open_obsidian(payload)
            elif self.path == "/api/intake/screening":
                self._screen_intake(payload)
            elif self.path == "/api/citations/render":
                self._render_citation(payload)
            elif self.path in {"/api/agent/chat", "/api/settings/api", "/api/obsidian/sync"}:
                self._json({"error": "该写入或模型接口已在只读镜像中停用"}, 410)
            else:
                self._json({"error": "not found"}, 404)
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:
            self._json({"error": f"本地操作失败：{exc}"}, 500)

    def _open_obsidian(self, payload: dict[str, Any]) -> None:
        relative = str(payload.get("path") or "").strip()
        params = {"vault": obsidian_vault_identifier()}
        local_path = str(VAULT_ROOT.resolve())
        if relative:
            path = safe_knowledge_path(relative)
            params["file"] = path.resolve().relative_to(VAULT_ROOT.resolve()).as_posix()
            local_path = str(path.resolve())
        uri = "obsidian://open?" + urllib.parse.urlencode(params)
        subprocess.Popen(["open" if platform.system() == "Darwin" else "xdg-open", uri])
        self._json({"ok": True, "message": "已交给Obsidian打开", "uri": uri, "localPath": local_path})

    def _screen_intake(self, payload: dict[str, Any]) -> None:
        relative = clean_short_text(payload.get("path"), maximum=500)
        decision = clean_short_text(payload.get("decision"), maximum=30) or "pending"
        reason = clean_short_text(payload.get("reason"), maximum=500)
        domain = clean_short_text(payload.get("domain"), maximum=100)
        self._json(update_intake_screening(relative, decision, reason, domain))

    def _render_citation(self, payload: dict[str, Any]) -> None:
        relative = clean_short_text(payload.get("path"), maximum=500)
        mode = clean_short_text(payload.get("mode"), maximum=30) or "paraphrase"
        pinpoint = clean_short_text(payload.get("pinpointPage"), maximum=30)
        result = render_legal_citation(relative, mode, pinpoint)
        self._json(result, 200 if result.get("ok") else 422)

    def _get_cnki_status(self) -> dict[str, Any]:
        pid_file = RUNTIME_ROOT / "crawler.pid"
        status_file = RUNTIME_ROOT / "crawler_status.json"
        running = False
        pid: int | None = None
        details: dict[str, Any] = {}
        if status_file.exists():
            try:
                details = json.loads(status_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        if pid_file.exists():
            try:
                pid_val = int(pid_file.read_text(encoding="utf-8").strip())
                os.kill(pid_val, 0)
                running = True
                pid = pid_val
            except (OSError, ValueError):
                running = False
                pid_file.unlink(missing_ok=True)
                if details.get("running"):
                    details["running"] = False
        return {
            "ok": True,
            "running": running,
            "pid": pid,
            "details": details,
        }

    def _stop_cnki(self) -> None:
        RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
        stop_flag = RUNTIME_ROOT / "stop_crawler.flag"
        stop_flag.write_text("stop", encoding="utf-8")
        pid_file = RUNTIME_ROOT / "crawler.pid"
        signaled = False
        if pid_file.exists():
            try:
                pid_val = int(pid_file.read_text(encoding="utf-8").strip())
                os.kill(pid_val, signal.SIGINT)
                signaled = True
            except (OSError, ValueError):
                pass
        # 归档兜底保障：立即运行服务端同步，将所有已抓取元数据全部落盘入 Obsidian
        archived = sync_crawler_metadata_stubs()
        status_file = RUNTIME_ROOT / "crawler_status.json"
        try:
            status_file.write_text(json.dumps({
                "running": False,
                "stopped_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "message": "用户手动终止采集并归档入库",
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            pid_file.unlink(missing_ok=True)
        except OSError:
            pass
        self._json({
            "ok": True,
            "message": f"已成功终止知网采集！本次已确保归档 {archived} 篇样板至 Obsidian 论文库。",
            "archivedCount": archived,
            "signaled": signaled,
        })

    def _start_cnki(self, payload: dict[str, Any]) -> None:
        downloader = CRAWLER_ROOT / "pdf_downloader.py"
        if not downloader.exists():
            self._json({"error": f"未找到爬虫：{downloader}"}, 404)
            return
        mode = clean_short_text(payload.get("mode"), maximum=30) or "journal"
        author = clean_short_text(payload.get("author"), maximum=100)
        journals = clean_journals(payload.get("journals"))
        if mode != "author" and not journals:
            raise ValueError("至少启用一种期刊")
        RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
        stop_flag = RUNTIME_ROOT / "stop_crawler.flag"
        if stop_flag.exists():
            stop_flag.unlink(missing_ok=True)
        status_file = RUNTIME_ROOT / "crawler_status.json"
        try:
            status_file.write_text(json.dumps({
                "running": True,
                "mode": mode,
                "author": author,
                "started_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass
        selection_path = RUNTIME_ROOT / "cnki_selection.json"
        selection_path.write_text(json.dumps({
            "mode": mode,
            "author": author,
            "journals": journals,
            "strictJournal": bool(payload.get("strictJournal", True)),
            "profile": {
                "researchQuestion": clean_short_text(payload.get("researchQuestion"), maximum=500),
                "keywords": clean_journals(payload.get("keywords")),
                "yearRange": clean_short_text(payload.get("yearRange"), maximum=40),
                "destination": "采集后创建Obsidian待审核样板",
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        command = ["python3", str(BRIDGE_ROOT / "run_cnki.py"), str(selection_path)]
        if platform.system() == "Darwin":
            launch_file = RUNTIME_ROOT / "launch_cnki.command"
            launch_file.write_text(
                "#!/bin/zsh\n"
                f"cd {shlex.quote(str(PROJECT_ROOT))}\n"
                f"{' '.join(shlex.quote(part) for part in command)}\n"
                "exit_code=$?\n"
                "echo\n"
                "echo \"LexTrace：知网采集进程已结束，退出码 $exit_code。\"\n"
                "echo \"下一步：回到LexTrace待处理队列进行初筛或交给Agent。\"\n"
                "read \"?按回车关闭窗口…\"\n",
                encoding="utf-8",
            )
            launch_file.chmod(0o700)
            subprocess.Popen(["open", "-a", "Terminal", str(launch_file)])
        else:
            subprocess.Popen(command, cwd=str(PROJECT_ROOT))
        msg = f"已启动作者检索模式（作者：{author}）" if mode == "author" else f"已启动知网爬虫（{len(journals)} 种期刊）；采集后会自动同步至 Obsidian 待审核样板。"
        self._json({
            "ok": True,
            "message": msg,
        })


def main() -> None:
    sync_crawler_metadata_stubs()
    server = ThreadingHTTPServer((HOST, PORT), BridgeHandler)
    print(f"LexTrace 本机桥接：http://{HOST}:{PORT}")
    print(f"Obsidian 数据源：{KNOWLEDGE_ROOT}")
    print("模式：导航只读；仅允许新采集样板和筛选状态写入。按 Ctrl+C 停止。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLexTrace只读桥接已停止。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
