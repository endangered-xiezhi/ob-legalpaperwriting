#!/usr/bin/env python3
"""Run the upgraded CNKI intake crawler with settings selected in LexTrace."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


DEFAULT_CRAWLER_ROOT = Path(__file__).resolve().parent.parent / "cnki_crawler"


def resolve_vault_root() -> Path:
    env_vault = os.environ.get("LEXTRACE_OBSIDIAN_VAULT") or os.environ.get("CNKI_OBSIDIAN_VAULT")
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
    project_vault = (Path(__file__).resolve().parent.parent / "vault").resolve()
    if (project_vault / "知识产权").exists():
        return project_vault
    return project_vault


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("用法：run_cnki.py <selection.json>")
    selection_path = Path(sys.argv[1]).resolve()
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    mode = str(selection.get("mode") or "journal").strip()
    author = str(selection.get("author") or "").strip()
    journals = [str(name).strip() for name in selection.get("journals", []) if str(name).strip()]
    if mode != "author" and not journals:
        raise SystemExit("未选择任何期刊，已停止启动爬虫。")

    candidates = [
        Path(os.environ.get("LEXTRACE_CNKI_ROOT", "")).expanduser() if os.environ.get("LEXTRACE_CNKI_ROOT") else None,
        DEFAULT_CRAWLER_ROOT,
        Path("/Users/kansang/Documents/Codex/2026-08-08/h/cnki_crawler"),
        Path("/Users/kansang/Downloads/claude 使用专用/cnki_crawler"),
        Path("/Users/kansang/Downloads/claude 使用专用/ob-legalpaperwriting/cnki_crawler"),
    ]
    script_path = None
    crawler_root = None
    for cand in candidates:
        if cand and (cand / "pdf_downloader.py").exists():
            crawler_root = cand.resolve()
            script_path = crawler_root / "pdf_downloader.py"
            break

    if not script_path or not script_path.exists():
        raise SystemExit(f"未找到爬虫脚本：{DEFAULT_CRAWLER_ROOT / 'pdf_downloader.py'}")

    sys.path.insert(0, str(crawler_root))
    import config as crawler_config  # type: ignore

    # 关键修复：强制开启 Obsidian 笔记自动同步
    crawler_config.AUTO_CREATE_OBSIDIAN_STUB = True

    if mode == "author":
        crawler_config.RUN_MODE = "author"
        crawler_config.FILTER_BY_JOURNAL = False
        crawler_config.TARGET_AUTHORS = [author] if author else []
    else:
        crawler_config.RUN_MODE = "journal"
        crawler_config.FILTER_BY_JOURNAL = True
        crawler_config.TARGET_JOURNALS = journals
        crawler_config.STRICT_JOURNAL_MATCH = bool(selection.get("strictJournal", True))

    crawler_config.CAPTURE_PROFILE = selection.get("profile", {})
    vault_root = resolve_vault_root()
    crawler_config.OBSIDIAN_VAULT_ROOT = str(vault_root)
    crawler_config.PAPER_STUB_DIR = str(vault_root / "知识产权" / "论文库")

    print("=" * 62)
    print(f"LexTrace 采集模式：{'作者检索模式 (' + author + ')' if mode == 'author' else '期刊范围过滤模式'}")
    if mode != "author":
        print("已载入期刊范围：")
        for name in journals:
            print(f"  - {name}")
        print(f"筛选模式：{'严格匹配' if selection.get('strictJournal', True) else '兼容原爬虫宽松规则'}")
    print(f"Obsidian 仓库同步目标：{crawler_config.PAPER_STUB_DIR}")
    print(f"样板卡片自动生成开关：{crawler_config.AUTO_CREATE_OBSIDIAN_STUB}")
    print("=" * 62)

    source = script_path.read_text(encoding="utf-8")
    namespace = {
        "__name__": "__main__",
        "__file__": str(script_path),
        "__package__": None,
    }
    exec(compile(source, str(script_path), "exec"), namespace)


if __name__ == "__main__":
    main()
