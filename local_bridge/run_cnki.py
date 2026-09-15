#!/usr/bin/env python3
"""Run the upgraded CNKI intake crawler with settings selected in LexTrace."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


DEFAULT_CRAWLER_ROOT = Path(__file__).resolve().parent.parent / "cnki_crawler"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("用法：run_cnki.py <selection.json>")
    selection_path = Path(sys.argv[1]).resolve()
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    journals = [str(name).strip() for name in selection.get("journals", []) if str(name).strip()]
    if not journals:
        raise SystemExit("未选择任何期刊，已停止启动爬虫。")

    crawler_root = Path(os.environ.get("LEXTRACE_CNKI_ROOT", str(DEFAULT_CRAWLER_ROOT))).expanduser()
    script_path = crawler_root / "pdf_downloader.py"
    if not script_path.exists():
        raise SystemExit(f"未找到爬虫脚本：{script_path}")

    sys.path.insert(0, str(crawler_root))
    import config as crawler_config  # type: ignore

    crawler_config.FILTER_BY_JOURNAL = True
    crawler_config.TARGET_JOURNALS = journals
    crawler_config.STRICT_JOURNAL_MATCH = bool(selection.get("strictJournal", True))
    crawler_config.CAPTURE_PROFILE = selection.get("profile", {})
    vault_root = os.environ.get(
        "LEXTRACE_OBSIDIAN_VAULT",
        str(Path(__file__).resolve().parent.parent / "vault"),
    )
    crawler_config.OBSIDIAN_VAULT_ROOT = vault_root
    crawler_config.PAPER_STUB_DIR = str(
        Path(vault_root) / "知识产权" / "论文库"
    )

    print("=" * 62)
    print("LexTrace 已载入期刊范围：")
    for name in journals:
        print(f"  - {name}")
    print(f"筛选模式：{'严格匹配' if selection.get('strictJournal', True) else '兼容原爬虫宽松规则'}")
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
