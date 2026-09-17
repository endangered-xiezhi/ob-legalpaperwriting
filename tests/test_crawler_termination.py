#!/usr/bin/env python3
"""Unit tests for CNKI crawler author mode decoupling and graceful CLI termination/archiving."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CRAWLER_ROOT = PROJECT_ROOT / "cnki_crawler"
sys.path.insert(0, str(CRAWLER_ROOT))

import config
from pdf_downloader import CNKIPDFDownloader


class CrawlerAuthorAndTerminationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # 备份配置
        self.orig_data_root = config.DATA_ROOT
        self.orig_download_dir = config.DOWNLOAD_DIR
        self.orig_metadata_dir = config.METADATA_DIR
        self.orig_paper_stub_dir = config.PAPER_STUB_DIR
        self.orig_run_mode = getattr(config, "RUN_MODE", "journal")
        self.orig_filter_journal = getattr(config, "FILTER_BY_JOURNAL", True)
        self.orig_target_authors = getattr(config, "TARGET_AUTHORS", [])

        # 隔离临时目录
        config.DATA_ROOT = str(self.root / "data")
        config.DOWNLOAD_DIR = str(self.root / "downloads")
        config.METADATA_DIR = str(self.root / "metadata")
        config.PAPER_STUB_DIR = str(self.root / "vault" / "知识产权" / "论文库")

        Path(config.DATA_ROOT).mkdir(parents=True, exist_ok=True)
        Path(config.DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(config.METADATA_DIR).mkdir(parents=True, exist_ok=True)
        Path(config.PAPER_STUB_DIR).mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        config.DATA_ROOT = self.orig_data_root
        config.DOWNLOAD_DIR = self.orig_download_dir
        config.METADATA_DIR = self.orig_metadata_dir
        config.PAPER_STUB_DIR = self.orig_paper_stub_dir
        config.RUN_MODE = self.orig_run_mode
        config.FILTER_BY_JOURNAL = self.orig_filter_journal
        config.TARGET_AUTHORS = self.orig_target_authors
        # 清理测试可能镜像到主库的临时测试文献
        mirror_candidates = [
            PROJECT_ROOT / "vault" / "知识产权" / "论文库" / "测试论文已完成下载.md",
            Path.home() / "Downloads" / "Obsidian Vault" / "知识产权" / "论文库" / "测试论文已完成下载.md",
            Path("/Users/kansang/Documents/Codex/2026-08-08/h/vault/知识产权/论文库/测试论文已完成下载.md"),
        ]
        for m in mirror_candidates:
            try:
                m.unlink(missing_ok=True)
            except OSError:
                pass
        self.temp_dir.cleanup()

    def test_author_mode_allows_any_custom_author(self) -> None:
        """测试作者模式下可任意指定学者（不仅限于知产名家），并且正确匹配。"""
        downloader = CNKIPDFDownloader()
        config.RUN_MODE = "author"
        config.FILTER_BY_JOURNAL = False

        # 测试任意法学学者，如民法学者'王利明'
        config.TARGET_AUTHORS = ["王利明"]
        paper1 = {"title": "民法典体系研究", "authors": ["王利明", "测试合著者"], "journal": "中国法学"}
        paper2 = {"title": "知识产权总论", "authors": ["崔国斌"], "journal": "中外法学"}
        self.assertTrue(downloader.paper_allowed(paper1))
        self.assertFalse(downloader.paper_allowed(paper2))

        # 测试支持多个作者（逗号/空格分隔或列表）
        config.TARGET_AUTHORS = ["王利明", "苏力", "蒋舸"]
        paper3 = {"title": "法治及其本土资源", "authors": ["苏力"], "journal": "中国法学"}
        paper4 = {"title": "竞争法分析", "authors": ["蒋舸 1"], "journal": "清华法学"}
        paper5 = {"title": "刑法学总论", "authors": ["张明楷"], "journal": "法学研究"}
        self.assertTrue(downloader.paper_allowed(paper3))
        self.assertTrue(downloader.paper_allowed(paper4))
        self.assertFalse(downloader.paper_allowed(paper5))

    def test_author_mode_empty_author_allows_all(self) -> None:
        """测试留空作者时，全量放行所有检索出的论文。"""
        downloader = CNKIPDFDownloader()
        config.RUN_MODE = "author"
        config.FILTER_BY_JOURNAL = False
        config.TARGET_AUTHORS = []

        paper1 = {"title": "任意论文A", "authors": ["任意学者甲"], "journal": "计算机学报"}
        paper2 = {"title": "任意论文B", "authors": ["某某某"], "journal": "中国法学"}
        self.assertTrue(downloader.paper_allowed(paper1))
        self.assertTrue(downloader.paper_allowed(paper2))

    def test_finalize_and_archive_creates_missing_stubs_and_moves_pdfs(self) -> None:
        """测试终止收尾时，自动补全Obsidian样板卡片并归档未整理PDF。"""
        downloader = CNKIPDFDownloader()

        # 1. 模拟临时 downloads 目录下已下载的 PDF
        dummy_pdf = Path(config.DOWNLOAD_DIR) / "测试论文已完成下载.pdf"
        dummy_pdf.write_bytes(b"%PDF-1.4 dummy content")

        # 2. 模拟下载中临时未完成的 .crdownload 文件（不应被移动）
        dummy_crdownload = Path(config.DOWNLOAD_DIR) / "未完成下载.pdf.crdownload"
        dummy_crdownload.write_bytes(b"downloading")

        # 3. 模拟 metadata 目录中抓取到的元数据
        meta_file = Path(config.METADATA_DIR) / "测试论文已完成下载.json"
        meta_data = {
            "title": "测试论文已完成下载",
            "authors": ["王迁", "测试作者"],
            "journal": "中国版权",
            "year": "2026",
            "record_id": "LTX-test123456",
            "abstract": "这是测试文章摘要。",
        }
        meta_file.write_text(json.dumps(meta_data, ensure_ascii=False), encoding="utf-8")

        # 执行收尾归档
        downloader.finalize_and_archive()

        # 验证 1：PDF 已归档到 data/unsorted
        archived_pdf = Path(config.DATA_ROOT) / "unsorted" / "测试论文已完成下载.pdf"
        self.assertTrue(archived_pdf.exists())
        self.assertTrue(dummy_crdownload.exists())  # crdownload 保持原状

        # 验证 2：Obsidian 样板 Markdown 文件已生成
        stub_file = Path(config.PAPER_STUB_DIR) / "测试论文已完成下载.md"
        self.assertTrue(stub_file.exists())
        stub_text = stub_file.read_text(encoding="utf-8")
        self.assertIn("王迁", stub_text)
        self.assertIn("中国版权", stub_text)
        self.assertIn("record_status: \"intake\"", stub_text)

    def test_is_stop_requested_detects_flag_and_instance_state(self) -> None:
        """测试 is_stop_requested 能够敏感检测内部变量与外部控制标志。"""
        downloader = CNKIPDFDownloader()
        self.assertFalse(downloader.is_stop_requested())

        # 设置内部变量
        downloader._stop_requested = True
        self.assertTrue(downloader.is_stop_requested())

    def test_extract_detail_metadata_defines_clean(self) -> None:
        """测试详情页解析脚本中必须预先定义 clean 辅助函数，避免抛出 clean is not defined 异常。"""
        downloader_file = CRAWLER_ROOT / "pdf_downloader.py"
        content = downloader_file.read_text(encoding="utf-8")
        self.assertIn("const clean = (s) =>", content)

    def test_pdf_download_selectors_validity(self) -> None:
        """测试下载按钮选择器不包含已废弃的 jQuery 伪类（如 :contains）。"""
        for sel in config.PDF_DOWNLOAD_SELECTORS:
            self.assertNotIn(":contains(", sel)


if __name__ == "__main__":
    unittest.main()
