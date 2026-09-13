"""知网论文独立爬虫配置文件 (CNKI Spider Configuration)

支持两种主要运行模式：
1. "journal" (期刊过滤模式): 按指定期刊白名单（默认法学核心16刊）精准筛选，非目标期刊自动跳过。
2. "author"  (作者模式/全量模式): 专为整理特定作者论文集设计，不限期刊，检索结果全部下载。
"""

from __future__ import annotations

import os
from pathlib import Path

# 当前独立爬虫根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# 1. 运行模式设置
# ==============================================================================
# 可选值: "journal" (期刊过滤模式) | "author" (作者/全量模式)
RUN_MODE = "journal"

# 期刊过滤开关（在 author 模式下自动置为 False）
FILTER_BY_JOURNAL = True

# 是否进行严格全字期刊匹配（False 则允许包含“法”或“知识产权”的学报期刊）
STRICT_JOURNAL_MATCH = False

# 法学核心期刊 (CLSCI) 白名单
TARGET_JOURNALS = [
    "中国社会科学",
    "中国法学",
    "法学研究",
    "中外法学",
    "法学家",
    "法商研究",
    "法学",
    "法律科学",
    "法学评论",
    "政法论坛",
    "法制与社会发展",
    "现代法学",
    "比较法研究",
    "环球法律评论",
    "清华法学",
    "政治与法律",
]

# 在作者模式下，可指定目标作者姓名用于核验（留空则对检索到的全部论文一律全量下载）
TARGET_AUTHORS: list[str] = []

# ==============================================================================
# 2. 文件与目录存储配置
# ==============================================================================
# PDF 正式存储根目录（内部按发表年份归档，例如 data/2024/xxx.pdf）
DATA_ROOT = os.path.join(BASE_DIR, "data")

# 浏览器临时下载目录
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

# 运行日志保存目录
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 结构化元数据 JSON 保存目录
METADATA_DIR = os.path.join(BASE_DIR, "metadata")

# PDF 页码与印刷页码对照索引 JSON 保存目录
PAGE_INDEX_DIR = os.path.join(BASE_DIR, "page_index")

# 分页 TXT 文本保存目录（含 [[PDF_PAGE:n]] 标记，支持配置外部路径）
TXT_DIR = os.environ.get(
    "CNKI_TXT_DIR",
    os.environ.get("LEXTRACE_TXT_DIR", os.path.join(BASE_DIR, "txt")),
)

# Chrome 用户数据目录（用于保存知网、CARSI/校园网持久化登录状态）
USER_DATA_DIR = os.path.join(BASE_DIR, "cnki_chrome_data")

# 是否在下载 PDF 后自动生成带页码标记的 TXT 与页码对照索引（需 PyMuPDF）
EXTRACT_PAGINATED_TXT = True

# ==============================================================================
# 3. Obsidian 联动配置 (可选)
# ==============================================================================
# 是否自动在 Obsidian 中创建待审核笔记样板（如果不需要，设为 False 即可）
AUTO_CREATE_OBSIDIAN_STUB = os.environ.get("CNKI_CREATE_OBSIDIAN", "false").lower() in ("true", "1", "yes")

# Obsidian 仓库路径（仅当 AUTO_CREATE_OBSIDIAN_STUB 为 True 时生效）
OBSIDIAN_VAULT_ROOT = os.environ.get(
    "CNKI_OBSIDIAN_VAULT",
    os.environ.get("LEXTRACE_OBSIDIAN_VAULT", "" + os.path.abspath(os.path.join(BASE_DIR, "..", "vault")) + ""),
)
PAPER_STUB_DIR = os.path.join(OBSIDIAN_VAULT_ROOT, "知识产权", "论文库")

# ==============================================================================
# 4. Chrome 浏览器与自动化配置
# ==============================================================================
CHROME_PATH = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# CHROMEDRIVER_PATH = "" # 如需手动指定 ChromeDriver 路径可在此填写

PDF_DOWNLOAD_TIMEOUT = 120  # PDF 下载等待超时（秒）
PAGE_LOAD_WAIT = 3          # 页面加载缓冲等待时间（秒）

ARTICLE_LINK_SELECTOR = "td.name a.fz14"

PDF_DOWNLOAD_SELECTORS = [
    "#pdfDown",
    "a[name='pdfDown']",
    ".btn-dlpdf a",
    "a#pdfDown",
    "a:contains('PDF下载')",
]

# 附加采集元信息画像
CAPTURE_PROFILE: dict = {}
