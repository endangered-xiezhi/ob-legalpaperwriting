#!/usr/bin/env python3
"""Run the upgraded CNKI intake crawler with settings selected in LexTrace."""

from __future__ import annotations

import atexit
from datetime import datetime
import json
import os
import signal
import sys
from pathlib import Path

RUNTIME_ROOT = Path(__file__).resolve().parent / "runtime"


def write_crawler_pid(pid: int, info: dict) -> None:
    try:
        RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
        (RUNTIME_ROOT / "crawler.pid").write_text(str(pid), encoding="utf-8")
        status = {
            "running": True,
            "pid": pid,
            **info,
            "started_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        (RUNTIME_ROOT / "crawler_status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def cleanup_crawler_state() -> None:
    try:
        pid_file = RUNTIME_ROOT / "crawler.pid"
        if pid_file.exists():
            pid_file.unlink(missing_ok=True)
        status_file = RUNTIME_ROOT / "crawler_status.json"
        if status_file.exists():
            try:
                status = json.loads(status_file.read_text(encoding="utf-8"))
                status["running"] = False
                status["stopped_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
                status_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
    except OSError:
        pass


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

    # 注册 PID 与状态监听，支持外部安全终止
    write_crawler_pid(os.getpid(), {"mode": mode, "author": author})
    atexit.register(cleanup_crawler_state)

    def sig_handler(signum, frame):
        print(f"\n[LexTrace] 捕获终止信号 ({signum})，正在安全停止知网采集并完成 Obsidian 归档...")
        cleanup_crawler_state()
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)
    except Exception:
        pass

    source = script_path.read_text(encoding="utf-8")
    namespace = {
        "__name__": "__main__",
        "__file__": str(script_path),
        "__package__": None,
    }
    try:
        exec(compile(source, str(script_path), "exec"), namespace)
    except KeyboardInterrupt:
        print("\n[LexTrace] 用户手动中止采集任务，已触发收尾归档。")
    finally:
        cleanup_crawler_state()


if __name__ == "__main__":
    main()
