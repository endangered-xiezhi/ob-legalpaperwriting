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
import signal
import sys
import threading
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
    find_existing_stub,
    link_pdf_to_vaults,
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
        self._stop_requested = False
        self._is_terminating = False
        self.log_filename = log_filename.name
        self.stats = {
            "success": 0,
            "stubs": 0,
            "metadata_only": 0,
            "skipped": 0,
            "failed": 0,
            "duplicates": [],
            "start_time": time.time(),
        }
        self.download_history: dict[str, dict] = {}
        self.downloaded_titles, self.downloaded_record_ids = self.load_download_history()

    def setup_signals(self) -> None:
        """在终端运行环境下注册 SIGINT (Ctrl+C) 与 SIGTERM 监听，支持优雅秒级收尾。"""
        def _sig_handler(signum, frame):
            logger.info("\n🛑 [CNKI Spider] 接收到终端终止信号 (%s)，正在安全停止采集并对齐 Obsidian 论文库...", signum)
            self._stop_requested = True
            raise KeyboardInterrupt("用户按键或系统终止信号")

        try:
            signal.signal(signal.SIGINT, _sig_handler)
            signal.signal(signal.SIGTERM, _sig_handler)
        except Exception:
            pass

    def _start_terminal_listener(self) -> None:
        """启动终端后台按键监听：采集中随时输入 'q' 并回车即可立即秒级终止采集并安全归档。"""
        def _listen():
            while not self._stop_requested:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        break
                    cmd = line.strip().lower()
                    if cmd in ("q", "quit", "exit", "stop", "终止", "退出"):
                        logger.info("🛑 终端后台监听捕获到退出指令: %s", cmd)
                        print(f"\n🛑 [CNKI Spider] 接收到终端 '{cmd}' 退出指令，正在安全停止采集并立即执行归档...")
                        self._stop_requested = True
                        try:
                            flag_candidates = [
                                Path(config.BASE_DIR).parent / "local_bridge" / "runtime" / "stop_crawler.flag",
                                Path(config.DATA_ROOT).parent.parent / "local_bridge" / "runtime" / "stop_crawler.flag",
                                Path("/Users/kansang/Documents/Codex/2026-08-08/h/local_bridge/runtime/stop_crawler.flag"),
                            ]
                            for flag in flag_candidates:
                                flag.parent.mkdir(parents=True, exist_ok=True)
                                flag.write_text("stop", encoding="utf-8")
                        except Exception:
                            pass
                        try:
                            os.kill(os.getpid(), signal.SIGINT)
                        except Exception:
                            pass
                        break
                except Exception:
                    break

        try:
            t = threading.Thread(target=_listen, name="CNKI-Terminal-Listener", daemon=True)
            t.start()
        except Exception:
            pass

    def load_download_history(self) -> tuple[set[str], set[str]]:
        """读取本地已有 PDF、元数据记录、历史日志及目标 Obsidian 知识库，用于增量精准去重与源头追溯。"""
        titles: set[str] = set()
        record_ids: set[str] = set()
        self.download_history = {}

        # 1. 扫描历史运行日志 (logs/*.log)
        log_dir = Path(config.LOG_DIR)
        if log_dir.exists():
            for log_path in sorted(log_dir.glob("*.log")):
                log_name = log_path.name
                m_batch = re.search(r"cnki_spider_(\d{8}_\d{6})", log_name)
                batch_str = m_batch.group(1) if m_batch else log_name
                try:
                    with log_path.open("r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            m_art = re.search(r"正在采集：(.+)", line)
                            if m_art:
                                raw_t = m_art.group(1).strip()
                                clean_t = re.sub(r"[^\w\u4e00-\u9fa5]", "", raw_t)
                                if clean_t:
                                    self.download_history[clean_t] = {
                                        "title": raw_t,
                                        "log_file": log_name,
                                        "batch": batch_str,
                                        "source": "历史采集日志",
                                    }
                                    titles.add(safe_filename(raw_t))
                            m_pdf = re.search(r"归档残留临时 PDF：(.+?)(?:__[\w\-]+)?\.pdf", line)
                            if m_pdf:
                                raw_t = m_pdf.group(1).strip()
                                clean_t = re.sub(r"[^\w\u4e00-\u9fa5]", "", raw_t)
                                if clean_t and clean_t not in self.download_history:
                                    self.download_history[clean_t] = {
                                        "title": raw_t,
                                        "log_file": log_name,
                                        "batch": batch_str,
                                        "source": "历史归档记录",
                                    }
                                    titles.add(safe_filename(raw_t))
                except OSError:
                    pass

        # 2. 扫描已有的物理 PDF 文件
        for path in Path(config.DATA_ROOT).rglob("*.pdf"):
            stem_clean = re.sub(r"__[A-Za-z0-9_-]{6,}$", "", path.stem)
            titles.add(stem_clean)
            c_key = re.sub(r"[^\w\u4e00-\u9fa5]", "", stem_clean)
            if c_key and c_key not in self.download_history:
                self.download_history[c_key] = {
                    "title": stem_clean,
                    "log_file": f"data/{path.parent.name}/{path.name}",
                    "batch": path.parent.name,
                    "source": "本地已存在PDF",
                }

        # 3. 扫描已有的结构化元数据 (metadata/*.json)
        for path in Path(config.METADATA_DIR).glob("*.json"):
            try:
                item = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            rec_id = str(item.get("record_id") or "")
            item_title = str(item.get("title") or "")
            clean_t = re.sub(r"[^\w\u4e00-\u9fa5]", "", item_title)
            cap_time = str(item.get("captured_at") or "")
            m_cap = re.search(r"(\d{4}-\d{2}-\d{2})", cap_time)
            batch_date = m_cap.group(1) if m_cap else "已入库元数据"

            info = {
                "title": item_title,
                "log_file": path.name,
                "batch": batch_date,
                "source": "已归档元数据",
            }
            if rec_id:
                record_ids.add(rec_id)
                self.download_history[rec_id] = info
            if clean_t:
                titles.add(safe_filename(item_title))
                if clean_t not in self.download_history:
                    self.download_history[clean_t] = info

        # 4. 扫描目标 Obsidian 论文库 (/Users/kansang/Downloads/Obsidian Vault/11论文收集)
        obs_11_dir = Path(config.OBSIDIAN_VAULT_ROOT) / "11论文收集"
        if obs_11_dir.exists():
            for root, dirs, files in os.walk(obs_11_dir):
                for f in files:
                    if f.endswith(".md"):
                        stem = f[:-3]
                        clean_t = re.sub(r"[^\w\u4e00-\u9fa5]", "", stem)
                        rel_p = os.path.relpath(os.path.join(root, f), config.OBSIDIAN_VAULT_ROOT)
                        if clean_t and clean_t not in self.download_history:
                            self.download_history[clean_t] = {
                                "title": stem,
                                "log_file": rel_p,
                                "batch": os.path.basename(os.path.dirname(root)),
                                "source": "Obsidian 11论文收集",
                            }
                            titles.add(safe_filename(stem))

        logger.info(
            "已读取历史查重台账：%s 个题名，%s 个稳定记录ID（命中历史文献将自动精准追溯并跳过）。",
            len(titles),
            len(record_ids),
        )
        return titles, record_ids

    def is_stop_requested(self) -> bool:
        """检查外部是否有终止采集的控制指令（如来自前端UI、命令行 Ctrl+C 或信号文件）。"""
        if self._stop_requested:
            return True
        flag_candidates = [
            Path(config.BASE_DIR).parent / "local_bridge" / "runtime" / "stop_crawler.flag",
            Path(config.DATA_ROOT).parent.parent / "local_bridge" / "runtime" / "stop_crawler.flag",
            Path("/Users/kansang/Documents/Codex/2026-08-08/h/local_bridge/runtime/stop_crawler.flag"),
        ]
        if any(f.exists() for f in flag_candidates):
            self._stop_requested = True
            return True
        return False

    def finalize_and_archive(self) -> None:
        """终止后归档与双仓对齐收尾流程：确保所有已下载和已抓取文献100%沉淀至Obsidian。"""
        if self._is_terminating:
            return
        self._is_terminating = True
        logger.info("📦 正在执行终止收尾：扫描未归档文件并对齐 Obsidian 论文库...")
        # 1. 扫描临时 downloads 目录中是否有已下载完毕的 PDF
        try:
            download_dir = Path(config.DOWNLOAD_DIR)
            if download_dir.exists():
                for pdf in download_dir.glob("*.pdf"):
                    if not pdf.name.endswith(".crdownload"):
                        target_dir = Path(config.DATA_ROOT) / "unsorted"
                        target_dir.mkdir(parents=True, exist_ok=True)
                        dest = target_dir / pdf.name
                        if not dest.exists():
                            shutil.move(str(pdf), dest)
                            logger.info("归档残留临时 PDF：%s", dest.name)
                        link_pdf_to_vaults(dest, {"title": dest.stem})
        except Exception as exc:
            logger.warning("归档临时 PDF 异常：%s", exc)

        # 1.1 全量确保 DATA_ROOT 中所有 PDF 均已在 Obsidian 库建立了零空间软链接
        try:
            data_dir = Path(config.DATA_ROOT)
            if data_dir.exists():
                for pdf_file in data_dir.rglob("*.pdf"):
                    if not pdf_file.name.endswith(".crdownload"):
                        link_pdf_to_vaults(pdf_file, {"title": pdf_file.stem})
        except Exception as exc:
            logger.warning("全量建立 Obsidian PDF 软链接异常：%s", exc)

        # 2. 扫描 metadata 目录，确保每一份 JSON 元数据均已落盘为 Obsidian Markdown 样板笔记
        try:
            meta_dir = Path(config.METADATA_DIR)
            stub_dir = Path(config.PAPER_STUB_DIR)
            stub_dir.mkdir(parents=True, exist_ok=True)
            if meta_dir.exists():
                archived_new = 0
                for json_file in meta_dir.glob("*.json"):
                    try:
                        data = json.loads(json_file.read_text(encoding="utf-8"))
                        if not data.get("title"):
                            continue
                        existing = find_existing_stub(stub_dir, data)
                        stub_path, created = upsert_obsidian_stub(data, stub_dir, existing)
                        if created:
                            archived_new += 1
                            self.stats["stubs"] += 1
                    except Exception:
                        continue
                if archived_new > 0:
                    logger.info("✅ 终止归档完成：补全生成了 %s 篇 Obsidian 样板卡片。", archived_new)
        except Exception as exc:
            logger.warning("补全元数据样板异常：%s", exc)

        # 3. 清理 stop_crawler.flag
        try:
            flag_candidates = [
                Path(config.BASE_DIR).parent / "local_bridge" / "runtime" / "stop_crawler.flag",
                Path(config.DATA_ROOT).parent.parent / "local_bridge" / "runtime" / "stop_crawler.flag",
                Path("/Users/kansang/Documents/Codex/2026-08-08/h/local_bridge/runtime/stop_crawler.flag"),
            ]
            for flag in flag_candidates:
                if flag.exists():
                    flag.unlink(missing_ok=True)
        except OSError:
            pass

        # 4. 更新 crawler_status.json
        try:
            status_candidates = [
                Path(config.BASE_DIR).parent / "local_bridge" / "runtime" / "crawler_status.json",
                Path(config.DATA_ROOT).parent.parent / "local_bridge" / "runtime" / "crawler_status.json",
                Path("/Users/kansang/Documents/Codex/2026-08-08/h/local_bridge/runtime/crawler_status.json"),
            ]
            for status_file in status_candidates:
                if status_file.parent.exists():
                    status_file.write_text(json.dumps({
                        "running": False,
                        "stopped_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                        "stats": self.stats,
                    }, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

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
        print("\n" + "=" * 66)
        print("📌 【第一步】：请在弹出的 Chrome 浏览器中登录知网")
        print("   （如校园网认证、CARSI 认证或知网个人账号）")
        print("   👉 登录成功后在此窗口按【回车】继续；或随时输入【q】/ 按【Ctrl+C】安全终止退出并归档")
        print("=" * 66)
        try:
            resp = input("👉 请按回车继续 (输入 q 退出): ").strip().lower()
            if resp in ("q", "quit", "exit", "stop"):
                print("\n🛑 用户在登录步骤选择终止退出。")
                self._stop_requested = True
                raise KeyboardInterrupt("用户在登录步骤选择退出")
        except (KeyboardInterrupt, EOFError):
            self._stop_requested = True
            raise KeyboardInterrupt("用户按键或信号终止")

    def wait_for_search_setup(self) -> None:
        mode = getattr(config, "RUN_MODE", "journal")
        if mode == "author" or not getattr(config, "FILTER_BY_JOURNAL", True):
            target_authors = getattr(config, "TARGET_AUTHORS", [])
            if isinstance(target_authors, str):
                target_authors = [a.strip() for a in re.split(r"[,，\s]+", target_authors) if a.strip()]
            author_tip = f"（目标学者：{'、'.join(target_authors)}）" if target_authors else "（不限学者，结果全部全量下载）"
            print("\n" + "=" * 66)
            print(f"📌 【第二步 - 学者/全量采集模式 {author_tip}】：")
            print("   请在知网页面输入学者姓名并点击检索；进入结果列表后，建议将每页显示数量设为【50条】。")
            print("   💡 本模式下已解除期刊限制，列表中的全部文献均会按顺序自动下载并归档！")
        else:
            print("\n" + "=" * 66)
            print("📌 【第二步 - 法学核心期刊过滤模式】：")
            print("   请在知网页面输入主题/关键词检索；进入结果列表后，建议将每页显示数量设为【50条】。")
            print("   💡 本模式将仅下载符合法学核心期刊白名单的文献，其它期刊将自动跳过。")
        print("   👉 确认已进入结果列表页后按【回车】正式开始采集；或输入【q】/ 按【Ctrl+C】安全终止退出")
        print("=" * 66)
        try:
            resp = input("👉 请按回车正式开始自动采集 (输入 q 退出): ").strip().lower()
            if resp in ("q", "quit", "exit", "stop"):
                print("\n🛑 用户在检索设置步骤选择终止退出。")
                self._stop_requested = True
                raise KeyboardInterrupt("用户在检索设置步骤选择退出")
        except (KeyboardInterrupt, EOFError):
            self._stop_requested = True
            raise KeyboardInterrupt("用户按键或信号终止")
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
            if isinstance(target_authors, str):
                target_authors = [a.strip() for a in re.split(r"[,，\s]+", target_authors) if a.strip()]
            if not target_authors:
                # 用户没有指定具体姓名，则检索出来的所有条目一律全量下载
                return True

            # 若指定了作者名单，则核实作者列表是否匹配
            authors = [str(a).strip() for a in row_metadata.get("authors", [])]
            for target in target_authors:
                if any(target in a for a in authors):
                    return True

            logger.info("⏭️ 跳过非指定作者文献：%s（文献作者：%s；筛选作者：%s）", row_metadata.get("title"), "、".join(authors), "、".join(target_authors))
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
            const clean = (s) => (s ? String(s).replace(/\s+/g, ' ').trim() : '');
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
            if self.is_stop_requested():
                logger.info("🛑 wait_for_new_pdf 检测到终止请求，提前退出下载等待。")
                return None
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
            try:
                resp = input("⚠️ 知网详情页要求滑动验证，请手动完成后按回车继续 (输入 q 终止)……").strip().lower()
                if resp in ("q", "quit", "exit", "stop"):
                    self._stop_requested = True
            except (KeyboardInterrupt, EOFError):
                self._stop_requested = True
        return handle

    def click_pdf_download(self) -> bool:
        assert self.driver is not None
        # 1. 优先尝试 CSS 选择器
        for selector in config.PDF_DOWNLOAD_SELECTORS:
            if ":contains(" in selector:
                continue
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                self.driver.execute_script("arguments[0].click();", button)
                logger.info("已点击 PDF 下载按钮：%s", selector)
                return True
            except (NoSuchElementException, WebDriverException):
                continue

        # 2. 备选 XPath 策略（全面覆盖知网新版HTML5详情页、旧版、海外版等不同DOM结构）
        xpath_candidates = [
            "//a[@id='pdfDown']",
            "//a[contains(@class, 'btn-dlpdf') or contains(@class, 'dlpdf')]",
            "//a[contains(normalize-space(.), 'PDF下载') or contains(normalize-space(.), 'PDF 下载')]",
            "//a[contains(@href, 'download') and (contains(normalize-space(.), 'PDF') or contains(normalize-space(.), '下载'))]",
            "//a[contains(normalize-space(.), '整本下载') or contains(normalize-space(.), '分章下载')]",
            "//li[@id='pdfDown']/a",
            "//div[contains(@class, 'operate-btn')]//a[contains(., 'PDF')]",
            "//a[contains(@class, 'btn-download') or contains(@class, 'down-btn')]",
        ]
        for xp in xpath_candidates:
            try:
                elem = self.driver.find_element(By.XPATH, xp)
                self.driver.execute_script("arguments[0].click();", elem)
                logger.info("已通过 XPath 点击 PDF 下载按钮：%s", xp)
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
        clean_key = re.sub(r"[^\w\u4e00-\u9fa5]", "", title)

        # 1. 列表层快速比对历史台账查重（无需点开详情页，秒级跳过）
        if clean_key and clean_key in self.download_history:
            dup = self.download_history[clean_key]
            msg = f"⚠️ [重复跳过] 《{title}》已在【{dup['source']}】(日志/路径: {dup['log_file']}, 批次: {dup['batch']}) 中采集过，跳过下载与重复建卡。"
            logger.info(msg)
            print(f"\n{msg}")
            self.stats["skipped"] += 1
            self.stats["duplicates"].append({"title": title, **dup})
            return

        logger.info("正在采集：%s", title)
        self.clear_downloads_dir()
        stub_path: Path | None = None
        metadata: dict = {}
        stub_dir: Path | None = None
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

            # 2. 详情层根据稳定记录ID或正式标题二次精准查重
            rec_id = str(metadata.get("record_id") or "")
            clean_title = re.sub(r"[^\w\u4e00-\u9fa5]", "", str(metadata.get("title") or title))
            if rec_id in self.download_history or (clean_title and clean_title in self.download_history):
                dup = self.download_history.get(rec_id) or self.download_history.get(clean_title)
                msg = f"⚠️ [重复跳过] 《{title}》(稳定ID: {rec_id}) 已在【{dup['source']}】(日志/路径: {dup['log_file']}, 批次: {dup['batch']}) 中采集过，跳过下载与重复建卡。"
                logger.info(msg)
                print(f"\n{msg}")
                self.stats["skipped"] += 1
                self.stats["duplicates"].append({"title": title, **dup})
                return

            # 核心产物落地：按 [项目/批次/年份] 写入 Obsidian 11论文收集
            year = str(metadata.get("year") or "unsorted").strip()
            if not re.match(r"^\d{4}$", year):
                year = "unsorted"
            stub_dir = Path(config.get_paper_stub_dir(year))
            stub_path, created = upsert_obsidian_stub(metadata, stub_dir)
            metadata["obsidian_note_path"] = str(stub_path)
            if created:
                self.stats["stubs"] += 1
                logger.info("✅ 已直接生成 Obsidian Markdown 笔记：%s", stub_path.name)
            else:
                logger.info("ℹ️ 已匹配现有 Obsidian 笔记，保留人工内容并更新元数据：%s", stub_path.name)

            # 更新当前运行时历史台账，防止同批次后续检索项重复
            curr_info = {
                "title": title,
                "log_file": self.log_filename,
                "batch": getattr(config, "BATCH_NAME", "当前批次") or "当前批次",
                "source": "本次当前批次",
            }
            if clean_title:
                self.download_history[clean_title] = curr_info
            if rec_id:
                self.download_history[rec_id] = curr_info

            try:
                write_manifest(metadata, Path(config.METADATA_DIR))
            except OSError:
                pass

            windows_before_download = set(self.driver.window_handles)
            if not self.click_pdf_download():
                metadata["ingest_warning"] = "未找到PDF下载按钮"
                upsert_obsidian_stub(metadata, stub_dir, stub_path)
                try:
                    write_manifest(metadata, Path(config.METADATA_DIR))
                except OSError:
                    pass
                self.stats["metadata_only"] += 1
                logger.warning("只保存元数据笔记，未找到 PDF 下载按钮：%s", title)
                return

            time.sleep(2)
            download_windows = set(self.driver.window_handles) - windows_before_download
            if download_windows:
                try:
                    self.driver.switch_to.window(list(download_windows)[-1])
                except WebDriverException:
                    pass
                if self._captcha_visible():
                    try:
                        resp = input("⚠️ 知网下载页要求滑动验证，请手动完成后按回车继续 (输入 q 终止)……").strip().lower()
                        if resp in ("q", "quit", "exit", "stop"):
                            self._stop_requested = True
                            return
                    except (KeyboardInterrupt, EOFError):
                        self._stop_requested = True
                        return
            elif self._captcha_visible():
                try:
                    resp = input("⚠️ PDF 下载触发滑动验证，请手动完成后按回车继续 (输入 q 终止)……").strip().lower()
                    if resp in ("q", "quit", "exit", "stop"):
                        self._stop_requested = True
                        return
                except (KeyboardInterrupt, EOFError):
                    self._stop_requested = True
                    return

            if self.is_stop_requested():
                return

            downloaded = self.wait_for_new_pdf()
            if not downloaded:
                metadata["ingest_warning"] = "PDF下载超时或失败"
                upsert_obsidian_stub(metadata, Path(config.PAPER_STUB_DIR), stub_path)
                try:
                    write_manifest(metadata, Path(config.METADATA_DIR))
                except OSError:
                    pass
                self.stats["metadata_only"] += 1
                logger.warning("只保存元数据笔记，PDF 下载超时：%s", title)
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

            # 核心：将已下载物理 PDF 立即无冗余软链接至 Obsidian 库的 知识产权/PDF/ 目录
            link_pdf_to_vaults(pdf_path, metadata)

            # 自动提取带 [[PDF_PAGE:n]] 标柱的 TXT 和页码对照索引
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

            # 直接回写实际 PDF/TXT 路径与最新状态至 Obsidian Markdown 笔记
            target_dir = stub_dir or Path(config.get_paper_stub_dir())
            stub_path, _ = upsert_obsidian_stub(metadata, target_dir, stub_path)
            try:
                write_manifest(metadata, Path(config.METADATA_DIR))
            except OSError:
                pass

            self.downloaded_titles.add(stem)
            self.downloaded_record_ids.add(metadata["record_id"])
            self.stats["success"] += 1
            logger.info("✅ 采集成功并完成 Obsidian 笔记落盘：%s", stub_path.name if stub_path else pdf_path.name)
        except (Exception, KeyboardInterrupt) as exc:
            is_interrupt = isinstance(exc, KeyboardInterrupt)
            self.stats["failed" if not is_interrupt else "metadata_only"] += 1
            if is_interrupt:
                logger.info("⚠️ 采集过程收到中断信号，立即保存当前文献元数据样板：%s", title)
            else:
                logger.exception("采集文章失败 %s：%s", title, exc)
            if metadata:
                metadata["ingest_warning"] = "用户手动中止采集" if is_interrupt else f"采集异常：{exc}"
                try:
                    target_dir = stub_dir or Path(config.get_paper_stub_dir())
                    upsert_obsidian_stub(metadata, target_dir, stub_path)
                except Exception:
                    pass
                try:
                    write_manifest(metadata, Path(config.METADATA_DIR))
                except OSError:
                    pass
            if is_interrupt:
                raise
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
        self.setup_signals()
        self._start_terminal_listener()
        try:
            self.wait_for_user_login()
            self.wait_for_search_setup()
            print("\n" + "=" * 66)
            print("🚀 开始自动采集！")
            print("💡 采集中随时在终端输入【q + 回车】或按【Ctrl+C】可立即安全终止并归档！")
            print("=" * 66 + "\n")
            logger.info("采集中随时在终端输入【q + 回车】或按【Ctrl+C】可立即安全终止并归档。")
            page_number = 1
            while not self.is_stop_requested():
                logger.info("============ 正在处理第 %s 页 ============", page_number)
                self._ensure_window_alive()
                if self._captcha_visible():
                    try:
                        c_resp = input("⚠️ 结果列表页要求滑动验证，请手动完成后按回车继续 (输入 q 退出)……").strip().lower()
                        if c_resp in ("q", "quit", "exit", "stop"):
                            self._stop_requested = True
                            break
                    except (KeyboardInterrupt, EOFError):
                        self._stop_requested = True
                        break
                links = self.get_article_links()
                if not links:
                    logger.info("当前页未检测到更多文章链接。")
                    break
                logger.info("当前页共检测到 %s 篇文献，开始处理。", len(links))
                for index in range(len(links)):
                    if self.is_stop_requested():
                        logger.info("🛑 检测到终止采集指令，停止处理后续文献，立即执行归档...")
                        break
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

                if self.is_stop_requested():
                    break
                if not self.goto_next_page():
                    break
                page_number += 1
        except (KeyboardInterrupt, SystemExit):
            logger.info("🛑 知网采集进程已捕获终止指令，正在退出并执行安全归档。")
        finally:
            try:
                self.finalize_and_archive()
            except Exception as exc:
                logger.error("执行收尾归档发生异常：%s", exc)
            self.print_summary()
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None

    def print_summary(self) -> None:
        duration = time.time() - self.stats["start_time"]
        mode = getattr(config, "RUN_MODE", "")
        target_authors = getattr(config, "TARGET_AUTHORS", [])
        if mode == "author" or not getattr(config, "FILTER_BY_JOURNAL", True):
            mode_desc = f"✍️ 作者模式（指定学者：{'、'.join(target_authors)}）" if target_authors else "✍️ 作者/全量模式（不限学者全量下载）"
        else:
            mode_desc = "🎯 期刊模式（CLSCI法学核心过滤）"
        status_banner = "🛑 知网文献采集已安全终止 (已完成全部数据对齐与归档)" if self._stop_requested else "🎉 知网文献采集整理完成"

        dup_section = ""
        if self.stats.get("duplicates"):
            dup_lines = ["\n📋 历史重复文献对照明细 (已自动去重并精准溯源)："]
            for idx, dup in enumerate(self.stats["duplicates"], 1):
                dup_lines.append(
                    f"  [{idx}] 《{dup['title']}》\n"
                    f"      ↳ 重复来源: 【{dup['source']}】\n"
                    f"      ↳ 历史日志/路径: {dup['log_file']} (批次: {dup['batch']})"
                )
            dup_section = "\n".join(dup_lines) + "\n"

        target_obsidian_dir = getattr(config, "get_paper_stub_dir", lambda: config.PAPER_STUB_DIR)()
        summary = f"""
============================================================
              {status_banner}
============================================================
  运行模式: {mode_desc}
  耗时: {duration:.1f} 秒
  成功归档 (PDF + 分页TXT): {self.stats['success']} 篇
  已存在/跳过: {self.stats['skipped']} 篇
  仅保存元数据 (无PDF): {self.stats['metadata_only']} 篇
  Obsidian卡片创建: {self.stats['stubs']} 篇
  失败: {self.stats['failed']} 篇{dup_section}
------------------------------------------------------------
  Obsidian 论文库: {target_obsidian_dir}
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
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as exc:
        logger.exception("采集器遇到异常退出：%s", exc)
        sys.exit(1)
    sys.exit(0)
