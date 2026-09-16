#!/usr/bin/env python3
"""知网学术论文采集器 (CNKI PDF Downloader)

核心引擎：
1. 自动化 Chrome 浏览器交互，支持保持校园网/CARSI登录态；
2. 检索结果行与详情页深度信息提取；
3. 异步调用知网官方导出接口获取高精度 EndNote 引注数据；
4. 支持【期刊过滤模式】与【作者全量模式】双轨采集；
5. 自动下载 PDF 并依据真实出版年份归档；
6. 自动解析 PDF 逐页文本并附带 [[PDF_PAGE:n]] 标柱；
7. 可选同步创建 Obsidian 结构化笔记样板。
"""

from __future__ import annotations

import glob
import json
import logging
import os
import random
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
from intake_pipeline import (
    extract_paginated_text,
    merge_metadata,
    parse_endnote,
    safe_filename,
    upsert_obsidian_stub,
    write_manifest,
)

# 自动创建必要的工作目录
for directory in (
    config.DATA_ROOT,
    config.DOWNLOAD_DIR,
    config.LOG_DIR,
    config.METADATA_DIR,
    config.PAGE_INDEX_DIR,
    config.TXT_DIR,
    config.USER_DATA_DIR,
):
    Path(directory).mkdir(parents=True, exist_ok=True)

log_filename = Path(config.LOG_DIR) / f"cnki_spider_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_filename, encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class CNKIPDFDownloader:
    def __init__(self) -> None:
        self.driver: webdriver.Chrome | None = None
        self.main_window: str | None = None
        self.stats = {
            "success": 0,
            "stubs": 0,
            "metadata_only": 0,
            "skipped": 0,
            "failed": 0,
            "start_time": time.time(),
        }
        self.downloaded_titles, self.downloaded_record_ids = self.load_download_history()

    def load_download_history(self) -> tuple[set[str], set[str]]:
        """读取本地已有 PDF 与元数据记录，用于增量去重。"""
        titles: set[str] = set()
        record_ids: set[str] = set()
        for path in Path(config.DATA_ROOT).rglob("*.pdf"):
            titles.add(re.sub(r"__[A-Za-z0-9_-]{6,}$", "", path.stem))
        for path in Path(config.METADATA_DIR).glob("*.json"):
            try:
                item = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            pdf_path = Path(str(item.get("pdf_path") or "")).expanduser()
            if pdf_path.exists():
                if item.get("record_id"):
                    record_ids.add(str(item["record_id"]))
                if item.get("title"):
                    titles.add(safe_filename(str(item["title"])))
        logger.info("已读取历史记录：%s 个题名，%s 个稳定记录ID（已下载文献将自动跳过）。", len(titles), len(record_ids))
        return titles, record_ids

    def start_browser(self) -> None:
        """启动配备反爬绕过与登录态保持的 Chrome 浏览器。"""
        logger.info("正在启动 Chrome 自动化浏览器……")
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f"--user-data-dir={config.USER_DATA_DIR}")

        if os.path.exists(config.CHROME_PATH):
            options.binary_location = config.CHROME_PATH

        options.add_argument(
            "user-agent="
            + random.choice([
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            ])
        )
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(Path(config.DOWNLOAD_DIR).resolve()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,
            },
        )

        # 优先使用 webdriver_manager，如失败则尝试 Selenium 内置 Manager 或本地缓存
        driver = None
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as exc:
            logger.warning("webdriver_manager 自动适配失败：%s，尝试直接驱动……", exc)
            try:
                # Selenium 4.6+ 具备原生驱动管理能力
                driver = webdriver.Chrome(options=options)
            except Exception as inner_exc:
                configured = getattr(config, "CHROMEDRIVER_PATH", "")
                if configured and Path(configured).exists():
                    driver = webdriver.Chrome(service=Service(configured), options=options)
                else:
                    candidates = sorted(
                        Path("~/.wdm/drivers/chromedriver").expanduser().glob("**/chromedriver"),
                        key=lambda item: item.stat().st_mtime,
                        reverse=True,
                    )
                    if not candidates:
                        raise RuntimeError("无法启动 Chrome。请确认已安装 Google Chrome 浏览器。") from inner_exc
                    driver = webdriver.Chrome(service=Service(str(candidates[0])), options=options)

        self.driver = driver
        self.driver.set_script_timeout(30)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
        )
        self.driver.get("https://kns.cnki.net/kns8s/AdvSearch")
        self.main_window = self.driver.current_window_handle
        try:
            self.driver.maximize_window()
        except WebDriverException:
            pass

    def wait_for_user_login(self) -> None:
        input("\n📌 【第一步】：请在弹出的 Chrome 浏览器中登录知网（如校园网认证、CARSI 或个人账号），登录成功后在此窗口按【回车】继续……")

    def wait_for_search_setup(self) -> None:
        mode = getattr(config, "RUN_MODE", "journal")
        if mode == "author":
            target_authors = getattr(config, "TARGET_AUTHORS", [])
            author_tip = f"（目标作者：{'、'.join(target_authors)}）" if target_authors else "（不限期刊，全量下载）"
            print(f"\n📌 【第二步 - 作者模式 {author_tip}】：")
            print("   请在知网页面设置作者姓名并点击检索；进入结果列表后，建议将每页显示数量设为【50条】。")
            print("   💡 本模式下已关闭期刊限制，列表中的全部文献均会按顺序自动下载并归档！")
        else:
            print("\n📌 【第二步 - 期刊过滤模式】：")
            print("   请在知网页面输入主题/关键词检索；进入结果列表后，建议将每页显示数量设为【50条】。")
            print("   💡 本模式将仅下载符合法学核心期刊白名单的文献，其它期刊将自动跳过。")

        input("   确认已进入结果列表页后，在此窗口按【回车】正式开始自动采集……")
        self._ensure_window_alive()
        assert self.driver is not None
        self.main_window = self.driver.current_window_handle

    def _ensure_window_alive(self) -> None:
        assert self.driver is not None
        try:
            _ = self.driver.current_window_handle
            _ = self.driver.title
        except WebDriverException:
            if self.driver.window_handles:
                self.driver.switch_to.window(self.driver.window_handles[-1])

    def _captcha_visible(self) -> bool:
        assert self.driver is not None
        try:
            return bool(
                self.driver.execute_script(
                    """
                    const el = document.querySelector('#tcaptcha_transform_dy');
                    return !!(el && el.getBoundingClientRect().top >= 0);
                    """
                )
            )
        except WebDriverException:
            source = self.driver.page_source or ""
            return "拖动下方拼图" in source or "verifybox" in source

    def get_article_links(self):
        assert self.driver is not None
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config.ARTICLE_LINK_SELECTOR))
            )
            return self.driver.find_elements(By.CSS_SELECTOR, config.ARTICLE_LINK_SELECTOR)
        except TimeoutException:
            # 备用选择器容错（适应知网不同版本布局）
            for fallback in ["td.name a", ".result-table-list td.name a", "a.fz14"]:
                links = self.driver.find_elements(By.CSS_SELECTOR, fallback)
                if links:
                    return links
            logger.warning("未检测到文章链接，请确认当前页面是知网文献检索结果列表页。")
            return []

    def extract_row_metadata(self, link_element) -> dict:
        assert self.driver is not None
        try:
            row = link_element.find_element(By.XPATH, "./ancestor::tr")
            return self.driver.execute_script(
                """
                const row=arguments[0], link=arguments[1];
                const texts=(selector)=>Array.from(row.querySelectorAll(selector)).map(x=>x.innerText.trim()).filter(Boolean);
                const one=(selector)=>row.querySelector(selector)?.innerText?.trim()||'';
                return {
                  title: link.innerText.trim(), detail_url: link.href||'',
                  authors: texts('td.author a.KnowledgeNetLink, td.author a'),
                  journal: one('td.source a, td.source'), date: one('td.date'),
                  citation_count: one('td.quote'), download_count: one('td.download'),
                  export_id: row.querySelector('input.cbItem')?.value||''
                };
                """,
                row,
                link_element,
            )
        except WebDriverException:
            return {"title": link_element.text, "detail_url": link_element.get_attribute("href") or ""}

    def paper_allowed(self, row_metadata: dict) -> bool:
        """核心准入校验：支持【期刊模式过滤】与【作者模式全量下载】。"""
        mode = getattr(config, "RUN_MODE", "journal")

        # 模式 1：作者模式（全量采集，不限制期刊）
        if mode == "author" or not getattr(config, "FILTER_BY_JOURNAL", True):
            target_authors = getattr(config, "TARGET_AUTHORS", [])
            if not target_authors:
                # 用户没有指定具体姓名，则检索出来的所有条目一律全量下载
                return True

            # 若指定了作者名单，则核实作者列表或题名是否匹配
            authors = [str(a).strip() for a in row_metadata.get("authors", [])]
            for target in target_authors:
                if any(target in a for a in authors):
                    return True

            logger.info("⏭️ 跳过非指定作者文献：%s（作者：%s）", row_metadata.get("title"), "、".join(authors))
            return False

        # 模式 2：期刊过滤模式（仅限白名单期刊）
        journal = str(row_metadata.get("journal") or "").strip()
        targets = getattr(config, "TARGET_JOURNALS", [])
        if journal in targets:
            return True
        if not getattr(config, "STRICT_JOURNAL_MATCH", False) and ("法" in journal or "知识产权" in journal):
            return True

        logger.info("⏭️ 跳过非目标期刊：%s（%s）", row_metadata.get("title"), journal or "来源未知")
        return False

    def extract_detail_metadata(self) -> dict:
        assert self.driver is not None
        return self.driver.execute_script(
            r"""
            const brief=document.querySelector('.brief');
            const authorHeads=brief?.querySelectorAll('h3.author')||[];
            const authors=authorHeads[0]?Array.from(authorHeads[0].querySelectorAll('a')).map(a=>clean(a.innerText).replace(/[\d,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰]+$/,'').replace(/^[\d,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰]+/,'')).filter(a=>a&&!/^[\d,，、;.；：:¹²³⁴⁵⁶⁷⁸⁹⁰]+$/.test(a)):[];
            const affiliations=authorHeads[1]?Array.from(authorHeads[1].querySelectorAll('a')).map(a=>clean(a.innerText).replace(/^\d+\.?/,'')).filter(Boolean):[];
            const keywords=Array.from(document.querySelectorAll('p.keywords a')).map(a=>clean(a.innerText).replace(/[;；]$/,'')).filter(Boolean);
            const citationInfo={};
            document.querySelectorAll('ul.module-tab.tpl_lieteratures li').forEach(li=>{
              const text=clean(li.innerText), match=text.match(/(\d+)/);
              citationInfo[li.getAttribute('data-id')||text]= {label:text.replace(/\d+/,'').trim(),count:match?Number(match[1]):0};
            });
            const url=new URL(window.location.href);
            return {
              title: clean(brief?.querySelector('h1')?.innerText).replace(/\s*(附视频|网络首发)\s*$/,''),
              authors, affiliations,
              abstract: clean(document.querySelector('.abstract-text')?.innerText), keywords,
              fund: clean(document.querySelector('p.funds')?.innerText),
              classification: clean(document.querySelector('.clc-code')?.innerText),
              journal: clean(document.querySelector('.doc-top a')?.innerText),
              publication_info: clean(document.querySelector('.head-time')?.innerText),
              toc: clean(document.querySelector('.catalog-list,.catalog-listDiv')?.innerText),
              is_online_first: !!brief?.querySelector('.icon-shoufa'), citation_info: citationInfo,
              detail_url: window.location.href,
              cnki_id: document.querySelector('#paramfilename')?.value||url.searchParams.get('filename')||'',
              export_id: document.querySelector('#export-id')?.value||'',
              dbcode: document.querySelector('#paramdbcode')?.value||''
            };
            """
        ) or {}

    def extract_export_metadata(self) -> tuple[dict, dict]:
        assert self.driver is not None
        raw = self.driver.execute_async_script(
            """
            const done=arguments[0];
            const exportId=document.querySelector('#export-id')?.value;
            const api=document.querySelector('#export-url')?.value||'https://kns.cnki.net/dm8/API/GetExport';
            if(!exportId){done({});return;}
            const platform=new URLSearchParams(location.search).get('uniplatform')||'NZKPT';
            fetch(api,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({filename:exportId,displaymode:'GBTREFER,elearning,EndNote',uniplatform:platform})})
              .then(r=>r.json()).then(data=>{
                const result={};
                if(data.code===1){for(const item of data.data||[]){result[String(item.mode||'').toUpperCase()]=item.value?.[0]||'';}}
                done(result);
              }).catch(error=>done({error:String(error)}));
            """
        ) or {}
        endnote = raw.get("ENDNOTE", "")
        return parse_endnote(endnote), raw

    def clear_downloads_dir(self) -> None:
        for path in Path(config.DOWNLOAD_DIR).iterdir():
            if path.is_file() and path.suffix.lower() in {".pdf", ".crdownload", ".tmp"}:
                try:
                    path.unlink()
                except OSError as exc:
                    logger.warning("清理临时下载文件失败 %s：%s", path, exc)

    def wait_for_new_pdf(self, timeout: int = config.PDF_DOWNLOAD_TIMEOUT) -> Path | None:
        start = time.time()
        while time.time() - start < timeout:
            partial = glob.glob(os.path.join(config.DOWNLOAD_DIR, "*.crdownload"))
            pdfs = glob.glob(os.path.join(config.DOWNLOAD_DIR, "*.pdf"))
            if pdfs and not partial:
                return Path(max(pdfs, key=os.path.getmtime))
            time.sleep(1)
        return None

    def open_detail(self, row_metadata: dict, link_element) -> str:
        assert self.driver is not None
        initial = set(self.driver.window_handles)
        url = str(row_metadata.get("detail_url") or "")
        if url:
            self.driver.execute_script("window.open(arguments[0], '_blank');", url)
        else:
            self.driver.execute_script("arguments[0].click();", link_element)
        WebDriverWait(self.driver, 12).until(lambda driver: len(set(driver.window_handles) - initial) > 0)
        handle = list(set(self.driver.window_handles) - initial)[-1]
        self.driver.switch_to.window(handle)
        time.sleep(config.PAGE_LOAD_WAIT)
        if self._captcha_visible():
            input("⚠️ 知网详情页要求滑动验证，请手动完成后按回车继续……")
        return handle

    def click_pdf_download(self) -> bool:
        assert self.driver is not None
        for selector in config.PDF_DOWNLOAD_SELECTORS:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.driver.execute_script("arguments[0].click();", button)
                logger.info("已点击 PDF 下载按钮：%s", selector)
                return True
            except (NoSuchElementException, WebDriverException):
                continue
        return False

    def close_secondary_windows(self) -> None:
        assert self.driver is not None
        handles = self.driver.window_handles
        if self.main_window not in handles and handles:
            self.main_window = handles[0]
        for handle in list(handles):
            if handle != self.main_window:
                try:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                except WebDriverException:
                    pass
        if self.main_window in self.driver.window_handles:
            self.driver.switch_to.window(self.main_window)

    def process_article(self, link_element, row_metadata: dict) -> None:
        assert self.driver is not None
        title = str(row_metadata.get("title") or link_element.text).strip()
        logger.info("正在采集：%s", title)
        self.clear_downloads_dir()
        stub_path: Path | None = None
        metadata: dict = {}
        try:
            self.open_detail(row_metadata, link_element)
            detail = self.extract_detail_metadata()
            try:
                exported, export_raw = self.extract_export_metadata()
            except (WebDriverException, TimeoutException) as exc:
                logger.warning("EndNote 接口导出受限，使用页面字段：%s", exc)
                exported, export_raw = {}, {}

            metadata = merge_metadata(row_metadata, detail, exported)
            metadata["export_raw"] = export_raw
            metadata["capture_profile"] = getattr(config, "CAPTURE_PROFILE", {})
            metadata["captured_at"] = datetime.now().astimezone().isoformat(timespec="seconds")

            # 可选：在 Obsidian 中创建样板卡片
            if getattr(config, "AUTO_CREATE_OBSIDIAN_STUB", False):
                stub_path, created = upsert_obsidian_stub(metadata, Path(config.PAPER_STUB_DIR))
                metadata["obsidian_note_path"] = str(stub_path)
                if created:
                    self.stats["stubs"] += 1
                    logger.info("✅ 已创建 Obsidian 样板卡片：%s", stub_path.name)
                else:
                    logger.info("ℹ️ 已匹配现有 Obsidian 笔记，保留人工内容：%s", stub_path.name)

            write_manifest(metadata, Path(config.METADATA_DIR))

            if metadata["record_id"] in self.downloaded_record_ids:
                logger.info("⏭️ 该文献稳定ID已下载过，跳过下载：%s", metadata["record_id"])
                self.stats["skipped"] += 1
                return

            windows_before_download = set(self.driver.window_handles)
            if not self.click_pdf_download():
                metadata["ingest_warning"] = "未找到PDF下载按钮"
                write_manifest(metadata, Path(config.METADATA_DIR))
                self.stats["metadata_only"] += 1
                logger.warning("只保存元数据，未找到 PDF 下载按钮：%s", title)
                return

            time.sleep(2)
            download_windows = set(self.driver.window_handles) - windows_before_download
            if download_windows:
                self.driver.switch_to.window(list(download_windows)[-1])
                input("⚠️ 知网打开了下载中间页或验证页，请手动完成后按回车继续……")
            if self._captcha_visible():
                input("⚠️ PDF 下载触发滑动验证，请手动完成后按回车继续……")

            downloaded = self.wait_for_new_pdf()
            if not downloaded:
                metadata["ingest_warning"] = "PDF下载超时或失败"
                write_manifest(metadata, Path(config.METADATA_DIR))
                self.stats["metadata_only"] += 1
                logger.warning("只保存元数据，PDF 下载超时：%s", title)
                return

            year = str(metadata.get("year") or "unknown")
            year_dir = Path(config.DATA_ROOT) / safe_filename(year, "unknown")
            year_dir.mkdir(parents=True, exist_ok=True)
            stem = safe_filename(str(metadata.get("title") or title))
            suffix = str(metadata["record_id"])[-8:]
            pdf_path = year_dir / f"{stem}__{suffix}.pdf"

            if pdf_path.exists():
                logger.info("目标 PDF 已存在，移除重复下载：%s", pdf_path.name)
                downloaded.unlink(missing_ok=True)
            else:
                shutil.move(str(downloaded), pdf_path)

            # 自动提取带 [[PDF_PAGE:n]] 标柱的 TXT 和页码对照 JSON
            if getattr(config, "EXTRACT_PAGINATED_TXT", True):
                txt_path = Path(config.TXT_DIR) / f"{stem}__{suffix}.txt"
                index_path = Path(config.PAGE_INDEX_DIR) / f"{stem}__{suffix}.json"
                page_result = extract_paginated_text(
                    pdf_path,
                    txt_path,
                    index_path,
                    str(metadata.get("page_range") or ""),
                )
                metadata.update({
                    "pdf_path": str(pdf_path),
                    "txt_path": str(txt_path),
                    "page_index_path": str(index_path),
                    "page_count": page_result["page_count"],
                    "ocr_required": page_result["ocr_required"],
                })
                if page_result["ocr_required"]:
                    metadata["ingest_warning"] = "部分 PDF 页未提取到文本，建议 OCR"
            else:
                metadata["pdf_path"] = str(pdf_path)

            write_manifest(metadata, Path(config.METADATA_DIR))

            # 若开启了 Obsidian 联动，回写实际路径
            if getattr(config, "AUTO_CREATE_OBSIDIAN_STUB", False):
                stub_path, _ = upsert_obsidian_stub(metadata, Path(config.PAPER_STUB_DIR), stub_path)

            self.downloaded_titles.add(stem)
            self.downloaded_record_ids.add(metadata["record_id"])
            self.stats["success"] += 1
            logger.info("✅ 采集成功归档：%s", pdf_path.name)
        except Exception as exc:
            self.stats["failed"] += 1
            logger.exception("采集文章失败 %s：%s", title, exc)
            if metadata:
                metadata["ingest_warning"] = f"采集异常：{exc}"
                try:
                    write_manifest(metadata, Path(config.METADATA_DIR))
                except OSError:
                    pass
        finally:
            try:
                self.close_secondary_windows()
            except WebDriverException:
                pass

    def goto_next_page(self) -> bool:
        assert self.driver is not None
        selectors = ["#PageNext", "a.next"]
        for selector in selectors:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                classes = button.get_attribute("class") or ""
                if button.is_displayed() and "disabled" not in classes:
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(config.PAGE_LOAD_WAIT)
                    return True
            except (NoSuchElementException, WebDriverException):
                continue
        try:
            button = self.driver.find_element(By.XPATH, "//a[contains(normalize-space(.),'下一页')]")
            if button.is_displayed():
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(config.PAGE_LOAD_WAIT)
                return True
        except (NoSuchElementException, WebDriverException):
            pass
        logger.info("已到达最后一页或无下一页按钮，本次采集结束。")
        return False

    def run(self) -> None:
        self.start_browser()
        assert self.driver is not None
        try:
            self.wait_for_user_login()
            self.wait_for_search_setup()
            page_number = 1
            while True:
                logger.info("============ 正在处理第 %s 页 ============", page_number)
                self._ensure_window_alive()
                if self._captcha_visible():
                    input("⚠️ 结果列表页要求滑动验证，请手动完成后按回车继续……")
                links = self.get_article_links()
                if not links:
                    logger.info("当前页未检测到更多文章链接。")
                    break
                logger.info("当前页共检测到 %s 篇文献，开始处理。", len(links))
                for index in range(len(links)):
                    self._ensure_window_alive()
                    current = self.get_article_links()
                    if index >= len(current):
                        continue
                    link = current[index]
                    row = self.extract_row_metadata(link)

                    # 核心判定：期刊模式过滤 or 作者模式全量放行
                    if not self.paper_allowed(row):
                        continue

                    stem = safe_filename(str(row.get("title") or link.text))
                    if stem in self.downloaded_titles:
                        logger.info("⏭️ 本地已有同名 PDF，跳过重复下载：%s", row.get("title"))
                        self.stats["skipped"] += 1
                        continue

                    self.process_article(link, row)

                if not self.goto_next_page():
                    break
                page_number += 1
        finally:
            self.print_summary()
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass

    def print_summary(self) -> None:
        duration = time.time() - self.stats["start_time"]
        mode_desc = "✍️ 作者模式（不限期刊全量下载）" if getattr(config, "RUN_MODE", "") == "author" else "🎯 期刊模式（CLSCI法学核心过滤）"
        summary = f"""
============================================================
              🎉 知网文献采集整理完成
============================================================
  运行模式: {mode_desc}
  耗时: {duration:.1f} 秒
  成功归档 (PDF + 分页TXT): {self.stats['success']} 篇
  已存在/跳过: {self.stats['skipped']} 篇
  仅保存元数据 (无PDF): {self.stats['metadata_only']} 篇
  Obsidian卡片创建: {self.stats['stubs']} 篇
  失败: {self.stats['failed']} 篇
------------------------------------------------------------
  PDF 归档目录: {config.DATA_ROOT}
  分页 TXT 目录: {config.TXT_DIR}
  结构化元数据: {config.METADATA_DIR}
  页码索引目录: {config.PAGE_INDEX_DIR}
============================================================
"""
        logger.info(summary)
        print(summary)


if __name__ == "__main__":
    downloader = CNKIPDFDownloader()
    try:
        downloader.run()
    except KeyboardInterrupt:
        logger.info("用户手动中止采集任务。")
        downloader.print_summary()
