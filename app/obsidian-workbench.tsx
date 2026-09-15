"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

const BRIDGE = "http://127.0.0.1:8765";

type View = "overview" | "intake" | "library" | "relations" | "citations" | "agents" | "export";
type LibraryFilter = "all" | "formal" | "pending" | "unclassified";

type LinkItem = { target: string; label: string; path?: string };
type NoteRecord = {
  path: string;
  title: string;
  folder: string;
  type: string;
  authors: string[];
  year: string;
  journal: string;
  domain: string;
  status: string;
  warning: string;
  topics: string[];
  paths: string[];
  summary: string;
  modified: string;
  links: LinkItem[];
  headings: Array<{ level: number; text: string }>;
  isPaper: boolean;
  isFormal: boolean;
  isCanonicalDomain: boolean;
  isExcluded: boolean;
  isIntake: boolean;
  recordStatus: string;
  metadataStatus: string;
  screeningStatus: string;
  analysisStatus: string;
  relationStatus: string;
  citationStatus: string;
  recordId: string;
  issue: string;
  volume: string;
  pageRange: string;
  doi: string;
  cnkiId: string;
  sourcePdf?: string;
  pdfLink?: string;
};

type NoteDetail = NoteRecord & { backlinks: Array<{ path: string; title: string }>; localPath: string };

type NavigationData = {
  ok: boolean;
  vaultName: string;
  scope: string;
  generatedAt: string;
  version: string;
  stats: { notes: number; papers: number; formal: number; pending: number; intake: number; excluded: number; unclassified: number; domains: number; rulesAndCases?: number };
  quickLinks: Array<{ title: string; path: string; caption: string }>;
  rulebookHubs?: Array<{ title: string; path: string; caption: string }>;
  domains: Array<{ name: string; path: string; count: number; summary: string }>;
  controversies: NoteRecord[];
  researchPaths: NoteRecord[];
  recent: NoteRecord[];
  pending: NoteRecord[];
  intake: NoteRecord[];
  unclassified: NoteRecord[];
  searchNotes: NoteRecord[];
};

type Journal = { id: string; name: string; enabled: boolean; custom?: boolean };

const JOURNAL_NAMES = [
  "中国社会科学", "中国法学", "法学研究", "中外法学", "法学家", "法商研究", "法学", "法律科学",
  "法学评论", "政法论坛", "法制与社会发展", "现代法学", "比较法研究", "环球法律评论", "清华法学", "政治与法律",
];

const AGENTS = [
  { id: "paper", name: "论文整理 Agent", mark: "整", description: "按库内SOP核对元数据、全文结构、论证链和观点卡。" },
  { id: "controversy", name: "争议结构 Agent", mark: "争", description: "按具体命题比较观点、理由、条件和反驳关系。" },
  { id: "citation", name: "引文核验 Agent", mark: "核", description: "核查作者、年份、刊物、限定词和原文证据入口。" },
  { id: "trend", name: "研究趋势 Agent", mark: "趋", description: "只基于所选材料归纳库内年度变化和研究路径。" },
];

const NAV_ITEMS: Array<{ id: View; label: string; caption: string; glyph: string }> = [
  { id: "overview", label: "研究导航", caption: "领域 → 争议 → 论文", glyph: "⌂" },
  { id: "intake", label: "采集与待处理", caption: "知网 → 空白样板", glyph: "↓" },
  { id: "library", label: "论文目录", caption: "搜索与筛选", glyph: "▤" },
  { id: "relations", label: "关系工作台", caption: "争议矩阵与路径", glyph: "◎" },
  { id: "citations", label: "引注中心", caption: "Obsidian / Word", glyph: "注" },
  { id: "agents", label: "Agent 任务单", caption: "选择材料后复制", glyph: "✦" },
  { id: "export", label: "研究包导出", caption: "路径、引注与审计", glyph: "⇩" },
];

function shortDate(value: string) {
  return value ? value.slice(0, 10) : "—";
}

function noteMatches(note: NoteRecord, query: string) {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!words.length) return true;
  const haystack = [note.title, note.path, note.authors.join(" "), note.year, note.journal, note.domain, note.topics.join(" "), note.paths.join(" ")].join(" ").toLowerCase();
  return words.every((word) => haystack.includes(word));
}

function buildSimpleCitation(note: NoteRecord) {
  const authors = note.authors.join("、") || "作者待核";
  const journal = note.journal || "刊物待核";
  const year = note.year || "年份待核";
  const issue = note.issue ? `第${note.issue}期` : "";
  return `${authors}：《${note.title}》，载《${journal}》${year}年${issue}。`;
}

export default function ObsidianWorkbench() {
  const [view, setView] = useState<View>("overview");
  const [navigation, setNavigation] = useState<NavigationData | null>(null);
  const [bridgeState, setBridgeState] = useState<"loading" | "connected" | "offline">("loading");
  const [notice, setNotice] = useState("");
  const [query, setQuery] = useState("");
  const [libraryFilter, setLibraryFilter] = useState<LibraryFilter>("all");
  const [selectedNote, setSelectedNote] = useState<NoteDetail | null>(null);
  const [noteLoading, setNoteLoading] = useState(false);
  const [contextPaths, setContextPaths] = useState<string[]>([]);
  const [agentId, setAgentId] = useState("paper");
  const [agentTask, setAgentTask] = useState("");
  const [journals, setJournals] = useState<Journal[]>(JOURNAL_NAMES.map((name, index) => ({ id: `journal-${index}`, name, enabled: true })));
  const [newJournal, setNewJournal] = useState("");
  const [strictJournal, setStrictJournal] = useState(true);
  const [crawlerBusy, setCrawlerBusy] = useState(false);
  const [researchQuestion, setResearchQuestion] = useState("");
  const [keywordText, setKeywordText] = useState("");
  const [yearRange, setYearRange] = useState("");
  const [screeningReasons, setScreeningReasons] = useState<Record<string, string>>({});
  const [citationPath, setCitationPath] = useState("");
  const [citationMode, setCitationMode] = useState<"direct" | "paraphrase" | "general" | "short">("paraphrase");
  const [pinpointPage, setPinpointPage] = useState("");
  const [citationResult, setCitationResult] = useState<{
    citation: string;
    shortCitation?: string;
    wordFootnote?: string;
    obsidianMarker: string;
    obsidianDefinition: string;
    markdownFootnote?: string;
    verification: string;
  } | null>(null);
  const [citationSearchQuery, setCitationSearchQuery] = useState("");

  const [quickCitationNote, setQuickCitationNote] = useState<NoteRecord | null>(null);
  const [quickPinpoint, setQuickPinpoint] = useState("");
  const [quickMode, setQuickMode] = useState<"paraphrase" | "direct" | "general" | "short">("paraphrase");
  const [quickResult, setQuickResult] = useState<{
    citation: string;
    shortCitation?: string;
    wordFootnote?: string;
    obsidianMarker?: string;
    obsidianDefinition?: string;
    markdownFootnote?: string;
    verification?: string;
  } | null>(null);
  const [quickError, setQuickError] = useState("");
  const versionRef = useRef("");

  const loadNavigation = useCallback(async (silent = false) => {
    if (!silent) setBridgeState("loading");
    try {
      const response = await fetch(`${BRIDGE}/api/vault/navigation`);
      if (!response.ok) throw new Error("navigation unavailable");
      const data = (await response.json()) as NavigationData;
      versionRef.current = data.version;
      setNavigation(data);
      setBridgeState("connected");
      if (silent) setNotice("检测到 Obsidian 内容变化，目录已自动更新。");
    } catch {
      if (!silent) setBridgeState("offline");
    }
  }, []);

  const checkVersion = useCallback(async () => {
    if (document.visibilityState !== "visible") return;
    try {
      const response = await fetch(`${BRIDGE}/api/vault/version`);
      if (!response.ok) return;
      const data = await response.json();
      if (versionRef.current && data.version !== versionRef.current) {
        await loadNavigation(true);
      }
    } catch {
      // Keep the last valid directory visible during a temporary bridge interruption.
    }
  }, [loadNavigation]);

  useEffect(() => {
    const initialTimer = window.setTimeout(() => void loadNavigation(), 0);
    const interval = window.setInterval(() => void checkVersion(), 10_000);
    const handleVisibility = () => {
      if (document.visibilityState === "visible") void checkVersion();
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      window.clearTimeout(initialTimer);
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [checkVersion, loadNavigation]);

  const searchMatches = useMemo(() => {
    if (!navigation || query.trim().length < 2) return [];
    return navigation.searchNotes.filter((note) => noteMatches(note, query)).slice(0, 12);
  }, [navigation, query]);

  const libraryNotes = useMemo(() => {
    if (!navigation) return [];
    let notes = navigation.searchNotes.filter((note) => note.isPaper && !note.isExcluded);
    if (libraryFilter === "formal") notes = notes.filter((note) => note.isFormal);
    if (libraryFilter === "pending") notes = navigation.pending;
    if (libraryFilter === "unclassified") notes = navigation.unclassified;
    return notes.filter((note) => noteMatches(note, query)).slice(0, 180);
  }, [navigation, libraryFilter, query]);

  async function copyText(text: string, message: string) {
    try {
      const copyValue = selectedNote?.path === text ? selectedNote.localPath : text;
      await navigator.clipboard.writeText(copyValue);
      setNotice(message);
    } catch {
      setNotice("浏览器未允许复制，请在 Obsidian 中使用该路径。");
    }
  }

  async function openNote(path: string) {
    setNoteLoading(true);
    try {
      const response = await fetch(`${BRIDGE}/api/vault/note?path=${encodeURIComponent(path)}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "读取失败");
      setSelectedNote(data.note);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "无法读取笔记");
    } finally {
      setNoteLoading(false);
    }
  }

  async function openInObsidian(path = "") {
    try {
      const response = await fetch(`${BRIDGE}/api/obsidian/open`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "打开失败");
      setNotice(path ? "已交给 Obsidian 打开原笔记。" : "已交给 Obsidian 打开知识库。");
    } catch {
      if (path) await copyText(path, "无法调用 Obsidian，笔记路径已复制。");
      else setNotice("未能调用 Obsidian，请直接打开本地仓库中的知识产权研究导航。");
    }
  }

  function toggleContext(path: string) {
    setContextPaths((current) => {
      if (current.includes(path)) return current.filter((item) => item !== path);
      if (current.length >= 8) {
        setNotice("一次最多选择 8 篇笔记作为 Agent 任务材料。");
        return current;
      }
      return [...current, path];
    });
  }

  function buildAgentTask() {
    const agent = AGENTS.find((item) => item.id === agentId) ?? AGENTS[0];
    const materials = contextPaths.length ? contextPaths.map((path) => `- ${path}`).join("\n") : "- 尚未选择材料";
    const rules: Record<string, string> = {
      paper: "核对题名、作者、年份、刊物、原文摘要、关键词、研究问题、论证链和制度方案。",
      controversy: "按具体争议命题列出结论、理由、适用条件、反驳对象、理论张力和证据入口。",
      citation: "逐项核验元数据、限定词、来源路径和原文定位，输出已核验、待核验与冲突清单。",
      trend: "只归纳所选材料体现的库内年份变化、领域分布和研究路径，明确样本边界。",
    };
    return `请作为「${agent.name}」完成任务：\n${agentTask || "梳理所选材料并提出下一步研究建议。"}\n\n必须先阅读并遵守：\n- 知识产权/研究趋势/法学论文整理SOP_Agent通用执行手册.md\n\n执行要求：\n1. ${rules[agent.id]}\n2. 只使用下列材料，不读取或推定整个知识库。\n3. 区分作者原文、Obsidian笔记概括和Agent推断。\n4. 不虚构文献、页码或引证；无法核验的内容明确标记。\n5. 输出可回到Obsidian复核的笔记路径。\n\n材料路径（${contextPaths.length}/8）：\n${materials}`;
  }

  function addJournal() {
    const name = newJournal.trim();
    if (!name || journals.some((journal) => journal.name === name)) return;
    setJournals((current) => [...current, { id: `custom-${Date.now()}`, name, enabled: true, custom: true }]);
    setNewJournal("");
  }

  async function startCrawler() {
    const enabled = journals.filter((journal) => journal.enabled).map((journal) => journal.name);
    setCrawlerBusy(true);
    try {
      const response = await fetch(`${BRIDGE}/api/cnki/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          journals: enabled,
          strictJournal,
          researchQuestion,
          keywords: keywordText.split(/[，,；;\n]/).map((item) => item.trim()).filter(Boolean),
          yearRange,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "启动失败");
      setNotice(`${data.message} 新样板会自动出现在本页待处理队列。`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "无法启动知网爬虫");
    } finally {
      setCrawlerBusy(false);
    }
  }

  async function screenIntake(note: NoteRecord, decision: "included" | "excluded" | "pending") {
    try {
      const response = await fetch(`${BRIDGE}/api/intake/screening`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: note.path, decision, reason: screeningReasons[note.path] || "" }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "保存筛选结论失败");
      setNotice(decision === "included" ? "已纳入后续全文处理。" : decision === "excluded" ? "已排除并移出待处理统计。" : "已保留为待定。" );
      await loadNavigation();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "无法写入筛选结论");
    }
  }

  async function renderCitation() {
    if (!citationPath) {
      setNotice("请先选择一篇论文。");
      return;
    }
    try {
      const response = await fetch(`${BRIDGE}/api/citations/render`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: citationPath, mode: citationMode, pinpointPage }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "生成引注失败");
      setCitationResult(data);
      setNotice("引注已按《法学引注手册（2019）》生成，请回看PDF核验具体页码。");
    } catch (error) {
      setCitationResult(null);
      setNotice(error instanceof Error ? error.message : "无法生成引注");
    }
  }

  function downloadResearchPackage() {
    const selected = contextPaths.map((path) => navigation?.searchNotes.find((note) => note.path === path)).filter(Boolean);
    const payload = {
      packageVersion: 1,
      generatedAt: new Date().toISOString(),
      vault: navigation?.vaultName || "",
      scope: "知识产权",
      selectedNotes: selected,
      citation: citationResult,
      audit: [
        "本研究包仅包含用户明确选择的笔记元数据和路径。",
        "具体观点、引文页码与Agent输出仍须回到PDF和Obsidian核验。",
      ],
    };
    const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `LexTrace-研究包-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    setNotice("可复核研究包已导出到浏览器下载目录。");
  }

  async function openQuickCitation(note: NoteRecord) {
    setQuickCitationNote(note);
    setQuickPinpoint("");
    setQuickMode("paraphrase");
    setQuickError("");
    try {
      const response = await fetch(`${BRIDGE}/api/citations/render`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: note.path, mode: "general", pinpointPage: "" }),
      });
      const data = await response.json();
      if (response.ok && data.ok) {
        setQuickResult(data);
      } else {
        setQuickResult(null);
        setQuickError(data.error || "字段不完整");
      }
    } catch {
      setQuickResult(null);
    }
  }

  async function updateQuickCitation(note: NoteRecord, mode: "paraphrase" | "direct" | "general" | "short", pinpoint: string) {
    setQuickMode(mode);
    setQuickPinpoint(pinpoint);
    try {
      const response = await fetch(`${BRIDGE}/api/citations/render`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: note.path, mode, pinpointPage: pinpoint }),
      });
      const data = await response.json();
      if (response.ok && data.ok) {
        setQuickResult(data);
        setQuickError("");
      } else {
        setQuickError(data.error || "引注生成失败");
      }
    } catch {
      setQuickError("无法连接到本地服务");
    }
  }

  function noteActions(note: NoteRecord) {
    return (
      <span className="row-actions">
        {note.isPaper && (
          <button type="button" className="cite-action-btn" title="一键生成法学引注" onClick={() => void openQuickCitation(note)}>引注</button>
        )}
        <button type="button" className={contextPaths.includes(note.path) ? "selected" : ""} onClick={() => toggleContext(note.path)}>{contextPaths.includes(note.path) ? "已加入" : "+ Agent"}</button>
        <button type="button" onClick={() => void openInObsidian(note.path)}>OB ↗</button>
      </span>
    );
  }

  function renderOverview() {
    return (
      <>
        <section className="welcome-card navigation-hero">
          <div className="welcome-copy">
            <span className="eyebrow">OBSIDIAN · SINGLE SOURCE OF TRUTH</span>
            <h1>从采集到引注，<br />始终回到原笔记。</h1>
            <p>网页负责导览、采集入口、筛选和引注输出；论文样板、双链和研究内容仍以你的 Obsidian 为准。</p>
            <div className="welcome-actions">
              <button className="primary-button" type="button" onClick={() => void openInObsidian("知识产权/00_知识产权研究导航.md")}>打开原生研究导航</button>
              <button className="quiet-button" type="button" onClick={() => void loadNavigation()}>立即检查更新</button>
            </div>
          </div>
          <div className="vault-pulse">
            <div className={`pulse-ring ${bridgeState}`}><span>OB</span></div>
            <strong>{bridgeState === "connected" ? "本机工作台已连接" : bridgeState === "loading" ? "正在读取目录" : "请运行一键启动器"}</strong>
            <small>{navigation ? `自动检查 · 每10秒` : "原生导航始终可用"}</small>
          </div>
        </section>

        <section className="stat-row" aria-label="知识库状态">
          {[
            [navigation?.stats.formal ?? "—", "规范论文", "进入正式目录"],
            [navigation?.stats.rulesAndCases ?? "448", "法规与案例", "50部法规+395篇案例"],
            [navigation?.stats.intake ?? "—", "新采集样板", "等待初筛或Agent"],
            [navigation?.stats.domains ?? "—", "现有领域", "不自动改写分类"],
          ].map(([value, label, hint]) => <div className="stat-card" key={String(label)}><strong>{value}</strong><span>{label}</span><small>{hint}</small></div>)}
        </section>

        <div className="section-heading"><div><span className="eyebrow">START HERE</span><h2>现有知识库入口</h2></div><span>所有链接回到原笔记</span></div>
        <section className="route-grid">
          {(navigation?.quickLinks ?? []).map((link, index) => (
            <button className="route-card" type="button" key={link.path} onClick={() => void openNote(link.path)}>
              <span className="route-index">0{index + 1}</span><strong>{link.title}</strong><small>{link.caption}</small><span className="route-enter">预览目录 ↗</span>
            </button>
          ))}
        </section>

        <div className="section-heading spaced-heading"><div><span className="eyebrow">01 · DOMAINS</span><h2>按七个现有领域进入</h2></div><span>字段异常另列待归类</span></div>
        <section className="domain-card-grid">
          {(navigation?.domains ?? []).map((domain, index) => (
            <button type="button" className="domain-card" key={domain.path} onClick={() => void openNote(domain.path)}>
              <span>{String(index + 1).padStart(2, "0")}</span><strong>{domain.name}</strong><p>{domain.summary}</p><em>{domain.count} 篇规范记录</em>
            </button>
          ))}
        </section>

        {navigation?.rulebookHubs && navigation.rulebookHubs.length > 0 && (
          <>
            <div className="section-heading spaced-heading">
              <div><span className="eyebrow">02 · STATUTES & CASES</span><h2>知识产权法律法规与典型案例库</h2></div>
              <span>致谢 @StefanCHEN2026 · 法条 ↔ 司法解释 ↔ 典型案例双链网络</span>
            </div>
            <section className="route-grid">
              {navigation.rulebookHubs.map((hub, index) => (
                <button className="route-card" type="button" key={hub.path} onClick={() => void openNote(hub.path)}>
                  <span className="route-index">R0{index + 1}</span>
                  <strong>{hub.title}</strong>
                  <small>{hub.caption}</small>
                  <span className="route-enter">查看法条与案例 ↗</span>
                </button>
              ))}
            </section>
          </>
        )}

        <section className="overview-columns">
          <div className="panel-card">
            <div className="panel-head"><div><span className="eyebrow">03 · CONTROVERSIES</span><h3>争议专题</h3></div><button type="button" onClick={() => setView("relations")}>查看全部</button></div>
            <div className="domain-list">
              {(navigation?.controversies ?? []).slice(0, 7).map((note, index) => <button type="button" key={note.path} onClick={() => void openNote(note.path)}><span>{String(index + 1).padStart(2, "0")}</span><strong>{note.title}</strong><em>进入</em></button>)}
            </div>
          </div>
          <div className="panel-card">
            <div className="panel-head"><div><span className="eyebrow">04 · RECENT</span><h3>最近新增的规范论文</h3></div><span>{navigation ? shortDate(navigation.generatedAt) : "—"}</span></div>
            <div className="recent-list">
              {(navigation?.recent ?? []).slice(0, 8).map((note) => <button type="button" key={note.path} onClick={() => void openNote(note.path)}><span className="file-mark">MD</span><span><strong>{note.title}</strong><small>{note.authors.join("、")} · {note.year || shortDate(note.modified)}</small></span></button>)}
            </div>
          </div>
        </section>
      </>
    );
  }

  function renderLibrary() {
    const filters: Array<[LibraryFilter, string, number]> = [
      ["all", "全部论文", navigation?.stats.papers ?? 0],
      ["formal", "规范记录", navigation?.stats.formal ?? 0],
      ["pending", "待整理", navigation?.stats.pending ?? 0],
      ["unclassified", "待归类", navigation?.stats.unclassified ?? 0],
    ];
    return (
      <section className="library-layout">
        <aside className="folder-panel"><span className="eyebrow">DIRECTORY FILTERS</span><h2>论文目录</h2>{filters.map(([id, label, count]) => <button className={libraryFilter === id ? "active" : ""} type="button" key={id} onClick={() => setLibraryFilter(id)}><span>▸</span>{label}<em>{count}</em></button>)}<div className="context-box"><strong>Agent 材料</strong><span>{contextPaths.length} / 8</span><p>这里只保存路径选择，不读取或发送整个知识库。</p><button type="button" onClick={() => setView("agents")}>生成任务单</button></div></aside>
        <div className="library-main"><div className="library-toolbar"><div><span className="eyebrow">READ-ONLY INDEX</span><h1>{filters.find(([id]) => id === libraryFilter)?.[1]}</h1></div><span>当前显示 {libraryNotes.length} 条</span></div><div className="note-table-head"><span>笔记</span><span>作者／领域</span><span>年份</span><span>状态</span><span>操作</span></div><div className="note-table">{libraryNotes.map((note) => <article className="note-row" key={note.path}><button className="note-title" type="button" onClick={() => void openNote(note.path)}><strong>{note.title}</strong><small>{note.path}</small></button><span>{note.authors.join("、") || "作者待补"}<small>{note.domain || note.journal || "领域待补"}</small></span><span>{note.year || "—"}</span><span><i className={note.isFormal ? "verified" : "neutral"}>{note.isFormal ? "规范记录" : note.warning || "待整理"}</i></span>{noteActions(note)}</article>)}{!libraryNotes.length && <div className="empty-state">当前筛选下没有匹配笔记。</div>}</div></div>
      </section>
    );
  }

  function renderRelations() {
    const selectedRecords = contextPaths.map((path) => navigation?.searchNotes.find((note) => note.path === path)).filter(Boolean) as NoteRecord[];
    return (
      <section>
        <div className="page-intro relation-intro"><span className="eyebrow">CLAIM-TO-CLAIM RELATIONS</span><h1>关系工作台</h1><p>关系首先建立在“观点—观点”之间。知网只能提供引用线索；支持、反对、限定和扩展必须由全文证据确认。</p></div>
        <div className="relation-method-grid">
          <article><span>01 · CNKI</span><strong>直接引证</strong><p>参考文献、被引与施引线索，只证明书目联系。</p></article>
          <article><span>02 · FULL TEXT</span><strong>明确对话</strong><p>正文证据支持 supports、opposes、qualifies、extends。</p></article>
          <article><span>03 · RESEARCHER</span><strong>平行比较</strong><p>共同概念或方法必须标记为系统构造，不冒充作者争论。</p></article>
        </div>
        <div className="relation-selection panel-card"><div><span className="eyebrow">MATRIX MATERIALS</span><h3>已选 {selectedRecords.length} / 8 篇</h3><p>{selectedRecords.length ? selectedRecords.map((note) => note.title).join(" · ") : "请在论文目录或待处理队列选择材料。"}</p></div><button className="primary-button" type="button" disabled={!selectedRecords.length} onClick={() => { setAgentId("controversy"); setView("agents"); }}>生成关系分析任务单</button></div>
        <div className="section-heading"><div><span className="eyebrow">CONTROVERSIES</span><h2>现有争议专题</h2></div></div>
        <div className="topic-grid">{(navigation?.controversies ?? []).map((note, index) => <article className="topic-card" key={note.path}><span className="topic-number">{String(index + 1).padStart(2, "0")}</span><div><small>{note.type}</small><h3>{note.title}</h3><p>{note.summary}</p></div><div className="topic-actions"><button type="button" onClick={() => void openNote(note.path)}>摘要与双链</button><button type="button" onClick={() => void openInObsidian(note.path)}>Obsidian ↗</button><button type="button" onClick={() => toggleContext(note.path)}>{contextPaths.includes(note.path) ? "已加入 Agent" : "+ Agent 材料"}</button></div></article>)}</div>
        <div className="section-heading spaced-heading"><div><span className="eyebrow">RESEARCH PATHS</span><h2>清华研究路径</h2></div></div>
        <div className="topic-grid">{(navigation?.researchPaths ?? []).map((note, index) => <article className="topic-card path-card" key={note.path}><span className="topic-number">{String(index + 1).padStart(2, "0")}</span><div><small>研究路径</small><h3>{note.title}</h3><p>{note.summary}</p></div><div className="topic-actions"><button type="button" onClick={() => void openNote(note.path)}>摘要与双链</button><button type="button" onClick={() => void openInObsidian(note.path)}>Obsidian ↗</button></div></article>)}</div>
      </section>
    );
  }

  function renderAgents() {
    const selectedRecords = contextPaths.map((path) => navigation?.searchNotes.find((note) => note.path === path)).filter(Boolean) as NoteRecord[];
    const activeAgent = AGENTS.find((agent) => agent.id === agentId) ?? AGENTS[0];
    return (
      <section><div className="page-intro"><span className="eyebrow">COPYABLE TASK ROUTER</span><h1>把材料路径交给合适的 Agent</h1><p>本页不调用模型、不保存密钥，也不发送笔记正文；只生成一份遵守库内 SOP 的可复制任务单。</p></div><div className="agent-grid">{AGENTS.map((agent) => <button type="button" className={`agent-card ${agent.id === agentId ? "active" : ""}`} key={agent.id} onClick={() => setAgentId(agent.id)}><span className="agent-mark">{agent.mark}</span><strong>{agent.name}</strong><p>{agent.description}</p></button>)}</div><div className="agent-workspace"><div className="context-panel"><div className="panel-head"><div><span className="eyebrow">MATERIAL PATHS</span><h3>已选材料</h3></div><span>{selectedRecords.length} / 8</span></div>{selectedRecords.length ? selectedRecords.map((note) => <div className="context-note" key={note.path}><span>MD</span><div><strong>{note.title}</strong><small>{note.path}</small></div><button type="button" onClick={() => toggleContext(note.path)}>移除</button></div>) : <div className="context-empty">请先在论文目录、争议专题或笔记预览中加入材料。</div>}</div><div className="task-panel"><div className="panel-head"><div><span className="eyebrow">TASK TEMPLATE</span><h3>交给 {activeAgent.name}</h3></div><span>遵守库内 SOP</span></div><textarea value={agentTask} onChange={(event) => setAgentTask(event.target.value)} placeholder="例如：比较所选论文对AIGC用户独创性贡献的判断标准，并列明仍需回看原文的证据。" /><div className="task-preview"><pre>{buildAgentTask()}</pre></div><button className="primary-button" type="button" onClick={() => void copyText(buildAgentTask(), "Agent任务单已复制。")}>复制完整任务单</button></div></div></section>
    );
  }

  function renderIntake() {
    const intakeNotes = navigation?.intake ?? [];
    return (
      <section>
        <div className="page-intro">
          <span className="eyebrow">CNKI → OBSIDIAN INTAKE</span>
          <h1>采集与待处理</h1>
          <p>知网采集后立即建立 Obsidian 空白样板；样板只进入待处理队列，完成筛选、全文卡片和人工核验后才进入正式统计。</p>
        </div>
        <div className="capture-flow">
          <div><span>01</span><strong>采集结构化元数据</strong><small>作者、摘要、卷期、页码、知网ID</small></div><b>→</b>
          <div><span>02</span><strong>创建 Obsidian 样板</strong><small>record_status: intake</small></div><b>→</b>
          <div><span>03</span><strong>PDF 与分页 TXT</strong><small>保留原文页和页码候选</small></div><b>→</b>
          <div><span>04</span><strong>初筛与 Agent</strong><small>纳入、排除、待定和结构化分析</small></div>
        </div>

        <div className="intake-config-grid">
          <div className="panel-card research-profile-card">
            <div className="panel-head"><div><span className="eyebrow">RESEARCH PROFILE</span><h3>本次研究画像</h3></div><span>随采集任务保存</span></div>
            <label>研究问题<textarea value={researchQuestion} onChange={(event) => setResearchQuestion(event.target.value)} placeholder="例如：大模型训练使用受著作权保护作品时，合理使用与许可机制的边界是什么？" /></label>
            <div className="field-row"><label>关键词<input value={keywordText} onChange={(event) => setKeywordText(event.target.value)} placeholder="大模型训练，合理使用，许可" /></label><label>年份范围<input value={yearRange} onChange={(event) => setYearRange(event.target.value)} placeholder="2020-2026" /></label></div>
            <p>这里用于记录研究边界；知网具体检索条件仍在登录后的页面中设置。</p>
          </div>

          <div className="journal-section">
            <div className="panel-head"><div><span className="eyebrow">JOURNAL CARDS</span><h3>期刊范围</h3></div><label className="switch-label"><input type="checkbox" checked={strictJournal} onChange={(event) => setStrictJournal(event.target.checked)} /><span />严格匹配</label></div>
            <div className="journal-add"><input value={newJournal} onChange={(event) => setNewJournal(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") addJournal(); }} placeholder="手动输入新增期刊" /><button type="button" onClick={addJournal}>＋ 加入</button></div>
            <div className="journal-grid">{journals.map((journal) => <article className={`journal-card ${journal.enabled ? "enabled" : ""}`} key={journal.id}><button className="journal-toggle" type="button" onClick={() => setJournals((current) => current.map((item) => item.id === journal.id ? { ...item, enabled: !item.enabled } : item))}><span>{journal.enabled ? "✓" : ""}</span><strong>{journal.name}</strong><small>{journal.custom ? "手动加入" : "默认法学期刊"}</small></button>{journal.custom && <button className="journal-remove" type="button" onClick={() => setJournals((current) => current.filter((item) => item.id !== journal.id))}>删除</button>}</article>)}</div>
            <div className="crawler-bar"><div><strong>{journals.filter((journal) => journal.enabled).length} 种期刊已启用</strong><span>爬虫会创建样板，但不会把它标为正式论文。</span></div><button className="primary-button" type="button" disabled={crawlerBusy} onClick={() => void startCrawler()}>{crawlerBusy ? "正在连接…" : "登录知网并启动采集"}</button></div>
          </div>
        </div>

        <div className="section-heading spaced-heading"><div><span className="eyebrow">INTAKE QUEUE</span><h2>Obsidian 待处理样板</h2></div><span>{intakeNotes.length} 篇 · 自动更新</span></div>
        <div className="intake-queue">
          {intakeNotes.map((note) => (
            <article className="intake-card" key={note.path}>
              <div className="intake-card-main"><span className={`status-chip ${note.metadataStatus === "ready" ? "ready" : "pending"}`}>{note.metadataStatus === "ready" ? "元数据齐备" : "字段待补"}</span><h3>{note.title}</h3><p>{note.summary || "已建立空白样板，等待摘要或全文处理。"}</p><small>{note.authors.join("、") || "作者待补"} · {note.journal || "刊物待补"} · {note.year || "年份待补"}</small></div>
              <div className="intake-review"><input aria-label={`${note.title}筛选理由`} value={screeningReasons[note.path] || ""} onChange={(event) => setScreeningReasons((current) => ({ ...current, [note.path]: event.target.value }))} placeholder="填写纳入、排除或待定理由" /><div><button type="button" className="accept" onClick={() => void screenIntake(note, "included")}>纳入</button><button type="button" onClick={() => void screenIntake(note, "pending")}>待定</button><button type="button" className="reject" onClick={() => void screenIntake(note, "excluded")}>排除</button></div><div><button type="button" onClick={() => toggleContext(note.path)}>交给 Agent</button><button type="button" onClick={() => void openInObsidian(note.path)}>打开样板 ↗</button></div></div>
            </article>
          ))}
          {!intakeNotes.length && <div className="empty-state panel-card">尚无新采集样板。启动爬虫后，样板会自动出现在这里。</div>}
        </div>
      </section>
    );
  }

  function renderCitations() {
    const allPapers = (navigation?.searchNotes ?? []).filter((note) => note.isPaper && !note.isExcluded);
    const papers = citationSearchQuery.trim()
      ? allPapers.filter((note) => noteMatches(note, citationSearchQuery))
      : allPapers;
    const active = allPapers.find((note) => note.path === citationPath);
    return (
      <section>
        <div className="page-intro"><span className="eyebrow">2019 LEGAL CITATION MANUAL</span><h1>引注中心</h1><p>书目信息来自 Obsidian YAML，具体观点页码由你依据 PDF 核验。系统不会猜测缺失的作者、期号或页码。</p></div>
        <div className="citation-layout">
          <div className="panel-card citation-form">
            <div className="panel-head"><div><span className="eyebrow">SOURCE</span><h3>选择论文与引用方式</h3></div><span>{active?.citationStatus || "等待选择"}</span></div>
            <label className="citation-search-filter">
              快速筛选论文
              <input
                type="text"
                value={citationSearchQuery}
                onChange={(event) => setCitationSearchQuery(event.target.value)}
                placeholder="搜索题名、作者关键词快速过滤..."
              />
            </label>
            <label>论文 ({papers.length} 篇可用)<select value={citationPath} onChange={(event) => { setCitationPath(event.target.value); setCitationResult(null); }}><option value="">请选择论文</option>{papers.map((note) => <option value={note.path} key={note.path}>{note.title}｜{note.authors.join("、") || "作者待补"}</option>)}</select></label>
            <div className="field-row"><label>用途<select value={citationMode} onChange={(event) => setCitationMode(event.target.value as typeof citationMode)}><option value="paraphrase">转述观点（参见）</option><option value="direct">直接引语</option><option value="general">整篇文献列示</option><option value="short">前引文（再次引用）</option></select></label><label>具体印刷页码<input value={pinpointPage} onChange={(event) => setPinpointPage(event.target.value)} placeholder={citationMode === "general" ? "可留空" : "例如 163 或 163-165"} /></label></div>
            {active && <div className="citation-metadata"><span>{active.journal || "刊物待补"}</span><span>{active.year || "年份待补"}年{active.issue ? `第${active.issue}期` : ""}</span><span>{active.pageRange ? `全文 ${active.pageRange} 页` : "起止页待补"}</span>{(active.pdfLink || active.sourcePdf) && <span style={{ color: "var(--teal)", fontWeight: 650 }}>📄 PDF 已关联</span>}</div>}
            <button className="primary-button" type="button" onClick={() => void renderCitation()}>生成法学脚注</button>
          </div>
          <div className="panel-card citation-output">
            <div className="panel-head"><div><span className="eyebrow">OUTPUT</span><h3>Obsidian 与 Word</h3></div><span>{citationResult ? "待回看PDF" : "尚未生成"}</span></div>
            {citationResult ? <><div className="citation-preview"><strong>{citationResult.citation}</strong><small>状态：{citationResult.verification === "pinpoint_unverified" ? "页码由用户输入，仍需回看PDF" : "书目信息已生成"}</small></div><div className="citation-actions"><button type="button" onClick={() => void copyText(citationResult.citation, "Word脚注文本已复制。")}>复制 Word 脚注</button><button type="button" onClick={() => void copyText(citationResult.markdownFootnote || `${citationResult.obsidianMarker}\n${citationResult.obsidianDefinition}`, "Obsidian脚注已复制。")}>复制 Obsidian 脚注</button>{citationResult.shortCitation && <button type="button" onClick={() => void copyText(citationResult.shortCitation!, "前引文短注已复制。")}>复制前引文</button>}{active && <button type="button" onClick={() => void openInObsidian(active.path)}>回到原笔记 ↗</button>}</div></> : <div className="context-empty">选择论文并填写具体页码后生成。字段缺失时，系统会明确提示而不会补猜。</div>}
          </div>
        </div>
      </section>
    );
  }

  function renderExport() {
    const selectedRecords = contextPaths.map((path) => navigation?.searchNotes.find((note) => note.path === path)).filter(Boolean) as NoteRecord[];
    return (
      <section>
        <div className="page-intro"><span className="eyebrow">REPRODUCIBLE RESEARCH PACKAGE</span><h1>研究包导出</h1><p>只导出你明确选择的笔记路径、元数据、当前引注和核验提示，不复制整个知识库，也不上传 PDF。</p></div>
        <div className="export-layout">
          <div className="panel-card export-manifest"><div className="panel-head"><div><span className="eyebrow">MANIFEST</span><h3>本次材料</h3></div><span>{selectedRecords.length} / 8</span></div>{selectedRecords.length ? selectedRecords.map((note) => <div className="context-note" key={note.path}><span>MD</span><div><strong>{note.title}</strong><small>{note.path}</small></div><button type="button" onClick={() => toggleContext(note.path)}>移除</button></div>) : <div className="context-empty">请先在论文目录、待处理队列或关系工作台选择材料。</div>}</div>
          <div className="panel-card audit-card"><span className="eyebrow">AUDIT CONTENTS</span><h3>导出内容</h3><ul><li>所选论文的 Obsidian 路径与书目元数据</li><li>筛选、核验和引注状态</li><li>本轮生成的法学引注</li><li>缺失字段及回看 PDF 提示</li></ul><button className="primary-button" type="button" disabled={!selectedRecords.length} onClick={downloadResearchPackage}>导出 JSON 研究包</button></div>
        </div>
      </section>
    );
  }

  return (
    <main className="obsidian-app"><aside className="sidebar"><div className="brand"><span className="brand-mark">L</span><div><strong>LexTrace</strong><small>Obsidian Research Workbench</small></div></div><div className="vault-chip"><span className={bridgeState === "connected" ? "connection-dot ready" : "connection-dot"} /><div><strong>{navigation?.vaultName || "Obsidian Vault"}</strong><small>{bridgeState === "connected" ? "样板可写 · 目录自动更新" : "请使用一键启动器"}</small></div></div><nav>{NAV_ITEMS.map((item) => <button type="button" className={view === item.id ? "active" : ""} key={item.id} onClick={() => setView(item.id)}><span>{item.glyph}</span><div><strong>{item.label}</strong><small>{item.caption}</small></div></button>)}</nav><div className="sidebar-bottom"><button type="button" onClick={() => void openInObsidian("知识产权/00_知识产权研究导航.md")}><span className="api-dot ready" />原生导航</button><button type="button" onClick={() => void openInObsidian()}>打开 Obsidian ↗</button></div></aside><div className="main-shell"><header className="topbar"><div className="global-search"><span>⌕</span><input aria-label="搜索Obsidian目录" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索题名、学者、年份、领域或争议…" /><kbd>本机</kbd>{searchMatches.length > 0 && <div className="search-popover">{searchMatches.map((note) => <button type="button" key={note.path} onClick={() => { void openNote(note.path); setQuery(""); }}><strong>{note.title}</strong><small>{note.authors.join("、") || note.folder}</small></button>)}</div>}</div><div className="top-actions"><span className="auto-update-label"><i />10秒自动检查</span><button type="button" onClick={() => void loadNavigation()}>↻ 刷新</button><button className="obsidian-button" type="button" onClick={() => void openInObsidian("知识产权/00_知识产权研究导航.md")}>OB&nbsp; 原生导航</button></div></header><div className="content-shell">{bridgeState === "offline" && <div className="connection-warning"><strong>本机工作台尚未启动</strong><span>请双击“启动LexTrace.command”；原生 Obsidian 导航仍可独立使用。</span><button type="button" onClick={() => void loadNavigation()}>重新连接</button></div>}{view === "overview" && renderOverview()}{view === "intake" && renderIntake()}{view === "library" && renderLibrary()}{view === "relations" && renderRelations()}{view === "citations" && renderCitations()}{view === "agents" && renderAgents()}{view === "export" && renderExport()}</div></div>

      {(selectedNote || noteLoading) && <aside className="note-drawer"><div className="drawer-head"><span>{noteLoading ? "正在读取…" : "OBSIDIAN NOTE PREVIEW"}</span><button type="button" onClick={() => setSelectedNote(null)}>×</button></div>{selectedNote && <><div className="drawer-title"><small>{selectedNote.path}</small><h2>{selectedNote.title}</h2><div>{selectedNote.authors.map((author) => <span key={author}>{author}</span>)}{selectedNote.year && <span>{selectedNote.year}</span>}{selectedNote.journal && <span>{selectedNote.journal}</span>}</div></div><div className="drawer-actions"><button className="primary-button" type="button" onClick={() => void openInObsidian(selectedNote.path)}>在 Obsidian 阅读全文</button><button className={contextPaths.includes(selectedNote.path) ? "quiet-button selected" : "quiet-button"} type="button" onClick={() => toggleContext(selectedNote.path)}>{contextPaths.includes(selectedNote.path) ? "已加入 Agent" : "+ Agent 材料"}</button><button className="quiet-button" type="button" onClick={() => void copyText(selectedNote.path, "笔记路径已复制。")}>复制路径</button></div>{selectedNote.isPaper && (<div className="drawer-citation-box"><div className="drawer-citation-header"><span className="eyebrow">LEGAL CITATION · 《法学引注手册》</span><button type="button" className="drawer-cite-open-btn" onClick={() => void openQuickCitation(selectedNote)}>精确引注弹窗 ↗</button></div><div className="drawer-citation-body"><p className="drawer-citation-text">{buildSimpleCitation(selectedNote)}</p><div className="drawer-citation-actions"><button type="button" onClick={() => void copyText(buildSimpleCitation(selectedNote), "Word 脚注已复制到剪贴板！")}>复制 Word 脚注</button><button type="button" onClick={() => void copyText(`[^${selectedNote.recordId || "cite"}]: ${buildSimpleCitation(selectedNote)}`, "Markdown 脚注已复制到剪贴板！")}>复制 Markdown 脚注</button><button type="button" onClick={() => void copyText(`${selectedNote.authors.join("、") || "作者待核"}前引文。`, "前引文已复制！")}>复制前引文</button>{(selectedNote.pdfLink || selectedNote.sourcePdf) && (<button type="button" className="pdf-split-btn" onClick={() => void openInObsidian(selectedNote.path)}>📄 在 Obsidian 分屏阅读 PDF (PDF++) ↗</button>)}</div></div></div>)}<section className="preview-summary"><span className="eyebrow">SUMMARY</span><p>{selectedNote.summary || "这篇导航笔记没有设置摘要，请在 Obsidian 中查看完整内容。"}</p></section><div className="drawer-columns"><div><span className="eyebrow">OUTLINE</span>{selectedNote.headings.slice(1, 16).map((heading, index) => <span className="outline-item" key={`${heading.text}-${index}`} style={{ paddingLeft: `${Math.max(0, heading.level - 1) * 11}px` }}>{heading.text}</span>)}</div><div><span className="eyebrow">LINKS</span><p>{selectedNote.links.length} 个出链 · {selectedNote.backlinks.length} 个反链</p></div></div><div className="link-preview"><span className="eyebrow">OUTGOING LINKS</span>{selectedNote.links.slice(0, 18).map((link) => link.path ? <button type="button" key={`${link.target}-${link.path}`} onClick={() => void openNote(link.path!)}>→ {link.label}</button> : <span key={link.target}>· {link.label}</span>)}</div><div className="backlinks"><span className="eyebrow">BACKLINKS</span>{selectedNote.backlinks.slice(0, 16).map((note) => <button type="button" key={note.path} onClick={() => void openNote(note.path)}>← {note.title}</button>)}</div></>}</aside>}

      {quickCitationNote && (
        <div className="modal-backdrop" onClick={() => setQuickCitationNote(null)}>
          <div className="api-modal quick-citation-modal" onClick={(event) => event.stopPropagation()}>
            <div className="modal-head">
              <div>
                <span className="eyebrow">2019 LEGAL CITATION · 一键引注与定位</span>
                <h2>{quickCitationNote.title}</h2>
                <p className="quick-citation-authors">
                  {quickCitationNote.authors.join("、") || "作者待核"} · {quickCitationNote.journal || "刊物待核"} {quickCitationNote.year ? `(${quickCitationNote.year})` : ""}
                </p>
              </div>
              <button type="button" onClick={() => setQuickCitationNote(null)}>×</button>
            </div>

            <div className="quick-citation-body">
              <div className="quick-mode-tabs">
                <button
                  type="button"
                  className={quickMode === "paraphrase" ? "active" : ""}
                  onClick={() => void updateQuickCitation(quickCitationNote, "paraphrase", quickPinpoint)}
                >
                  转述 (参见)
                </button>
                <button
                  type="button"
                  className={quickMode === "direct" ? "active" : ""}
                  onClick={() => void updateQuickCitation(quickCitationNote, "direct", quickPinpoint)}
                >
                  直接引语
                </button>
                <button
                  type="button"
                  className={quickMode === "general" ? "active" : ""}
                  onClick={() => void updateQuickCitation(quickCitationNote, "general", quickPinpoint)}
                >
                  整篇文献
                </button>
                <button
                  type="button"
                  className={quickMode === "short" ? "active" : ""}
                  onClick={() => void updateQuickCitation(quickCitationNote, "short", quickPinpoint)}
                >
                  前引文 (再次引用)
                </button>
              </div>

              <div className="quick-pinpoint-row">
                <label>
                  具体引用页码 (Pinpoint Page)：
                  <input
                    type="text"
                    value={quickPinpoint}
                    placeholder={quickMode === "general" ? "整篇引用可留空" : "例如 15 或 15-18"}
                    onChange={(event: ChangeEvent<HTMLInputElement>) => {
                      const val = event.target.value;
                      setQuickPinpoint(val);
                      void updateQuickCitation(quickCitationNote, quickMode, val);
                    }}
                  />
                </label>
              </div>

              {quickError && (
                <div className="quick-citation-error">⚠️ {quickError}</div>
              )}

              {quickResult && (
                <div className="quick-citation-preview-card">
                  <span className="eyebrow">引注预览 (《法学引注手册》规范)</span>
                  <div className="quick-citation-text">{quickResult.citation}</div>
                  {quickResult.shortCitation && quickMode !== "short" && (
                    <div className="quick-citation-short-text">
                      <small>再次引用形式：</small>{quickResult.shortCitation}
                    </div>
                  )}
                </div>
              )}

              <div className="quick-citation-actions-grid">
                <button
                  type="button"
                  className="primary-button"
                  disabled={!quickResult}
                  onClick={() => void copyText(quickResult?.citation || "", "Word 脚注已复制到剪贴板！")}
                >
                  📋 复制 Word 脚注
                </button>
                <button
                  type="button"
                  className="quiet-button"
                  disabled={!quickResult}
                  onClick={() => void copyText(quickResult?.markdownFootnote || quickResult?.obsidianDefinition || "", "Markdown 脚注已复制到剪贴板！")}
                >
                  📋 复制 Markdown 脚注
                </button>
                <button
                  type="button"
                  className="quiet-button"
                  disabled={!quickResult}
                  onClick={() => void copyText(quickResult?.shortCitation || `${quickCitationNote.authors.join("、")}前引文。`, "前引文短注已复制！")}
                >
                  📋 复制前引文
                </button>
                <button
                  type="button"
                  className="quiet-button"
                  onClick={() => void openInObsidian(quickCitationNote.path)}
                >
                  📄 在 Obsidian 查看 / PDF++ ↗
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {notice && <button type="button" className="toast" onClick={() => setNotice("")}>{notice}<span>×</span></button>}
    </main>
  );
}
