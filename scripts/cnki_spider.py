#!/usr/bin/env python3
"""知网学术论文采集器命令行统一启动入口 (CNKI Spider CLI Wrapper)

支持在项目根目录下直接运行：
  python3 scripts/cnki_spider.py --mode author
  python3 scripts/cnki_spider.py --mode author --author "崔国斌,蒋舸"
  python3 scripts/cnki_spider.py --mode journal
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CRAWLER_ROOT = PROJECT_ROOT / "cnki_crawler"

if str(CRAWLER_ROOT) not in sys.path:
    sys.path.insert(0, str(CRAWLER_ROOT))

import run_spider

if __name__ == "__main__":
    run_spider.main()
