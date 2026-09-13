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
CRAWLER_ROOT = Path(
    os.environ.get(
        "LEXTRACE_CNKI_ROOT",
        "" + str(PROJECT_ROOT / "cnki_crawler") + "",
    )
).expanduser()
VAULT_ROOT = Path(
    os.environ.get(
        "LEXTRACE_OBSIDIAN_VAULT",
        str(PROJECT_ROOT / "vault"),
    )
).expanduser()
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
    ("论文总览", "知识产权/00_知识产权论文总览.md", "全库结构与统计口径"),
    ("近五年趋势", "知识产权/研究趋势/近五年研究趋势总览.md", "库内研究问题的年度演变"),
    ("年度索引", "知识产权/研究趋势/年度论文索引.md", "按发表年份进入论文"),
    ("学者索引", "知识产权/研究趋势/学者观点索引.md", "按作者查找观点与对话"),
    ("整理 SOP", "知识产权/研究趋势/法学论文整理SOP_Agent通用执行手册.md", "新材料整理、核验与入库规范"),
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
        for vault_id, entry in config.get("vaults", {}).items():
            registered = Path(str(entry.get("path") or "")).expanduser().resolve()
            if registered == VAULT_ROOT.resolve():
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
    authors = list_value(metadata.get("author"))
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
    return {
        "path": relative,
        "title": title,
        "folder": resolved_path.parent.relative_to(resolved_vault).as_posix(),
        "type": str(metadata.get("type") or ("论文" if is_paper else "笔记")),
        "authors": authors,
        "year": str(metadata.get("year") or ""),
        "journal": str(metadata.get("journal") or ""),
        "domain": domain,
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


def scan_vault() -> list[dict[str, Any]]:
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
    searchable = [record for record in records if not is_navigation_excluded(record["path"])]
    version = vault_version()
    return {
        "ok": True,
        "vaultName": VAULT_ROOT.name,
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
        },
        "quickLinks": [
            {"title": title, "path": path, "caption": caption}
            for title, path, caption in QUICK_LINKS if path in by_path
        ],
        "domains": domains,
        "controversies": sorted(controversies, key=lambda record: record["title"]),
        "researchPaths": sorted(research_paths, key=lambda record: record["title"]),
        "recent": sorted(formal, key=lambda record: record["modified"], reverse=True)[:15],
        "pending": sorted(pending + inbox, key=lambda record: record["modified"], reverse=True)[:60],
        "intake": sorted(intake, key=lambda record: record["modified"], reverse=True)[:200],
        "unclassified": sorted(unclassified, key=lambda record: record["modified"], reverse=True)[:60],
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


def update_intake_screening(relative: str, decision: str, reason: str = "") -> dict[str, Any]:
    if decision not in {"included", "excluded", "pending"}:
        raise ValueError("筛选结论必须是 included、excluded 或 pending")
    path = safe_knowledge_path(relative)
    if path.suffix.lower() != ".md":
        raise ValueError("只支持更新Markdown样板")
    text = path.read_text(encoding="utf-8", errors="replace")
    if "<!-- LEXTRACE:GENERATED-STUB -->" not in text:
        raise ValueError("只能更新由LexTrace创建的待审核样板")
    record_status = "excluded" if decision == "excluded" else "intake"
    updates = {
        "screening_status": decision,
        "record_status": record_status,
        "screening_reason": clean_short_text(reason, maximum=500),
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
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
    return {"ok": True, "message": "筛选结论已写入样板", "recordStatus": record_status}


def render_legal_citation(relative: str, mode: str, pinpoint: str = "") -> dict[str, Any]:
    if mode not in {"direct", "paraphrase", "general"}:
        raise ValueError("引注模式不正确")
    pinpoint = clean_short_text(pinpoint, maximum=30)
    if pinpoint and not re.fullmatch(r"\d+(?:\s*[-–—、,，]\s*\d+)*", pinpoint):
        raise ValueError("页码只能填写数字、连接号或逗号")
    path = safe_knowledge_path(relative)
    metadata = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    authors = list_value(metadata.get("author"))
    required = {
        "作者": "、".join(authors),
        "题名": str(metadata.get("title") or ""),
        "刊物": str(metadata.get("journal") or ""),
        "年份": str(metadata.get("year") or ""),
        "期号": str(metadata.get("issue") or ""),
    }
    missing = [label for label, value in required.items() if not value]
    if mode in {"direct", "paraphrase"} and not pinpoint:
        missing.append("具体页码")
    if missing:
        return {"ok": False, "error": "引注字段待补：" + "、".join(missing), "missing": missing}
    prefix = "参见" if mode == "paraphrase" else ""
    citation = (
        f"{prefix}{required['作者']}：《{required['题名']}》，载《{required['刊物']}》"
        f"{required['年份']}年第{required['期号']}期"
    )
    if pinpoint:
        citation += f"，第{pinpoint}页"
    citation += "。"
    cite_id = str(metadata.get("record_id") or hashlib.sha256(relative.encode("utf-8")).hexdigest()[:12])
    return {
        "ok": True,
        "citation": citation,
        "wordFootnote": citation,
        "obsidianMarker": f"[^{cite_id}]",
        "obsidianDefinition": f"[^{cite_id}]: {citation}",
        "verification": "metadata_ready" if not pinpoint else "pinpoint_unverified",
    }


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "LexTraceBridge/0.4"

    def log_message(self, message: str, *args: Any) -> None:
        print(f"[LexTrace] {self.address_string()} - {message % args}")

    def _origin_allowed(self) -> bool:
        origin = self.headers.get("Origin")
        return origin is None or origin in ALLOWED_ORIGINS

    def _headers(self, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def _json(self, payload: dict[str, Any], status: int = 200) -> None:
        self._headers(status)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _read_payload(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0 or content_length > 1_000_000:
            raise ValueError("请求内容为空或过大")
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
        decision = clean_short_text(payload.get("decision"), maximum=30)
        reason = clean_short_text(payload.get("reason"), maximum=500)
        self._json(update_intake_screening(relative, decision, reason))

    def _render_citation(self, payload: dict[str, Any]) -> None:
        relative = clean_short_text(payload.get("path"), maximum=500)
        mode = clean_short_text(payload.get("mode"), maximum=30) or "paraphrase"
        pinpoint = clean_short_text(payload.get("pinpointPage"), maximum=30)
        result = render_legal_citation(relative, mode, pinpoint)
        self._json(result, 200 if result.get("ok") else 422)

    def _start_cnki(self, payload: dict[str, Any]) -> None:
        downloader = CRAWLER_ROOT / "pdf_downloader.py"
        if not downloader.exists():
            self._json({"error": f"未找到爬虫：{downloader}"}, 404)
            return
        journals = clean_journals(payload.get("journals"))
        if not journals:
            raise ValueError("至少启用一种期刊")
        RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
        selection_path = RUNTIME_ROOT / "cnki_selection.json"
        selection_path.write_text(json.dumps({
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
                "status=$?\n"
                "echo\n"
                "echo \"LexTrace：知网采集进程已结束，退出码 $status。\"\n"
                "echo \"下一步：回到LexTrace待处理队列进行初筛或交给Agent。\"\n"
                "read \"?按回车关闭窗口…\"\n",
                encoding="utf-8",
            )
            launch_file.chmod(0o700)
            subprocess.Popen(["open", "-a", "Terminal", str(launch_file)])
        else:
            subprocess.Popen(command, cwd=str(PROJECT_ROOT))
        self._json({
            "ok": True,
            "message": f"已启动升级后的爬虫并传入 {len(journals)} 种期刊；采集后会创建Obsidian待审核样板。",
        })


def main() -> None:
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
