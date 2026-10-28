#!/usr/bin/env python3
"""知网学术论文独立爬虫启动入口 (CNKI Spider Launcher)

支持两种方式使用：
1. 终端交互菜单（默认）：直接双击启动或终端运行 python3 run_spider.py，按提示选择模式。
2. 命令行参数模式：
   - 作者模式（不限期刊全量下载）：python3 run_spider.py --mode author
   - 期刊过滤模式：python3 run_spider.py --mode journal
   - 更多选项：python3 run_spider.py --help
"""

from __future__ import annotations

import argparse
from datetime import datetime
import os
import re
import sys
from pathlib import Path

# 保证当前模块目录置于搜索路径第一位
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import config
from pdf_downloader import CNKIPDFDownloader


def print_banner() -> None:
    print("""
======================================================================
           📚 知网学术论文智能采集与整理工具 (CNKI Spider)
======================================================================
  特点：
  • 独立运行，无需依赖任何外部网页前端或桥接服务
  • 支持【作者模式/全量下载】与【法学核心期刊过滤模式】
  • 自动提取知网官方 EndNote 高精度引注元数据
  • PDF 自动下载并按实际发表年份规范分目录归档
  • 自动基于 PyMuPDF 提取带有 [[PDF_PAGE:n]] 标柱的逐页文本与页码索引
  • 可选同步生成 Obsidian 待审核样板卡片
======================================================================
""")


def interactive_menu() -> None:
    print_banner()
    print("请选择本次采集的运行模式：\n")
    print("  [1] 🎯 法学核心期刊模式 (CLSCI)")
    print("      适合专题检索（如'数据确权'、'AIGC'），仅保留16种法学核心期刊论文，自动跳过其他期刊。\n")
    print("  [2] ✍️  作者模式 / 全量采集模式 (🌟 推荐用于整理专家学者论文集)")
    print("      解除期刊限制！检索列表出来的文献全部自动下载、解析并归档！\n")
    print("  [3] ⚙️  高级自定义模式")
    print("      自定义设置期刊白名单、Obsidian 同步开关、TXT 提取等参数。\n")

    try:
        choice = input("👉 请输入模式编号 [1/2/3] (直接按回车默认 [1]，输入 q 退出): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n🛑 用户取消启动。")
        sys.exit(0)

    if choice.lower() in ("q", "quit", "exit"):
        print("\n🛑 已退出。")
        sys.exit(0)

    if choice == "2":
        # 作者模式
        config.RUN_MODE = "author"
        config.FILTER_BY_JOURNAL = False
        print("\n✅ 已选择：【作者模式（全量采集）】")
        print("   💡 说明：")
        print("   • 直接按【回车】：不限学者姓名，知网检索出的全部文献一律全量下载入库（推荐！）")
        print("   • 手动输入姓名：支持任意学者（如'崔国斌'、'蒋舸'、'王利明'等，多个学者用逗号分隔）")
        print("   • 常见知产学者参考提示：崔国斌、蒋舸、冯术杰、王迁、孔祥俊、易继明、李琛、张平、熊丙万等")
        try:
            author_input = input("\n👉 请输入学者姓名校验 (直接按回车表示不限作者全量采集；输入 q 退出): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n🛑 用户取消启动。")
            sys.exit(0)
        if author_input.lower() in ("q", "quit", "exit"):
            print("\n🛑 已退出。")
            sys.exit(0)
        if author_input:
            config.TARGET_AUTHORS = [a.strip() for a in re.split(r"[,，\s]+", author_input) if a.strip()]
            print(f"   已设置学者核验名单：{'、'.join(config.TARGET_AUTHORS)}")
        else:
            config.TARGET_AUTHORS = []
            print("   已设置：不限学者姓名，知网检索列表全部论文直接全量下载入库。")

    elif choice == "3":
        # 自定义高级模式
        print("\n--- 高级自定义设置 ---")
        try:
            filter_choice = input("👉 是否开启期刊过滤？[Y/n] (默认 Y): ").strip().lower()
            if filter_choice in ("n", "no", "0"):
                config.FILTER_BY_JOURNAL = False
                config.RUN_MODE = "author"
            else:
                config.FILTER_BY_JOURNAL = True
                config.RUN_MODE = "journal"
                strict_choice = input("👉 是否严格全字匹配核心期刊？[y/N] (默认 N，宽松包含'法'或'知识产权'期刊): ").strip().lower()
                config.STRICT_JOURNAL_MATCH = strict_choice in ("y", "yes", "1")

            obsidian_choice = input("👉 是否自动在 Obsidian 中创建待审核笔记样板？[Y/n] (默认 Y): ").strip().lower()
            config.AUTO_CREATE_OBSIDIAN_STUB = obsidian_choice not in ("n", "no", "0")

            txt_choice = input("👉 是否提取带页码标记的分页 TXT 与页码对照索引？[Y/n] (默认 Y): ").strip().lower()
            config.EXTRACT_PAGINATED_TXT = txt_choice not in ("n", "no", "0")
        except (KeyboardInterrupt, EOFError):
            print("\n🛑 用户取消启动。")
            sys.exit(0)

    else:
        # 默认法学核心期刊模式
        config.RUN_MODE = "journal"
        config.FILTER_BY_JOURNAL = True
        config.STRICT_JOURNAL_MATCH = False
        print("\n✅ 已选择：【法学核心期刊过滤模式】（16种CLSCI核心期刊）")

    # 询问是否开启 Obsidian 联动（若之前未在第3项设置）
    if choice in ("1", "2"):
        try:
            obs_input = input("\n👉 是否同步在本地 Obsidian 论文库中生成待审核笔记样板？[Y/n] (回车默认 Y，自动生成样板): ").strip().lower()
            config.AUTO_CREATE_OBSIDIAN_STUB = obs_input not in ("n", "no", "0")
        except (KeyboardInterrupt, EOFError):
            print("\n🛑 用户取消启动。")
            sys.exit(0)

    # 项目与批次分类归档配置
    if config.AUTO_CREATE_OBSIDIAN_STUB:
        print("\n📁 【分类归档设置 (Obsidian 11论文收集)】")
        try:
            default_proj = getattr(config, "PROJECT_NAME", "证券虚假陈述")
            proj_input = input(f"👉 请输入项目名称 (回车默认: '{default_proj}'): ").strip()
            config.PROJECT_NAME = proj_input if proj_input else default_proj

            default_batch = datetime.now().strftime("%Y%m%d_%H%M")
            batch_input = input(f"👉 请输入本次采集批次名称 (回车默认: '{default_batch}'): ").strip()
            config.BATCH_NAME = batch_input if batch_input else default_batch
            
            print(f"   已设置归档层级：11论文收集/{config.PROJECT_NAME}/{config.BATCH_NAME}/[年份]/")
        except (KeyboardInterrupt, EOFError):
            print("\n🛑 用户取消启动。")
            sys.exit(0)

    print("\n" + "=" * 70)
    print("🚀 配置就绪，正在准备启动采集器……")
    print("=" * 70 + "\n")


def parse_arguments() -> bool:
    parser = argparse.ArgumentParser(
        description="知网学术论文智能独立爬虫 (CNKI Spider)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["journal", "author"],
        help="运行模式：\n  journal: 期刊过滤模式 (CLSCI核心刊)\n  author:  作者模式 (不限期刊全量下载)",
    )
    parser.add_argument(
        "--author",
        dest="authors",
        help="指定作者姓名（用于作者模式核验，多个作者用逗号分隔，例如: '崔国斌,王迁'）",
    )
    parser.add_argument(
        "--project",
        default="证券虚假陈述",
        help="归档项目名称（默认: '证券虚假陈述'）",
    )
    parser.add_argument(
        "--batch",
        default="",
        help="采集批次名称（留空则默认按当前时间戳命名）",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="关闭期刊过滤（相当于作者模式/全量下载）",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="期刊模式下开启严格全字匹配",
    )
    parser.add_argument(
        "--obsidian",
        action="store_true",
        help="开启 Obsidian 笔记样板联动生成",
    )
    parser.add_argument(
        "--no-txt",
        action="store_true",
        help="关闭 PDF 分页 TXT 提取",
    )

    args = parser.parse_args()

    # 如果没有任何参数，则进入终端交互式菜单
    if len(sys.argv) == 1:
        return False

    if args.project:
        config.PROJECT_NAME = args.project
    if args.batch:
        config.BATCH_NAME = args.batch

    if args.no_filter or args.mode == "author":
        config.RUN_MODE = "author"
        config.FILTER_BY_JOURNAL = False
    elif args.mode == "journal":
        config.RUN_MODE = "journal"
        config.FILTER_BY_JOURNAL = True

    if args.authors:
        config.TARGET_AUTHORS = [a.strip() for a in re.split(r"[,，\s]+", args.authors) if a.strip()]

    if args.strict:
        config.STRICT_JOURNAL_MATCH = True

    if args.obsidian:
        config.AUTO_CREATE_OBSIDIAN_STUB = True

    if args.no_txt:
        config.EXTRACT_PAGINATED_TXT = False

    return True


def main() -> None:
    try:
        has_args = parse_arguments()
        if not has_args:
            interactive_menu()
    except (KeyboardInterrupt, EOFError):
        print("\n🛑 用户取消启动。")
        sys.exit(0)

    downloader = CNKIPDFDownloader()
    try:
        downloader.run()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as exc:
        print(f"\n❌ 采集器异常退出：{exc}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
