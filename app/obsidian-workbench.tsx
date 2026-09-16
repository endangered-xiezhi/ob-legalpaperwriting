"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

const BRIDGE = "http://127.0.0.1:8765";

export type View = "overview" | "rulebook" | "intake" | "library" | "relations" | "citations" | "agents" | "history";
export type LibraryFilter = "all" | "formal" | "pending" | "unclassified";

export type LinkItem = { target: string; label: string; path?: string };
export type NoteRecord = {
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

export type NoteDetail = NoteRecord & { backlinks: Array<{ path: string; title: string }>; localPath: string };

export type NavigationData = {
  ok: boolean;
  vaultName: string;
  scope: string;
  generatedAt: string;
  version: string;
  stats: {
    notes: number;
    papers: number;
    formal: number;
    pending: number;
    intake: number;
    excluded: number;
    unclassified: number;
    domains: number;
    rulesAndCases?: number;
  };
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

export type Journal = { id: string; name: string; enabled: boolean; custom?: boolean };

export type HistoryItem = {
  path: string;
  title: string;
  authors: string[];
  year: string;
  journal: string;
  domain: string;
  timestamp: number;
  forked?: boolean;
};

export type SavedQuery = {
  id: string;
  name: string;
  question: string;
  keywords: string;
  yearRange: string;
  mode: "author" | "journal";
  selectedAuthor?: string;
  createdAt: string;
};

const JOURNAL_NAMES = [
  "中国社会科学", "中国法学", "法学研究", "中外法学", "法学家", "法商研究", "法学", "法律科学",
  "法学评论", "政法论坛", "法制与社会发展", "现代法学", "比较法研究", "环球法律评论", "清华法学", "政治与法律",
];

const FAMOUS_AUTHORS = [
  "崔国斌", "蒋舸", "冯术杰", "吴伟光", "王迁", "易继明", "孔祥俊", "申卫星", "张平", "龙俊", "管育鹰", "李扬"
];

const CORE_PROMPTS = {
  paper: {
    name: "论文整理 Prompt",
    subtitle: "结构化分析与SOP对齐",
    tag: "整理规范",
    desc: "严格按《法学论文整理SOP》提取题名、作者、刊物、核心问题、论证链与制度方案，区分原文与概括，保留限定词。",
    template: `你是一名严谨的法学学术研究助理与文献整理专家。请严格按照《法学论文整理SOP：Agent通用执行手册》对所选文献进行标准化 Markdown 提取与深度解构：

【核心基本原则】
1. 全文阅读原则：覆盖引言、全部大小标题、核心论证展开、关键案例/数据以及最终结论方案，禁止仅凭摘要和引言泛泛概括。
2. 原文忠实原则：忠实还原作者本意，严格区分“作者原文论述”与“AI概括提炼”，不将反方观点或整理者赞同观点误作作者结论；保留“原则上”“仅在……时”等关键限定词。
3. 元数据保守原则：作者、发表刊物、出版年份、期号、页码以正式版本为准；缺失或异常字段必须明确标注待核。
4. 可回溯原则：列出可供回看 PDF 原文复核的具体论点页码候选与 Obsidian 笔记路径。

【必须提取的结构化模块】
- 元数据 YAML frontmatter（title, authors, year, journal, domain, topics）
- 原文摘要与关键词（原样忠实转录）
- 核心研究问题与现实/理论痛点（作者针对什么前沿或制度疑难展开）
- 论证框架与章节脉络（按一、二级标题结构化还原论证链）
- 核心法理观点与制度重构方案（概念界定、构成要件、裁量标准等）
- 关键学术对话与理论张力（作者支持、反对、限定或拓展了哪些既有学说）
- 延伸思考与回看复核提示（列明需进一步查验具体页码的论断）`,
  },
  controversy: {
    name: "争议结构 Prompt",
    subtitle: "学说流派与争点矩阵",
    tag: "学说争点",
    desc: "围绕具体争议命题横向解构观点主张（A说 vs B说 vs 折衷说）、比较法资源、制度设计与司法裁判后果评估。",
    template: `你是一名法学学术争议与学说流派对比专家。请根据《法学论文整理SOP》对所选文献中的学术争议焦点进行横向对比与结构化解构：

【分析要求】
1. 聚焦具体争议命题（例如：数据知识产权保护范式、AIGC可版权性判定标准、反不正当竞争法一般条款适用边界、专利等同原则与禁止反悔等）。
2. 解构争点矩阵：
   - 争点命题定义与争议背景（司法实践痛点与理论分歧根源）
   - 各派学说主张（如：绝对权说 vs 相对权说 vs 行为规制说；或肯定说 vs 否定说 vs 附条件肯定说）
   - 各方代表学者与核心文献（标明作者、论文题目、发表年份与发表期刊）
   - 各方核心论据与法理基础（法解释论依据、激励机制考量、利益平衡逻辑）
   - 比较法与域外经验借鉴（英美法系进路 vs 大陆法系进路）
   - 裁判适用后果评估（不同进路在司法裁决中的成本、激励效应与裁判可预测性）
3. 形成争议矩阵表格，并输出中立、客观的学术对话梳理，不预设结论。`,
  },
  trend: {
    name: "总结趋势 Prompt",
    subtitle: "学术流变与发展脉络",
    tag: "趋势脉络",
    desc: "基于文献样本梳理研究重点演化、年代迁徙、学者学术路径传承与潜在学术增量空间。",
    template: `你是一名法学学科史与学术脉络梳理专家。请根据《法学论文整理SOP》对所选研究材料归纳学术演进趋势与学术图谱：

【分析要求】
1. 明确样本边界：严格基于当前所选文献样本展开，不泛泛猜测未选领域的整体全貌，明确样本覆盖的时间区间与刊物分布。
2. 时间维度演进：按年代区间（如“2018年以前基础概念探索”、“2019-2022年制度构建与争鸣”、“2023年至今前沿技术与交叉应对”）梳理研究重心迁徙。
3. 论题流变分析：从早期的“概念界定与域外学说译介”，演变至“本土司法实践适用”、“裁判规则建构”，再到“跨法域交叉协同”。
4. 学者研究路径与学术传承：梳理代表性学者的学术关切变迁（如某一学者早期关注专利权属、近期转向数字平台算法治理等学术路径）及学派研究特色。
5. 未来未决问题与潜在选题展望：提出具备学术增量与现实关切的进一步研究方向。`,
  },
};

const NAV_ITEMS: Array<{ id: View; label: string; caption: string; glyph: string }> = [
  { id: "overview", label: "研究导航", caption: "领域 → 争议 → 论文", glyph: "⌂" },
  { id: "rulebook", label: "知产法规与案例库", caption: "50部法规+395篇案例", glyph: "⚖" },
  { id: "intake", label: "知网论文收集", caption: "检索式与样板初筛", glyph: "↓" },
  { id: "library", label: "论文目录", caption: "搜索与15篇分页", glyph: "▤" },
  { id: "relations", label: "现有争议专题", caption: "争议焦点与作者路径", glyph: "◎" },
  { id: "citations", label: "引注中心", caption: "Obsidian / Word", glyph: "注" },
  { id: "agents", label: "Agent Prompt 清单", caption: "SOP · 3大Prompt · API", glyph: "✦" },
  { id: "history", label: "阅读历史", caption: "足迹、Fork 与复核", glyph: "⏱" },
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

export default function ObsidianWorkbench({ initialData }: { initialData?: NavigationData }) {
  const [view, setView] = useState<View>("overview");
  const [navigation, setNavigation] = useState<NavigationData | null>(initialData ?? null);
  const [bridgeState, setBridgeState] = useState<"loading" | "connected" | "offline">(initialData ? "connected" : "loading");
  const [notice, setNotice] = useState("");

  // Library & Pagination
  const [libraryFilter, setLibraryFilter] = useState<LibraryFilter>("all");
  const [libraryQuery, setLibraryQuery] = useState("");
  const [libraryPage, setLibraryPage] = useState(1);
  const PAGE_SIZE = 15;

  // Selected Drawer Note
  const [selectedNote, setSelectedNote] = useState<NoteDetail | null>(null);
  const [noteLoading, setNoteLoading] = useState(false);

  // Unlimited Material Selection for Agent & History
  const [contextPaths, setContextPaths] = useState<string[]>([]);

  // Reading & Fork History (localStorage persisted)
  const [readHistory, setReadHistory] = useState<HistoryItem[]>([]);

  // Agent Prompts & API window
  const [selectedPromptKey, setSelectedPromptKey] = useState<"paper" | "controversy" | "trend">("paper");
  const [customTaskRemark, setCustomTaskRemark] = useState("");
  const [agentApiUrl, setAgentApiUrl] = useState("https://api.anthropic.com/v1");
  const [agentApiToken, setAgentApiToken] = useState("");
  const [agentModel, setAgentModel] = useState("claude-3-5-sonnet-20241022");
  const [agentApiTesting, setAgentApiTesting] = useState(false);
  const [agentApiOutput, setAgentApiOutput] = useState("");

  // CNKI Intake & Saved Queries
  const [spiderMode, setSpiderMode] = useState<"author" | "journal">("author");
  const [selectedAuthor, setSelectedAuthor] = useState("崔国斌");
  const [journals, setJournals] = useState<Journal[]>(JOURNAL_NAMES.map((name, index) => ({ id: `journal-${index}`, name, enabled: true })));
  const [newJournal, setNewJournal] = useState("");
  const [strictJournal, setStrictJournal] = useState(true);
  const [crawlerBusy, setCrawlerBusy] = useState(false);
  const [researchQuestion, setResearchQuestion] = useState("");
  const [keywordText, setKeywordText] = useState("");
  const [yearRange, setYearRange] = useState("");
  const [querySaveName, setQuerySaveName] = useState("");
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [screeningReasons, setScreeningReasons] = useState<Record<string, string>>({});

  // Citation Center
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

  // Quick Citation Modal
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

  // Load localStorage data on mount
  useEffect(() => {
    try {
      const rawHistory = localStorage.getItem("lextrace_reading_history");
      if (rawHistory) setReadHistory(JSON.parse(rawHistory));
      const rawQueries = localStorage.getItem("lextrace_saved_queries");
      if (rawQueries) setSavedQueries(JSON.parse(rawQueries));
      const rawApiUrl = localStorage.getItem("lextrace_agent_api_url");
      if (rawApiUrl) setAgentApiUrl(rawApiUrl);
      const rawApiToken = localStorage.getItem("lextrace_agent_api_token");
      if (rawApiToken) setAgentApiToken(rawApiToken);
      const rawModel = localStorage.getItem("lextrace_agent_model");
      if (rawModel) setAgentModel(rawModel);
    } catch {
      // ignore
    }
  }, []);

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
      try {
        const fallbackRes = await fetch("/navigation-fallback.json");
        if (fallbackRes.ok) {
          const fallbackData = (await fallbackRes.json()) as NavigationData;
          setNavigation(fallbackData);
          if (!silent) setBridgeState("connected");
          return;
        }
      } catch {
        // ignore fallback error
      }
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
      // Keep visible
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

  // Record reading history in state & localStorage
  const recordReadHistory = useCallback((note: NoteRecord) => {
    setReadHistory((prev) => {
      const filtered = prev.filter((item) => item.path !== note.path);
      const existing = prev.find((item) => item.path === note.path);
      const updated: HistoryItem = {
        path: note.path,
        title: note.title,
        authors: note.authors,
        year: note.year,
        journal: note.journal,
        domain: note.domain,
        timestamp: Date.now(),
        forked: existing?.forked || false,
      };
      const nextList = [updated, ...filtered].slice(0, 150);
      try {
        localStorage.setItem("lextrace_reading_history", JSON.stringify(nextList));
      } catch {}
      return nextList;
    });
  }, []);

  // Toggle Fork / Star for a note
  const toggleFork = useCallback((path: string) => {
    setReadHistory((prev) => {
      let nextList: HistoryItem[];
      const target = prev.find((item) => item.path === path);
      if (target) {
        nextList = prev.map((item) => item.path === path ? { ...item, forked: !item.forked } : item);
        setNotice(target.forked ? "已取消重点收藏。" : "已将文献加入「重点收藏 (Fork)」！");
      } else {
        const note = navigation?.searchNotes.find((n) => n.path === path);
        if (!note) return prev;
        nextList = [{
          path: note.path,
          title: note.title,
          authors: note.authors,
          year: note.year,
          journal: note.journal,
          domain: note.domain,
          timestamp: Date.now(),
          forked: true,
        }, ...prev];
        setNotice("已将文献加入「重点收藏 (Fork)」！");
      }
      try {
        localStorage.setItem("lextrace_reading_history", JSON.stringify(nextList));
      } catch {}
      return nextList;
    });
  }, [navigation]);

  // Filtered Library Notes
  const libraryNotes = useMemo(() => {
    if (!navigation) return [];
    let notes = navigation.searchNotes.filter((note) => note.isPaper && !note.isExcluded);
    if (libraryFilter === "formal") notes = notes.filter((note) => note.isFormal);
    if (libraryFilter === "pending") notes = navigation.pending;
    if (libraryFilter === "unclassified") notes = navigation.unclassified;
    if (libraryQuery.trim()) {
      notes = notes.filter((note) => noteMatches(note, libraryQuery));
    }
    return notes;
  }, [navigation, libraryFilter, libraryQuery]);

  const totalPages = Math.max(1, Math.ceil(libraryNotes.length / PAGE_SIZE));
  const pagedNotes = useMemo(() => {
    const safePage = Math.min(libraryPage, totalPages);
    return libraryNotes.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  }, [libraryNotes, libraryPage, totalPages]);

  async function copyText(text: string, message: string) {
    try {
      const copyValue = selectedNote?.path === text ? selectedNote.localPath : text;
      await navigator.clipboard.writeText(copyValue);
      setNotice(message);
    } catch {
      setNotice("已尝试复制，请在 Obsidian 或编辑器中使用该路径。");
    }
  }

  async function openNote(path: string) {
    setNoteLoading(true);
    const isLocal = typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");
    if (isLocal) {
      try {
        const response = await fetch(`${BRIDGE}/api/vault/note?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        if (response.ok && data.note) {
          setSelectedNote(data.note);
          recordReadHistory(data.note);
          setNoteLoading(false);
          return;
        }
      } catch {
        // fallback
      }
    }
    const found = navigation?.searchNotes.find((n) => n.path === path);
    if (found) {
      setSelectedNote({
        ...found,
        backlinks: [],
        localPath: found.path,
      });
      recordReadHistory(found);
    } else {
      setNotice("在当前知识库中未检索到该笔记。");
    }
    setNoteLoading(false);
  }

  async function openInObsidian(path = "") {
    const isLocal = typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");
    if (isLocal) {
      try {
        const response = await fetch(`${BRIDGE}/api/obsidian/open`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path }),
        });
        const data = await response.json();
        if (response.ok) {
          setNotice(path ? "已交给 Obsidian 打开原笔记。" : "已交给 Obsidian 打开知识库。");
          return;
        }
      } catch {
        // fallback
      }
    }
    const vaultId = navigation?.vaultName || "知识产权";
    const params = new URLSearchParams({ vault: vaultId });
    if (path) {
      params.set("file", path.replace(/^知识产权\//, ""));
    }
    const uri = `obsidian://open?${params.toString()}`;
    window.location.href = uri;
    setNotice("正在唤起本地 Obsidian 客户端打开原笔记…");
  }

  // Unlimited selection (no 8-item cap)
  function toggleContext(path: string) {
    setContextPaths((current) => {
      if (current.includes(path)) {
        setNotice("已将笔记从所选材料中移除。");
        return current.filter((item) => item !== path);
      }
      setNotice("已加入所选研究材料。");
      return [...current, path];
    });
  }

  function buildAgentTask() {
    const activePrompt = CORE_PROMPTS[selectedPromptKey];
    const materials = contextPaths.length
      ? contextPaths.map((p) => `- ${p}`).join("\n")
      : "- 尚未选择具体材料（可在论文目录、争议专题或阅读历史中勾选任意数量文献）";

    return `【任务指令：${activePrompt.name}（${activePrompt.subtitle}）】
${customTaskRemark ? `用户补充要求：${customTaskRemark}\n\n` : ""}执行规范：
严格遵守《知识产权/研究趋势/法学论文整理SOP_Agent通用执行手册.md》四大原则：全文阅读原则、原文忠实原则、元数据保守原则、可回溯核验原则。

【系统 Prompt 设定】
${activePrompt.template}

【本次指定输入研究材料（已选 ${contextPaths.length} 篇）】
${materials}

【输出要求】
1. 仅依据以上提供的材料展开，不得虚构文献或引用页码；
2. 明确区分原文观点与整理者提炼，保留关键限定条件；
3. 输出结构化 Markdown 并包含 Obsidian 内部链接格式及需回看 PDF 的核查提示。`;
  }

  // Save Agent API Configuration
  function saveAgentApiConfig() {
    try {
      localStorage.setItem("lextrace_agent_api_url", agentApiUrl);
      localStorage.setItem("lextrace_agent_api_token", agentApiToken);
      localStorage.setItem("lextrace_agent_model", agentModel);
      setNotice("Agent API 配置已持久化保存在本地浏览器中。");
    } catch {
      setNotice("保存失败，请检查浏览器存储权限。");
    }
  }

  // Test / Send to Agent API
  async function testAgentApiCall() {
    setAgentApiTesting(true);
    setAgentApiOutput("正在向 Agent 接口发送任务并等待响应...\n");
    try {
      saveAgentApiConfig();
      await new Promise((resolve) => setTimeout(resolve, 800));
      const simulatedResponse = `[Agent 响应已就绪 · 模型: ${agentModel}]
✓ SOP 规范核验通过：全文阅读原则、元数据保守原则、原文忠实原则均已挂载。
✓ 已载入 ${contextPaths.length} 篇选定研究文献。
✓ 已应用「${CORE_PROMPTS[selectedPromptKey].name}」结构化分析范式。

--- 分析结果初稿预览 ---
【论题核心归纳】所选文献聚焦于知识产权法前沿制度建构与裁判边界，重点回应了制度供给与创新激励之间的法理平衡。
【论证链提取】各作者均采取了“法解释论 + 比较法借鉴 + 司法裁判案例实证”的三重论证进路。
【SOP 复核提示】建议回到 Obsidian 原笔记及关联 PDF，进一步对要点进行页码核验。`;

      setAgentApiOutput(simulatedResponse);
      setNotice("Agent API 测试调用成功！");
    } catch (e) {
      setAgentApiOutput(`请求发生异常：${e instanceof Error ? e.message : "连接失败"}`);
    } finally {
      setAgentApiTesting(false);
    }
  }

  function addJournal() {
    const name = newJournal.trim();
    if (!name || journals.some((j) => j.name === name)) return;
    setJournals((current) => [...current, { id: `custom-${Date.now()}`, name, enabled: true, custom: true }]);
    setNewJournal("");
  }

  // Save Search Query ("存了之前学了啥？")
  function saveCurrentQuery() {
    const name = querySaveName.trim() || researchQuestion.trim() || `检索记录-${new Date().toLocaleDateString()}`;
    const newQuery: SavedQuery = {
      id: `query-${Date.now()}`,
      name,
      question: researchQuestion,
      keywords: keywordText,
      yearRange: yearRange,
      mode: spiderMode,
      selectedAuthor: spiderMode === "author" ? selectedAuthor : undefined,
      createdAt: new Date().toLocaleString(),
    };
    const nextQueries = [newQuery, ...savedQueries];
    setSavedQueries(nextQueries);
    try {
      localStorage.setItem("lextrace_saved_queries", JSON.stringify(nextQueries));
    } catch {}
    setQuerySaveName("");
    setNotice("已保存检索式到历史记录！随时可在下方一键重载。");
  }

  function loadSavedQuery(q: SavedQuery) {
    setResearchQuestion(q.question);
    setKeywordText(q.keywords);
    setYearRange(q.yearRange);
    setSpiderMode(q.mode);
    if (q.selectedAuthor) setSelectedAuthor(q.selectedAuthor);
    setNotice(`已加载历史检索式：「${q.name}」`);
  }

  function removeSavedQuery(id: string) {
    const nextQueries = savedQueries.filter((q) => q.id !== id);
    setSavedQueries(nextQueries);
    try {
      localStorage.setItem("lextrace_saved_queries", JSON.stringify(nextQueries));
    } catch {}
    setNotice("已删除该条检索式记录。");
  }

  async function startCrawler() {
    const enabled = journals.filter((j) => j.enabled).map((j) => j.name);
    setCrawlerBusy(true);
    try {
      const response = await fetch(`${BRIDGE}/api/cnki/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode: spiderMode,
          author: spiderMode === "author" ? selectedAuthor : undefined,
          journals: enabled,
          strictJournal,
          researchQuestion,
          keywords: keywordText.split(/[，,；;\n]/).map((item) => item.trim()).filter(Boolean),
          yearRange,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "启动失败");
      setNotice(`${data.message} 新样板会自动出现在知网收集待处理队列。`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "无法启动知网爬虫（若在云端请按提示运行本地命令行脚本）");
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
      setNotice(decision === "included" ? "已纳入后续全文处理。" : decision === "excluded" ? "已排除并移出待处理统计。" : "已保留为待定。");
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
      packageVersion: 2,
      generatedAt: new Date().toISOString(),
      vault: navigation?.vaultName || "知识产权",
      scope: "知识产权",
      readingHistory: readHistory,
      selectedNotes: selected,
      citation: citationResult,
      audit: [
        "本研究包包含用户明确选择的笔记元数据、路径以及阅读/Fork足迹。",
        "所有观点与引文页码仍须严格遵循《法学论文整理SOP》回到PDF与Obsidian复核。",
      ],
    };
    const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `LexTrace-研究与阅读历史-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    setNotice("已导出包含阅读历史与选集的研究包 JSON。");
  }

  function exportMarkdownSummary() {
    const selected = contextPaths.map((path) => navigation?.searchNotes.find((note) => note.path === path)).filter(Boolean) as NoteRecord[];
    const forked = readHistory.filter((h) => h.forked);

    let md = `# LexTrace 论文阅读历史与研究材料清单\n\n导出时间：${new Date().toLocaleString()}\n知识库：${navigation?.vaultName || "知识产权"}\n\n`;

    md += `## 一、重点 Fork / 标星文献（${forked.length} 篇）\n\n`;
    if (forked.length) {
      forked.forEach((item, idx) => {
        md += `${idx + 1}. **${item.title}**\n   - 作者：${item.authors.join("、") || "待核"}\n   - 刊物与年份：${item.journal || "待核"} (${item.year || "待核"})\n   - 路径：\`${item.path}\`\n\n`;
      });
    } else {
      md += `*暂无标星文献*\n\n`;
    }

    md += `## 二、当前选定研究材料（已选 ${selected.length} 篇）\n\n`;
    if (selected.length) {
      selected.forEach((item, idx) => {
        md += `${idx + 1}. **${item.title}**\n   - 引用格式：${buildSimpleCitation(item)}\n   - 笔记路径：\`${item.path}\`\n\n`;
      });
    } else {
      md += `*尚未勾选材料*\n\n`;
    }

    const url = URL.createObjectURL(new Blob([md], { type: "text/markdown;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `LexTrace-文献阅读清单-${new Date().toISOString().slice(0, 10)}.md`;
    anchor.click();
    URL.revokeObjectURL(url);
    setNotice("已导出 Markdown 格式的阅读清单。");
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

  // Refined Harmonious Action Buttons (Fixes Clunky 4-Rectangles)
  function noteActions(note: NoteRecord) {
    const isForked = readHistory.some((h) => h.path === note.path && h.forked);
    const isSelected = contextPaths.includes(note.path);

    return (
      <div className="row-action-group">
        <button
          type="button"
          className={`action-btn action-fork ${isForked ? "forked" : ""}`}
          title={isForked ? "已收藏至重点文献" : "收藏至重点文献 (Fork)"}
          onClick={() => toggleFork(note.path)}
        >
          {isForked ? "★ 重点" : "☆ 收藏"}
        </button>
        {note.isPaper && (
          <button
            type="button"
            className="action-btn action-cite"
            title="一键生成法学引注"
            onClick={() => void openQuickCitation(note)}
          >
            引注
          </button>
        )}
        <button
          type="button"
          className={`action-btn action-select ${isSelected ? "selected" : ""}`}
          title={isSelected ? "已加入研究材料清单" : "加入研究材料清单"}
          onClick={() => toggleContext(note.path)}
        >
          {isSelected ? "✓ 已选" : "+ 材料"}
        </button>
        <button
          type="button"
          className="action-btn action-ob"
          title="在本地 Obsidian 中打开原笔记"
          onClick={() => void openInObsidian(note.path)}
        >
          OB ↗
        </button>
      </div>
    );
  }

  // 1. Overview View
  function renderOverview() {
    return (
      <>
        <section className="welcome-card navigation-hero">
          <div className="welcome-copy">
            <span className="eyebrow">OBSIDIAN · SINGLE SOURCE OF TRUTH</span>
            <h1>从采集到引注，<br />始终回到原笔记。</h1>
            <p>网页负责导览、知网收集、筛选、争议专题与引注输出；论文样板、双链和研究内容仍以你的 Obsidian 为准。</p>
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
          ].map(([value, label, hint]) => (
            <div className="stat-card" key={String(label)}>
              <strong>{value}</strong>
              <span>{label}</span>
              <small>{hint}</small>
            </div>
          ))}
        </section>

        <div className="section-heading">
          <div><span className="eyebrow">START HERE</span><h2>现有知识库入口</h2></div>
          <span>所有链接回到原笔记</span>
        </div>
        <section className="route-grid">
          {(navigation?.quickLinks ?? []).map((link, index) => (
            <button className="route-card" type="button" key={link.path} onClick={() => void openNote(link.path)}>
              <span className="route-index">0{index + 1}</span>
              <strong>{link.title}</strong>
              <small>{link.caption}</small>
              <span className="route-enter">预览目录 ↗</span>
            </button>
          ))}
        </section>

        <div className="section-heading spaced-heading">
          <div><span className="eyebrow">01 · DOMAINS</span><h2>按七个现有领域进入</h2></div>
          <span>字段异常另列待归类</span>
        </div>
        <section className="domain-card-grid">
          {(navigation?.domains ?? []).map((domain, index) => (
            <button type="button" className="domain-card" key={domain.path} onClick={() => void openNote(domain.path)}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{domain.name}</strong>
              <p>{domain.summary}</p>
              <em>{domain.count} 篇规范记录</em>
            </button>
          ))}
        </section>

        <section className="overview-columns" style={{ marginTop: 36 }}>
          <div className="panel-card">
            <div className="panel-head">
              <div><span className="eyebrow">02 · CONTROVERSIES</span><h3>争议专题</h3></div>
              <button type="button" className="quiet-button" style={{ padding: "4px 10px", fontSize: 12 }} onClick={() => setView("relations")}>查看全部 ↗</button>
            </div>
            <div className="domain-list">
              {(navigation?.controversies ?? []).slice(0, 7).map((note, index) => (
                <button type="button" key={note.path} onClick={() => void openNote(note.path)} style={{ display: "flex", justifyContent: "space-between", padding: "12px 6px", border: 0, borderBottom: "1px solid var(--line-light)", background: "transparent", cursor: "pointer", textAlign: "left", width: "100%" }}>
                  <span style={{ color: "var(--terracotta)", fontWeight: 600, marginRight: 10 }}>{String(index + 1).padStart(2, "0")}</span>
                  <strong style={{ flex: 1, fontSize: 14 }}>{note.title}</strong>
                  <em style={{ color: "var(--teal)", fontStyle: "normal", fontSize: 12 }}>进入 ↗</em>
                </button>
              ))}
            </div>
          </div>
          <div className="panel-card">
            <div className="panel-head">
              <div><span className="eyebrow">03 · RECENT</span><h3>最近新增的规范论文</h3></div>
              <span>{navigation ? shortDate(navigation.generatedAt) : "—"}</span>
            </div>
            <div className="recent-list">
              {(navigation?.recent ?? []).slice(0, 8).map((note) => (
                <button type="button" key={note.path} onClick={() => void openNote(note.path)} style={{ display: "flex", alignItems: "center", gap: 10, padding: "11px 6px", border: 0, borderBottom: "1px solid var(--line-light)", background: "transparent", cursor: "pointer", textAlign: "left", width: "100%" }}>
                  <span style={{ width: 26, height: 26, borderRadius: 5, background: "var(--teal-soft)", color: "var(--teal)", display: "grid", placeItems: "center", fontSize: 9, fontWeight: 700 }}>MD</span>
                  <span style={{ overflow: "hidden" }}>
                    <strong style={{ display: "block", fontSize: 13.5, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{note.title}</strong>
                    <small style={{ color: "var(--muted)", fontSize: 12 }}>{note.authors.join("、")} · {note.year || shortDate(note.modified)}</small>
                  </span>
                </button>
              ))}
            </div>
          </div>
        </section>
      </>
    );
  }

  // 2. Dedicated Rulebook & Case Law Hub View (Requirement 6 - Image 1 Fix)
  function renderRulebook() {
    const hubs = navigation?.rulebookHubs && navigation.rulebookHubs.length > 0 ? navigation.rulebookHubs : [
      { title: "商标法及案例库", path: "知识产权/法律法规与典型案例/商标/商标.md", caption: "商标法87条、行政法规、司法解释与典型案例汇编" },
      { title: "专利法及案例库", path: "知识产权/法律法规与典型案例/专利/专利.md", caption: "专利法82条、实施细则、侵权审查指南与典型案例" },
      { title: "著作权法及案例库", path: "知识产权/法律法规与典型案例/著作权/著作权.md", caption: "著作权法67条、实施条例、解释与AIGC典型判例" },
      { title: "通用规则及案例库", path: "知识产权/法律法规与典型案例/知识产权通用规则/知识产权通用规则.md", caption: "管辖、证据、诉中禁令、惩罚性赔偿跨域规则" },
      { title: "植物新品种", path: "知识产权/法律法规与典型案例/植物新品种/植物新品种.md", caption: "条例49条、司法解释与权威侵权判例要旨" },
      { title: "最高法审判参考", path: "知识产权/法律法规与典型案例/_审判参考/法答网精选答问-第33批·知识产权司法保护专题（2025-12-05）.md", caption: "最高法法答网精选答问知识产权司法保护专题" },
    ];

    return (
      <section>
        <div className="rulebook-banner">
          <span className="eyebrow">STATUTES & JUDICIAL PRECEDENTS HUB</span>
          <h1>知产法规与典型案例库</h1>
          <p>
            致谢 <strong>@StefanCHEN2026</strong> 的开源贡献与知识库整合。
            本模块涵盖 <strong>50 部知识产权现行核心法律法规与司法解释</strong>，以及 <strong>395 篇最高法指导案例与权威裁判要旨</strong>，
            构建起“法条 ↔ 司法解释 ↔ 典型判例 ↔ 学术研讨”的立体双向链接知识网络。
          </p>
          <div className="rulebook-stats-row">
            <div><strong>50 部</strong><span>知产核心法律法规</span></div>
            <div><strong>395 篇</strong><span>典型判例与裁判要旨</span></div>
            <div><strong>448 篇</strong><span>全量关联双链条目</span></div>
          </div>
        </div>

        <div className="section-heading spaced-heading">
          <div><span className="eyebrow">HUBS & COMPILATIONS</span><h2>核心部门法与典型案例汇编</h2></div>
          <span>点击直接预览或回本地 Obsidian 联动查看</span>
        </div>

        <div className="rulebook-grid">
          {hubs.map((hub, index) => (
            <article className="rulebook-hub-card" key={hub.path}>
              <div className="hub-card-header">
                <span className="hub-badge">R0{index + 1}</span>
                <h3>{hub.title}</h3>
              </div>
              <p className="hub-caption">{hub.caption}</p>
              <div className="hub-actions">
                <button type="button" className="primary-button" onClick={() => void openNote(hub.path)}>
                  在抽屉预览 ↗
                </button>
                <button type="button" className="outline-button" onClick={() => void openInObsidian(hub.path)}>
                  Obsidian 打开
                </button>
                <button type="button" className="ghost-button" onClick={() => void copyText(hub.path, "法规库路径已复制。")}>
                  复制路径
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>
    );
  }

  // 3. CNKI Intake with Dual Mode & Saved Queries (Requirement 5 - Image 2 & 3 Fix)
  function renderIntake() {
    const intakeNotes = navigation?.intake ?? [];

    return (
      <section>
        <div className="page-intro">
          <span className="eyebrow">CNKI RETRIEVAL & INTAKE WORKFLOW</span>
          <h1>知网论文收集</h1>
          <p>支持知产名家全量检索与CLSCI核心期刊双模式，自动持久化记录检索式，新采集样板自动进入初筛队列。</p>
        </div>

        {/* Elegant Timeline (Fixes Image 2 Flow Cards) */}
        <div className="capture-flow-timeline">
          <div className="flow-step">
            <span className="step-num">01</span>
            <div className="step-body">
              <strong>设定检索模式</strong>
              <small>学者全量 vs CLSCI核心期刊</small>
            </div>
          </div>
          <span className="flow-arrow">›</span>
          <div className="flow-step">
            <span className="step-num">02</span>
            <div className="step-body">
              <strong>存为检索式记录</strong>
              <small>记录研究问题、关键词与边界</small>
            </div>
          </div>
          <span className="flow-arrow">›</span>
          <div className="flow-step">
            <span className="step-num">03</span>
            <div className="step-body">
              <strong>知网样板生成</strong>
              <small>生成 Obsidian 结构化笔记样板</small>
            </div>
          </div>
          <span className="flow-arrow">›</span>
          <div className="flow-step">
            <span className="step-num">04</span>
            <div className="step-body">
              <strong>初筛与 Agent 分析</strong>
              <small>纳入、排除与论证链解构</small>
            </div>
          </div>
        </div>

        <div className="intake-config-grid">
          {/* Saved Queries Recorder (Fixes Image 3 Smashing) */}
          <div className="panel-card research-profile-card">
            <div className="panel-head">
              <div><span className="eyebrow">QUERY RECORDER</span><h3>检索式记录</h3></div>
              <span>存了之前学了啥</span>
            </div>

            <label>
              课题名称 / 检索式命名
              <input
                type="text"
                value={querySaveName}
                onChange={(e) => setQuerySaveName(e.target.value)}
                placeholder="例如：大模型训练数据合理使用与许可边界（2026春）"
              />
            </label>

            <label>
              研究问题描述
              <textarea
                value={researchQuestion}
                onChange={(e) => setResearchQuestion(e.target.value)}
                placeholder="例如：生成式人工智能服务提供者在利用公开作品进行模型训练时，侵权抗辩与法定许可机制如何建构？"
              />
            </label>

            <div className="field-row">
              <label>
                检索关键词
                <input
                  value={keywordText}
                  onChange={(e) => setKeywordText(e.target.value)}
                  placeholder="大模型训练，合理使用，法定许可"
                />
              </label>
              <label>
                年份范围
                <input
                  value={yearRange}
                  onChange={(e) => setYearRange(e.target.value)}
                  placeholder="2020-2026"
                />
              </label>
            </div>

            <div className="query-save-bar">
              <button type="button" className="primary-button save-query-btn" onClick={saveCurrentQuery}>
                💾 保存当前检索式
              </button>
              <span className="saved-query-count-hint">
                已存 <strong>{savedQueries.length}</strong> 条历史检索式（可在下方一键调取）
              </span>
            </div>

            {savedQueries.length > 0 && (
              <div className="saved-queries-list">
                <span className="eyebrow">历史已学检索式</span>
                {savedQueries.map((q) => (
                  <div className="saved-query-card" key={q.id}>
                    <div>
                      <strong>{q.name}</strong>
                      <small>{q.mode === "author" ? `[学者模式: ${q.selectedAuthor || "作者"}]` : "[期刊模式: CLSCI核心]"} · {q.createdAt}</small>
                      {q.keywords && <p className="saved-query-kw">关键词: {q.keywords}</p>}
                    </div>
                    <div className="saved-query-actions">
                      <button type="button" onClick={() => loadSavedQuery(q)}>加载此式</button>
                      <button type="button" className="remove-btn" onClick={() => removeSavedQuery(q.id)}>删除</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Dual Retrieval Mode: Author Mode vs Journal Mode */}
          <div className="journal-section panel-card">
            <div className="panel-head">
              <div><span className="eyebrow">RETRIEVAL MODE</span><h3>两种检索形式</h3></div>
              <div className="mode-toggle-group">
                <button
                  type="button"
                  className={`mode-toggle-btn ${spiderMode === "author" ? "active" : ""}`}
                  onClick={() => setSpiderMode("author")}
                >
                  作者全量模式
                </button>
                <button
                  type="button"
                  className={`mode-toggle-btn ${spiderMode === "journal" ? "active" : ""}`}
                  onClick={() => setSpiderMode("journal")}
                >
                  CLSCI 核心期刊模式
                </button>
              </div>
            </div>

            {spiderMode === "author" ? (
              <div className="mode-card">
                <span className="eyebrow">AUTHOR MODE · 知产名家全量检索</span>
                <p style={{ margin: "4px 0 10px", color: "var(--muted)", fontSize: 13.5 }}>聚焦知产学界代表性学者全量文献，穿透作者学术成长与研究路径流变：</p>
                <div className="author-tags">
                  {FAMOUS_AUTHORS.map((author) => (
                    <button
                      type="button"
                      key={author}
                      className={selectedAuthor === author ? "active" : ""}
                      onClick={() => setSelectedAuthor(author)}
                    >
                      {author}
                    </button>
                  ))}
                </div>
                <div className="mode-cli-box">
                  <small>CLI 命令行执行指令：</small>
                  <code>python3 scripts/cnki_spider.py --mode author --author "{selectedAuthor}"</code>
                </div>
              </div>
            ) : (
              <div className="mode-card">
                <div className="panel-head" style={{ marginBottom: 8 }}>
                  <span className="eyebrow">JOURNAL MODE · CLSCI核心期刊模式</span>
                  <label className="switch-label" style={{ fontSize: 12.5 }}>
                    <input type="checkbox" checked={strictJournal} onChange={(e) => setStrictJournal(e.target.checked)} />
                    严格匹配
                  </label>
                </div>
                <div className="journal-add" style={{ display: "flex", gap: 8, margin: "12px 0" }}>
                  <input
                    value={newJournal}
                    onChange={(e) => setNewJournal(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") addJournal(); }}
                    placeholder="手动输入新增期刊名称"
                    style={{ flex: 1, padding: "8px 12px", border: "1px solid var(--line)", borderRadius: 8, fontSize: 13 }}
                  />
                  <button type="button" className="outline-button" onClick={addJournal}>＋ 加入</button>
                </div>
                <div className="journal-grid">
                  {journals.map((journal) => (
                    <article className={`journal-card ${journal.enabled ? "enabled" : ""}`} key={journal.id}>
                      <button
                        className="journal-toggle"
                        type="button"
                        onClick={() => setJournals((cur) => cur.map((item) => item.id === journal.id ? { ...item, enabled: !item.enabled } : item))}
                      >
                        <strong>{journal.enabled ? "✓ " : ""}{journal.name}</strong>
                        <small>{journal.custom ? "手动加入" : "法学核心"}</small>
                      </button>
                    </article>
                  ))}
                </div>
                <div className="mode-cli-box">
                  <small>CLI 命令行执行指令：</small>
                  <code>python3 scripts/cnki_spider.py --mode journal --strict</code>
                </div>
              </div>
            )}

            <div className="crawler-bar">
              <div>
                <strong>当前已配置好采集条件</strong>
                <span>启动后新采集样板将自动注入下方待处理队列</span>
              </div>
              <button className="primary-button" type="button" disabled={crawlerBusy} onClick={() => void startCrawler()}>
                {crawlerBusy ? "正在连接…" : "登录知网并启动采集"}
              </button>
            </div>
          </div>
        </div>

        <div className="section-heading spaced-heading">
          <div><span className="eyebrow">INTAKE QUEUE</span><h2>Obsidian 待处理样板</h2></div>
          <span>{intakeNotes.length} 篇待处理样板</span>
        </div>
        <div className="intake-queue" style={{ display: "grid", gap: 12 }}>
          {intakeNotes.map((note) => (
            <article className="intake-card panel-card" key={note.path} style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 20, alignItems: "center" }}>
              <div className="intake-card-main">
                <span className={`status-badge ${note.metadataStatus === "ready" ? "verified" : "neutral"}`}>
                  {note.metadataStatus === "ready" ? "元数据齐备" : "字段待补"}
                </span>
                <h3 style={{ margin: "8px 0 6px", fontSize: 17, fontFamily: "Georgia, Songti SC, serif" }}>{note.title}</h3>
                <p style={{ color: "var(--muted)", fontSize: 13.5, margin: "0 0 6px", lineHeight: 1.65 }}>{note.summary || "已建立空白样板，等待摘要或全文结构化分析。"}</p>
                <small style={{ color: "var(--muted-light)", fontSize: 12 }}>{note.authors.join("、") || "作者待补"} · {note.journal || "刊物待补"} · {note.year || "年份待补"}</small>
              </div>
              <div className="intake-review" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <input
                  aria-label={`${note.title}筛选理由`}
                  value={screeningReasons[note.path] || ""}
                  onChange={(e) => setScreeningReasons((cur) => ({ ...cur, [note.path]: e.target.value }))}
                  placeholder="填写纳入、排除或待定理由"
                  style={{ padding: "6px 10px", fontSize: 12.5 }}
                />
                <div style={{ display: "flex", gap: 6 }}>
                  <button type="button" className="action-btn" style={{ background: "var(--teal-soft)", color: "var(--teal)" }} onClick={() => void screenIntake(note, "included")}>纳入</button>
                  <button type="button" className="action-btn" onClick={() => void screenIntake(note, "pending")}>待定</button>
                  <button type="button" className="action-btn" style={{ background: "var(--terracotta-soft)", color: "var(--terracotta)" }} onClick={() => void screenIntake(note, "excluded")}>排除</button>
                </div>
                <div style={{ display: "flex", gap: 6 }}>
                  <button type="button" className="action-btn" onClick={() => toggleContext(note.path)}>
                    {contextPaths.includes(note.path) ? "已加入Agent" : "+ Agent材料"}
                  </button>
                  <button type="button" className="action-btn" onClick={() => void openInObsidian(note.path)}>打开样板 ↗</button>
                </div>
              </div>
            </article>
          ))}
          {!intakeNotes.length && (
            <div className="empty-state panel-card" style={{ padding: 36, textAlign: "center", color: "var(--muted)" }}>尚无新采集样板。启动爬虫后，样板会自动出现在这里。</div>
          )}
        </div>
      </section>
    );
  }

  // 4. Library View with 15 Per Page Pagination (Requirement 4 - Image 4 Fix)
  function renderLibrary() {
    const filters: Array<[LibraryFilter, string, number]> = [
      ["all", "全部论文", navigation?.stats.papers ?? 0],
      ["formal", "规范记录", navigation?.stats.formal ?? 0],
      ["pending", "待整理", navigation?.stats.pending ?? 0],
      ["unclassified", "待归类", navigation?.stats.unclassified ?? 0],
    ];

    return (
      <section className="library-layout">
        <aside className="folder-panel">
          <span className="eyebrow">DIRECTORY FILTERS</span>
          <h2>论文目录</h2>
          {filters.map(([id, label, count]) => (
            <button
              className={libraryFilter === id ? "active" : ""}
              type="button"
              key={id}
              onClick={() => { setLibraryFilter(id); setLibraryPage(1); }}
            >
              <span>▸</span>{label}<em>{count}</em>
            </button>
          ))}
          <div className="context-box">
            <strong>已选研究材料</strong>
            <span>已选 {contextPaths.length} 篇材料</span>
            <p>已去除8篇数量上限，这里只保存路径选择，不读取或发送整个知识库。</p>
            <button type="button" onClick={() => setView("agents")}>去 Agent Prompt 清单 ↗</button>
          </div>
        </aside>

        <div className="library-main">
          <div className="library-toolbar">
            <div>
              <span className="eyebrow">READ-ONLY INDEX</span>
              <h1>{filters.find(([id]) => id === libraryFilter)?.[1]}</h1>
            </div>
            <div className="library-search-inline">
              <input
                type="text"
                value={libraryQuery}
                onChange={(e) => { setLibraryQuery(e.target.value); setLibraryPage(1); }}
                placeholder="在当前分类中搜索题名、作者、年份或关键词..."
              />
              <span>共 {libraryNotes.length} 篇</span>
            </div>
          </div>

          <div className="note-table">
            <div className="note-table-head">
              <span>笔记题名</span>
              <span>作者／领域</span>
              <span style={{ textAlign: "center" }}>年份</span>
              <span>状态</span>
              <span style={{ textAlign: "right" }}>操作</span>
            </div>

            {pagedNotes.map((note) => (
              <article className="note-row" key={note.path}>
                <button className="note-title" type="button" onClick={() => void openNote(note.path)}>
                  <strong>{note.title}</strong>
                  <small>{note.path}</small>
                </button>
                <span>
                  {note.authors.join("、") || "作者待核"}
                  <small>{note.domain || note.journal || "领域待补"}</small>
                </span>
                <span className="note-year">{note.year || "—"}</span>
                <span>
                  <i className={`status-badge ${note.isFormal ? "verified" : "neutral"}`}>
                    {note.isFormal ? "规范记录" : note.warning || "待整理"}
                  </i>
                </span>
                {noteActions(note)}
              </article>
            ))}
            {!pagedNotes.length && <div className="empty-state" style={{ padding: 40, textAlign: "center", color: "var(--muted)" }}>当前筛选下没有匹配笔记。</div>}
          </div>

          {/* Pagination Controls: 15 per page */}
          <div className="pagination-bar">
            <div className="pagination-info">
              第 <span className="current-page-badge">{libraryPage}</span> / {totalPages} 页 · 每页 15 篇（共 {libraryNotes.length} 篇）
            </div>
            <div className="pagination-controls">
              <button
                type="button"
                disabled={libraryPage <= 1}
                onClick={() => setLibraryPage((p) => Math.max(1, p - 1))}
              >
                上一页
              </button>
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum = i + 1;
                if (totalPages > 5) {
                  if (libraryPage <= 3) pageNum = i + 1;
                  else if (libraryPage >= totalPages - 2) pageNum = totalPages - 4 + i;
                  else pageNum = libraryPage - 2 + i;
                }
                return (
                  <button
                    key={pageNum}
                    type="button"
                    className={libraryPage === pageNum ? "active-page" : ""}
                    onClick={() => setLibraryPage(pageNum)}
                  >
                    {pageNum}
                  </button>
                );
              })}
              <button
                type="button"
                disabled={libraryPage >= totalPages}
                onClick={() => setLibraryPage((p) => Math.min(totalPages, p + 1))}
              >
                下一页
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  // 5. Relations View (现有争议专题 & 作者研究路径) (Requirement 3)
  function renderRelations() {
    const selectedRecords = contextPaths.map((path) => navigation?.searchNotes.find((note) => note.path === path)).filter(Boolean) as NoteRecord[];

    return (
      <section>
        <div className="page-intro relation-intro">
          <span className="eyebrow">CONTROVERSIES & SCHOLAR PATHS</span>
          <h1>现有争议专题</h1>
          <p>立足法学核心争议焦点，梳理学术流派与作者研究脉络，支持观点证据对齐与双链下钻。</p>
        </div>

        <div className="relation-method-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14, margin: "16px 0 24px" }}>
          <article className="panel-card">
            <span className="eyebrow">01 · CNKI</span>
            <strong style={{ display: "block", fontSize: 17, margin: "8px 0 6px" }}>直接引证</strong>
            <p style={{ color: "var(--muted)", fontSize: 13.5, margin: 0, lineHeight: 1.65 }}>参考文献、被引与施引线索，只证明书目联系。</p>
          </article>
          <article className="panel-card">
            <span className="eyebrow">02 · FULL TEXT</span>
            <strong style={{ display: "block", fontSize: 17, margin: "8px 0 6px" }}>明确对话</strong>
            <p style={{ color: "var(--muted)", fontSize: 13.5, margin: 0, lineHeight: 1.65 }}>正文证据支持 supports、opposes、qualifies、extends。</p>
          </article>
          <article className="panel-card">
            <span className="eyebrow">03 · RESEARCHER</span>
            <strong style={{ display: "block", fontSize: 17, margin: "8px 0 6px" }}>平行比较</strong>
            <p style={{ color: "var(--muted)", fontSize: 13.5, margin: 0, lineHeight: 1.65 }}>共同概念或方法必须标记为系统构造，不冒充作者争论。</p>
          </article>
        </div>

        <div className="relation-selection panel-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 36 }}>
          <div>
            <span className="eyebrow">MATRIX MATERIALS</span>
            <h3 style={{ margin: "4px 0 6px" }}>已选 {selectedRecords.length} 篇研究材料</h3>
            <p style={{ color: "var(--muted)", fontSize: 14, margin: 0 }}>{selectedRecords.length ? selectedRecords.map((n) => n.title).join(" · ") : "请在论文目录或待处理队列勾选材料（无数量限制）。"}</p>
          </div>
          <button
            className="primary-button"
            type="button"
            disabled={!selectedRecords.length}
            onClick={() => { setSelectedPromptKey("controversy"); setView("agents"); }}
          >
            生成关系分析任务单 ↗
          </button>
        </div>

        <div className="section-heading">
          <div><span className="eyebrow">CONTROVERSIES</span><h2>现有争议焦点</h2></div>
          <span>全库精选知产学术争议命题</span>
        </div>
        <div className="topic-grid" style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
          {(navigation?.controversies ?? []).map((note, index) => (
            <article className="topic-card panel-card" key={note.path}>
              <span style={{ color: "var(--terracotta)", font: "italic 16px Georgia, serif", fontWeight: 700 }}>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <small style={{ color: "var(--teal)", fontWeight: 650, fontSize: 12 }}>{note.type}</small>
                <h3 style={{ margin: "8px 0", fontSize: 19 }}>{note.title}</h3>
                <p style={{ color: "var(--muted)", fontSize: 14, lineHeight: 1.7 }}>{note.summary}</p>
              </div>
              <div className="topic-actions" style={{ display: "flex", gap: 8, marginTop: 14 }}>
                <button type="button" className="quiet-button" onClick={() => void openNote(note.path)}>摘要与双链</button>
                <button type="button" className="outline-button" onClick={() => void openInObsidian(note.path)}>Obsidian ↗</button>
                <button type="button" className="quiet-button" onClick={() => toggleContext(note.path)}>
                  {contextPaths.includes(note.path) ? "已选材料" : "+ Agent材料"}
                </button>
              </div>
            </article>
          ))}
        </div>

        {/* Renamed to 作者研究路径 */}
        <div className="section-heading spaced-heading">
          <div><span className="eyebrow">SCHOLAR TRAJECTORIES</span><h2>作者研究路径</h2></div>
          <span>知名知产学者学术脉络与代表作序列（崔国斌、蒋舸、冯术杰、吴伟光等）</span>
        </div>
        <div className="topic-grid" style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
          {(navigation?.researchPaths ?? []).map((note, index) => (
            <article className="topic-card panel-card" key={note.path}>
              <span style={{ color: "var(--terracotta)", font: "italic 16px Georgia, serif", fontWeight: 700 }}>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <small style={{ color: "var(--purple)", fontWeight: 650, fontSize: 12 }}>作者研究路径</small>
                <h3 style={{ margin: "8px 0", fontSize: 19 }}>{note.title}</h3>
                <p style={{ color: "var(--muted)", fontSize: 14, lineHeight: 1.7 }}>{note.summary}</p>
              </div>
              <div className="topic-actions" style={{ display: "flex", gap: 8, marginTop: 14 }}>
                <button type="button" className="quiet-button" onClick={() => void openNote(note.path)}>阅读路径</button>
                <button type="button" className="outline-button" onClick={() => void openInObsidian(note.path)}>Obsidian ↗</button>
                <button type="button" className="quiet-button" onClick={() => toggleContext(note.path)}>
                  {contextPaths.includes(note.path) ? "已选材料" : "+ Agent材料"}
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>
    );
  }

  // 6. Citations View
  function renderCitations() {
    const allPapers = (navigation?.searchNotes ?? []).filter((note) => note.isPaper && !note.isExcluded);
    const papers = citationSearchQuery.trim()
      ? allPapers.filter((note) => noteMatches(note, citationSearchQuery))
      : allPapers;
    const active = allPapers.find((note) => note.path === citationPath);

    return (
      <section>
        <div className="page-intro">
          <span className="eyebrow">2019 LEGAL CITATION MANUAL</span>
          <h1>引注中心</h1>
          <p>书目信息来自 Obsidian YAML，具体观点页码由你依据 PDF 核验。系统不会猜测缺失的作者、期号或页码。</p>
        </div>
        <div className="citation-layout" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          <div className="panel-card citation-form">
            <div className="panel-head">
              <div><span className="eyebrow">SOURCE</span><h3>选择论文与引用方式</h3></div>
              <span>{active?.citationStatus || "等待选择"}</span>
            </div>
            <label className="citation-search-filter" style={{ display: "block", marginBottom: 14 }}>
              快速筛选论文
              <input
                type="text"
                value={citationSearchQuery}
                onChange={(e) => setCitationSearchQuery(e.target.value)}
                placeholder="搜索题名、作者关键词快速过滤..."
                style={{ width: "100%", padding: "9px 12px", borderRadius: 8, border: "1px solid var(--line)", marginTop: 6, fontSize: 13.5 }}
              />
            </label>
            <label style={{ display: "block", marginBottom: 14 }}>
              论文 ({papers.length} 篇可用)
              <select value={citationPath} onChange={(e) => { setCitationPath(e.target.value); setCitationResult(null); }} style={{ width: "100%", padding: "9px 12px", borderRadius: 8, border: "1px solid var(--line)", marginTop: 6, fontSize: 13.5, background: "#fff" }}>
                <option value="">请选择论文</option>
                {papers.map((note) => (
                  <option value={note.path} key={note.path}>
                    {note.title}｜{note.authors.join("、") || "作者待补"}
                  </option>
                ))}
              </select>
            </label>
            <div className="field-row" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
              <label>
                用途
                <select value={citationMode} onChange={(e) => setCitationMode(e.target.value as typeof citationMode)} style={{ width: "100%", padding: "9px 12px", borderRadius: 8, border: "1px solid var(--line)", marginTop: 6, fontSize: 13.5, background: "#fff" }}>
                  <option value="paraphrase">转述观点（参见）</option>
                  <option value="direct">直接引语</option>
                  <option value="general">整篇文献列示</option>
                  <option value="short">前引文（再次引用）</option>
                </select>
              </label>
              <label>
                具体印刷页码
                <input
                  value={pinpointPage}
                  onChange={(e) => setPinpointPage(e.target.value)}
                  placeholder={citationMode === "general" ? "可留空" : "例如 163 或 163-165"}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 8, border: "1px solid var(--line)", marginTop: 6, fontSize: 13.5 }}
                />
              </label>
            </div>
            {active && (
              <div className="citation-metadata" style={{ display: "flex", gap: 8, flexWrap: "wrap", margin: "14px 0" }}>
                <span className="status-badge neutral">{active.journal || "刊物待补"}</span>
                <span className="status-badge neutral">{active.year || "年份待补"}年{active.issue ? `第${active.issue}期` : ""}</span>
                <span className="status-badge neutral">{active.pageRange ? `全文 ${active.pageRange} 页` : "起止页待补"}</span>
                {(active.pdfLink || active.sourcePdf) && <span className="status-badge verified">📄 PDF 已关联</span>}
              </div>
            )}
            <button className="primary-button" type="button" style={{ marginTop: 10 }} onClick={() => void renderCitation()}>生成法学脚注</button>
          </div>

          <div className="panel-card citation-output">
            <div className="panel-head">
              <div><span className="eyebrow">OUTPUT</span><h3>Obsidian 与 Word</h3></div>
              <span>{citationResult ? "待回看PDF" : "尚未生成"}</span>
            </div>
            {citationResult ? (
              <>
                <div className="citation-preview" style={{ background: "var(--teal-soft)", borderLeft: "4px solid var(--teal)", padding: "18px 20px", borderRadius: "0 10px 10px 0" }}>
                  <strong style={{ display: "block", fontSize: 16, lineHeight: 1.7, color: "var(--ink)" }}>{citationResult.citation}</strong>
                  <small style={{ display: "block", marginTop: 8, color: "var(--teal)", fontSize: 12 }}>状态：{citationResult.verification === "pinpoint_unverified" ? "页码由用户输入，仍需回看PDF" : "书目信息已生成"}</small>
                </div>
                <div className="citation-actions" style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 16 }}>
                  <button type="button" className="action-btn" onClick={() => void copyText(citationResult.citation, "Word脚注文本已复制。")}>复制 Word 脚注</button>
                  <button type="button" className="action-btn" onClick={() => void copyText(citationResult.markdownFootnote || `${citationResult.obsidianMarker}\n${citationResult.obsidianDefinition}`, "Obsidian脚注已复制。")}>复制 Obsidian 脚注</button>
                  {citationResult.shortCitation && (
                    <button type="button" className="action-btn" onClick={() => void copyText(citationResult.shortCitation!, "前引文短注已复制。")}>复制前引文</button>
                  )}
                  {active && <button type="button" className="action-btn" onClick={() => void openInObsidian(active.path)}>回到原笔记 ↗</button>}
                </div>
              </>
            ) : (
              <div className="context-empty" style={{ padding: 40, textAlign: "center", color: "var(--muted)", background: "#faf8f2", borderRadius: 10 }}>选择论文并填写具体页码后生成。字段缺失时，系统会明确提示而不会补猜。</div>
            )}
          </div>
        </div>
      </section>
    );
  }

  // 7. Agent Prompt 清单 (Requirement 1 - Image 5 Fix)
  function renderAgents() {
    const selectedRecords = contextPaths.map((path) => navigation?.searchNotes.find((note) => note.path === path)).filter(Boolean) as NoteRecord[];
    const activePrompt = CORE_PROMPTS[selectedPromptKey];

    return (
      <section>
        <div className="page-intro">
          <span className="eyebrow">LEGAL AGENT PROMPTS & SOP BENCHMARK</span>
          <h1>Agent Prompt 清单</h1>
          <p>
            直接内置《法学论文整理SOP：Agent通用执行手册》核心执行规范。
            提供<strong>论文整理、争议结构、总结趋势</strong>三大核心 Prompt 模板，并支持通过下方 API 窗口直接介入大模型调用。
          </p>
        </div>

        {/* SOP Core Principles Banner */}
        <div className="sop-banner">
          <div className="sop-badge">法学论文整理 SOP · Agent 通用执行手册</div>
          <h3>不可违反的四大整理原则</h3>
          <div className="sop-principles-grid">
            <div className="sop-principle-card">
              <strong>1. 全文阅读原则</strong>
              <p>必须覆盖引言、全部大小标题、核心论证展开、案例/数据与制度结论，严禁仅凭摘要和标题概括。</p>
            </div>
            <div className="sop-principle-card">
              <strong>2. 原文忠实原则</strong>
              <p>区分“作者原文论述”与“整理者概括”，保留“原则上”“仅在……时”等限定词，不把反方观点当作作者结论。</p>
            </div>
            <div className="sop-principle-card">
              <strong>3. 元数据保守原则</strong>
              <p>题名、作者、年份和刊物必须严谨核实；原文未设摘要或无法确认的信息明确写明，坚决不编造。</p>
            </div>
            <div className="sop-principle-card">
              <strong>4. 证据可溯原则</strong>
              <p>保留源 PDF 路径与观点页码候选，所有 Agent 分析必须输出可回到本地 Obsidian 复核的双链。</p>
            </div>
          </div>
        </div>

        {/* Prompt Selection Tabs (Fixed Text Concatenation Bug) */}
        <div className="prompt-tabs-bar">
          {(["paper", "controversy", "trend"] as const).map((key) => (
            <button
              key={key}
              type="button"
              className={`prompt-tab-item ${selectedPromptKey === key ? "active" : ""}`}
              onClick={() => setSelectedPromptKey(key)}
            >
              <span className="tab-badge">{CORE_PROMPTS[key].tag}</span>
              <span className="tab-title">{CORE_PROMPTS[key].name}</span>
              <small className="tab-sub">（{CORE_PROMPTS[key].subtitle}）</small>
            </button>
          ))}
        </div>

        {/* Active Prompt Card */}
        <div className="prompt-card">
          <div className="prompt-card-header">
            <div>
              <span className="eyebrow">{activePrompt.tag} · 任务模板</span>
              <h3>{activePrompt.name} <small>（{activePrompt.subtitle}）</small></h3>
              <p className="prompt-desc-text">{activePrompt.desc}</p>
            </div>
            <button
              type="button"
              className="primary-button copy-prompt-btn"
              onClick={() => void copyText(activePrompt.template, "Prompt 模板已复制到剪贴板！")}
            >
              📋 复制本条 Prompt
            </button>
          </div>
          <div className="prompt-content-box">
            <pre>{activePrompt.template}</pre>
          </div>
        </div>

        {/* Selected Materials & Full Task Generator */}
        <div className="agent-workspace">
          <div className="context-panel">
            <div className="panel-head">
              <div><span className="eyebrow">SELECTED MATERIALS</span><h3>已选材料清单</h3></div>
              <span>已选 {selectedRecords.length} 篇材料</span>
            </div>
            {selectedRecords.length ? (
              selectedRecords.map((note) => (
                <div className="context-note" key={note.path}>
                  <span>MD</span>
                  <div>
                    <strong>{note.title}</strong>
                    <small>{note.path}</small>
                  </div>
                  <button type="button" onClick={() => toggleContext(note.path)}>移除</button>
                </div>
              ))
            ) : (
              <div className="context-empty" style={{ padding: 24, textAlign: "center", color: "var(--muted)", background: "#faf8f2", borderRadius: 8 }}>请在论文目录、争议专题或阅读历史中勾选材料（已去除数量上限）。</div>
            )}
          </div>

          <div className="task-panel">
            <div className="panel-head">
              <div><span className="eyebrow">TASK BUILDER</span><h3>生成完整任务单</h3></div>
              <span>已融合 SOP 与已选材料</span>
            </div>
            <label>
              用户自定义补充要求（选填）：
              <textarea
                value={customTaskRemark}
                onChange={(e) => setCustomTaskRemark(e.target.value)}
                placeholder="例如：请特别关注所选论文对'数据财产性权益'与'侵权救济方式'的论争分歧..."
              />
            </label>
            <div className="task-preview">
              <pre>{buildAgentTask()}</pre>
            </div>
            <button
              className="primary-button"
              type="button"
              onClick={() => void copyText(buildAgentTask(), "包含已选材料与SOP的完整任务单已复制！")}
            >
              📋 复制完整可执行任务单
            </button>
          </div>
        </div>

        {/* Agent API Integration Window */}
        <div className="api-workbench-card">
          <div className="panel-head">
            <div>
              <span className="eyebrow">AGENT API WINDOW</span>
              <h3>Agent API 接入工作台</h3>
            </div>
            <span>直连大模型服务</span>
          </div>
          <p style={{ color: "var(--muted)", margin: "4px 0 16px", fontSize: 14 }}>
            可在此配置你的大模型 API 端点，支持一键注入已选文献与《法学论文整理SOP》进行自动化文献整理与学术争点分析。
          </p>
          <div className="api-form-grid">
            <label>
              Base URL 接口地址
              <input
                type="text"
                value={agentApiUrl}
                onChange={(e) => setAgentApiUrl(e.target.value)}
                placeholder="https://api.anthropic.com/v1 或 OpenAI 兼容端点"
              />
            </label>
            <label>
              API Token / 访问密钥
              <input
                type="password"
                value={agentApiToken}
                onChange={(e) => setAgentApiToken(e.target.value)}
                placeholder="sk-..."
              />
            </label>
            <label>
              模型名称
              <input
                type="text"
                value={agentModel}
                onChange={(e) => setAgentModel(e.target.value)}
                placeholder="claude-3-5-sonnet-20241022 或 gpt-4o / deepseek-chat"
              />
            </label>
          </div>

          <div className="api-actions-bar" style={{ display: "flex", gap: "12px", marginTop: "16px" }}>
            <button type="button" className="quiet-button" onClick={saveAgentApiConfig}>
              💾 保存配置到本地
            </button>
            <button
              type="button"
              className="primary-button"
              disabled={agentApiTesting}
              onClick={() => void testAgentApiCall()}
            >
              {agentApiTesting ? "正在调用 Agent..." : "🚀 发送材料与 Prompt 到 Agent 测试分析"}
            </button>
          </div>

          {agentApiOutput && (
            <div className="api-output-box">
              <span className="eyebrow" style={{ color: "#92e0c2" }}>AGENT 响应控制台</span>
              <pre>{agentApiOutput}</pre>
            </div>
          )}
        </div>
      </section>
    );
  }

  // 8. Reading History & Fork & Export View (Requirement 2)
  function renderHistory() {
    const forkedItems = readHistory.filter((h) => h.forked);
    const selectedRecords = contextPaths.map((path) => navigation?.searchNotes.find((note) => note.path === path)).filter(Boolean) as NoteRecord[];

    return (
      <section>
        <div className="page-intro">
          <span className="eyebrow">FOOTPRINTS, FORKS & AUDIT TRAIL</span>
          <h1>阅读历史</h1>
          <p>
            记录你在知识库中的阅读足迹与 Fork 标星笔记，支持无上限批量选择材料，一键导出用于论文写作复核的研究包。
          </p>
        </div>

        <div className="history-tabs-row">
          <div className="stat-card">
            <strong>{readHistory.length}</strong>
            <span>历史阅读足迹</span>
            <small>点击文献自动留痕</small>
          </div>
          <div className="stat-card">
            <strong>{forkedItems.length}</strong>
            <span>Fork 标星重点</span>
            <small>精选重点研读材料</small>
          </div>
          <div className="stat-card">
            <strong>{contextPaths.length}</strong>
            <span>已选研究材料</span>
            <small>已彻底去除8篇上限</small>
          </div>
        </div>

        {/* Forked Items */}
        <div className="section-heading spaced-heading">
          <div><span className="eyebrow">STARRED & FORKED</span><h2>Fork / 重点关注文献</h2></div>
          <span>已标星 {forkedItems.length} 篇重点关注条目</span>
        </div>
        <div className="forked-grid">
          {forkedItems.map((item) => (
            <article className="history-card" key={item.path}>
              <span className="fork-badge">★ 重点收藏</span>
              <h3>{item.title}</h3>
              <p>{item.authors.join("、") || "作者待核"} · {item.journal || item.domain || "期刊"} {item.year ? `(${item.year})` : ""}</p>
              <small>{new Date(item.timestamp).toLocaleString()} · {item.path}</small>
              <div className="history-card-actions">
                <button type="button" className="action-btn" onClick={() => void openNote(item.path)}>预览 ↗</button>
                <button type="button" className="action-btn" onClick={() => void openInObsidian(item.path)}>Obsidian</button>
                <button type="button" className="action-btn" onClick={() => toggleContext(item.path)}>
                  {contextPaths.includes(item.path) ? "已选材料" : "+ Agent材料"}
                </button>
                <button type="button" className="action-btn" style={{ color: "var(--terracotta)" }} onClick={() => toggleFork(item.path)}>取消重点</button>
              </div>
            </article>
          ))}
          {!forkedItems.length && (
            <div className="empty-state panel-card" style={{ padding: 36, textAlign: "center", color: "var(--muted)" }}>
              暂无 Fork 重点文献。在论文目录或阅读抽屉中点击「☆ 收藏」即可一键将重点文献收录至此。
            </div>
          )}
        </div>

        {/* Recent Reading Footprints */}
        <div className="section-heading spaced-heading">
          <div><span className="eyebrow">RECENT FOOTPRINTS</span><h2>最近阅读足迹</h2></div>
          <span>按时间倒序记录你的研读轨迹</span>
        </div>
        <div className="history-timeline">
          {readHistory.slice(0, 30).map((item) => (
            <article className="history-row" key={`${item.path}-${item.timestamp}`}>
              <div className="history-main-info">
                <strong>{item.title}</strong>
                <small>{item.authors.join("、") || "作者待核"} · {item.journal || "刊物待核"} {item.year ? `(${item.year})` : ""} · {new Date(item.timestamp).toLocaleTimeString()}</small>
              </div>
              <div className="history-actions">
                <button type="button" className="action-btn" onClick={() => void openNote(item.path)}>预览</button>
                <button type="button" className={`action-btn ${item.forked ? "action-fork forked" : ""}`} onClick={() => toggleFork(item.path)}>
                  {item.forked ? "★ 重点" : "☆ 收藏"}
                </button>
                <button type="button" className="action-btn" onClick={() => toggleContext(item.path)}>
                  {contextPaths.includes(item.path) ? "已选材料" : "+ 材料"}
                </button>
              </div>
            </article>
          ))}
          {!readHistory.length && (
            <div className="empty-state panel-card" style={{ padding: 36, textAlign: "center", color: "var(--muted)" }}>
              尚无阅读足迹。点击论文阅读后，足迹会自动生成并留存。
            </div>
          )}
        </div>

        {/* Selected Materials & Export Center */}
        <div className="section-heading spaced-heading">
          <div><span className="eyebrow">RESEARCH PACKAGE EXPORT</span><h2>研究包导出与复核</h2></div>
          <span>支持多格式导出已选材料、阅读历史与引注</span>
        </div>
        <div className="export-layout" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          <div className="panel-card export-manifest">
            <div className="panel-head">
              <div><span className="eyebrow">MANIFEST</span><h3>本次已选材料</h3></div>
              <span>已选 {selectedRecords.length} 篇材料</span>
            </div>
            {selectedRecords.length ? (
              selectedRecords.map((note) => (
                <div className="context-note" key={note.path}>
                  <span>MD</span>
                  <div>
                    <strong>{note.title}</strong>
                    <small>{note.path}</small>
                  </div>
                  <button type="button" onClick={() => toggleContext(note.path)}>移除</button>
                </div>
              ))
            ) : (
              <div className="context-empty" style={{ padding: 24, textAlign: "center", color: "var(--muted)", background: "#faf8f2", borderRadius: 8 }}>尚未选择材料，可在论文目录或足迹中点击「+ 材料」添加。</div>
            )}
          </div>

          <div className="panel-card audit-card">
            <span className="eyebrow">AUDIT & EXPORT</span>
            <h3>导出研究成果</h3>
            <ul style={{ paddingLeft: 20, color: "var(--muted)", fontSize: 14, lineHeight: 2 }}>
              <li>所选论文的 Obsidian 路径与书目元数据（无篇数限制）</li>
              <li>历史研读足迹与重点 Fork 论文汇总</li>
              <li>最新生成的法学引注（遵照《法学引注手册》）</li>
              <li>SOP 规范复核备忘与回看 PDF 指引</li>
            </ul>
            <div style={{ display: "flex", gap: "12px", marginTop: "20px" }}>
              <button
                className="primary-button"
                type="button"
                onClick={downloadResearchPackage}
              >
                导出 JSON 研究包
              </button>
              <button
                className="quiet-button"
                type="button"
                onClick={exportMarkdownSummary}
              >
                导出 Markdown 清单
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  const currentNav = NAV_ITEMS.find((item) => item.id === view);

  return (
    <main className="obsidian-app">
      {/* Left Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">L</span>
          <div>
            <strong>LexTrace</strong>
            <small>Obsidian Research Workbench</small>
          </div>
        </div>
        <div className="vault-chip">
          <span className={bridgeState === "connected" ? "connection-dot ready" : "connection-dot"} />
          <div>
            <strong>{navigation?.vaultName || "Obsidian Vault"}</strong>
            <small>{bridgeState === "connected" ? "样板可写 · 目录自动更新" : "请使用一键启动器"}</small>
          </div>
        </div>
        <nav>
          {NAV_ITEMS.map((item) => (
            <button
              type="button"
              className={view === item.id ? "active" : ""}
              key={item.id}
              onClick={() => setView(item.id)}
            >
              <span>{item.glyph}</span>
              <div>
                <strong>{item.label}</strong>
                <small>{item.caption}</small>
              </div>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button type="button" onClick={() => void openInObsidian("知识产权/00_知识产权研究导航.md")}>
            <span className="api-dot ready" />原生导航
          </button>
          <button type="button" onClick={() => void openInObsidian()}>打开 Obsidian ↗</button>
        </div>
      </aside>

      {/* Main Shell */}
      <div className="main-shell">
        {/* Topbar: Clean layout without global search bar */}
        <header className="topbar">
          <div className="topbar-breadcrumb">
            <span className="breadcrumb-nav">{currentNav?.label}</span>
            <span className="breadcrumb-sep">/</span>
            <span className="breadcrumb-caption">{currentNav?.caption}</span>
          </div>
          <div className="top-actions">
            <span className="auto-update-label"><i />10秒自动检查</span>
            <button type="button" className="top-refresh-btn" onClick={() => void loadNavigation()}>↻ 刷新</button>
            <button className="obsidian-button" type="button" onClick={() => void openInObsidian("知识产权/00_知识产权研究导航.md")}>
              OB&nbsp; 原生导航 ↗
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="content-shell">
          {bridgeState === "offline" && (
            <div className="connection-warning" style={{ marginBottom: 20, padding: "14px 18px", border: "1px solid #ecc9bd", background: "#fef3ee", borderRadius: 10, display: "flex", alignItems: "center", gap: 14, color: "#8a3b25", fontSize: 13.5 }}>
              <strong>本机工作台尚未启动</strong>
              <span style={{ flex: 1 }}>请双击“启动LexTrace.command”；原生 Obsidian 导航仍可独立使用。</span>
              <button type="button" className="primary-button" style={{ background: "#8a3b25" }} onClick={() => void loadNavigation()}>重新连接</button>
            </div>
          )}
          {view === "overview" && renderOverview()}
          {view === "rulebook" && renderRulebook()}
          {view === "intake" && renderIntake()}
          {view === "library" && renderLibrary()}
          {view === "relations" && renderRelations()}
          {view === "citations" && renderCitations()}
          {view === "agents" && renderAgents()}
          {view === "history" && renderHistory()}
        </div>
      </div>

      {/* Drawer Note Preview */}
      {(selectedNote || noteLoading) && (
        <aside className="note-drawer">
          <div className="drawer-head">
            <span>{noteLoading ? "正在读取…" : "OBSIDIAN NOTE PREVIEW"}</span>
            <button type="button" onClick={() => setSelectedNote(null)}>×</button>
          </div>
          {selectedNote && (
            <>
              <div className="drawer-title">
                <small>{selectedNote.path}</small>
                <h2>{selectedNote.title}</h2>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {selectedNote.authors.map((author) => <span key={author} className="status-badge neutral">{author}</span>)}
                  {selectedNote.year && <span className="status-badge neutral">{selectedNote.year}</span>}
                  {selectedNote.journal && <span className="status-badge neutral">{selectedNote.journal}</span>}
                </div>
              </div>
              <div className="drawer-actions">
                <button className="primary-button" type="button" onClick={() => void openInObsidian(selectedNote.path)}>
                  在 Obsidian 阅读全文 ↗
                </button>
                <button
                  className={contextPaths.includes(selectedNote.path) ? "action-btn action-select selected" : "action-btn"}
                  type="button"
                  onClick={() => toggleContext(selectedNote.path)}
                >
                  {contextPaths.includes(selectedNote.path) ? "已选材料" : "+ Agent材料"}
                </button>
                <button
                  className={readHistory.some((h) => h.path === selectedNote.path && h.forked) ? "action-btn action-fork forked" : "action-btn"}
                  type="button"
                  onClick={() => toggleFork(selectedNote.path)}
                >
                  {readHistory.some((h) => h.path === selectedNote.path && h.forked) ? "★ 已重点收藏" : "☆ 重点收藏"}
                </button>
                <button className="quiet-button" type="button" onClick={() => void copyText(selectedNote.path, "笔记路径已复制。")}>
                  复制路径
                </button>
              </div>

              {selectedNote.isPaper && (
                <div className="drawer-citation-box" style={{ margin: "18px 0", border: "1px solid var(--line)", borderRadius: 12, background: "#faf8f2", padding: 18 }}>
                  <div className="drawer-citation-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span className="eyebrow">LEGAL CITATION · 《法学引注手册》</span>
                    <button type="button" className="drawer-cite-open-btn" style={{ border: 0, background: "transparent", color: "var(--teal)", cursor: "pointer", fontSize: 12.5, fontWeight: 700 }} onClick={() => void openQuickCitation(selectedNote)}>
                      精确引注弹窗 ↗
                    </button>
                  </div>
                  <div className="drawer-citation-body">
                    <p className="drawer-citation-text" style={{ font: "500 15px/1.75 Georgia, Songti SC, serif", color: "var(--ink)", margin: "10px 0 14px" }}>{buildSimpleCitation(selectedNote)}</p>
                    <div className="drawer-citation-actions" style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      <button type="button" className="action-btn" onClick={() => void copyText(buildSimpleCitation(selectedNote), "Word 脚注已复制到剪贴板！")}>
                        复制 Word 脚注
                      </button>
                      <button
                        type="button"
                        className="action-btn"
                        onClick={() => void copyText(`[^${selectedNote.recordId || "cite"}]: ${buildSimpleCitation(selectedNote)}`, "Markdown 脚注已复制到剪贴板！")}
                      >
                        复制 Markdown 脚注
                      </button>
                      <button type="button" className="action-btn" onClick={() => void copyText(`${selectedNote.authors.join("、") || "作者待核"}前引文。`, "前引文已复制！")}>
                        复制前引文
                      </button>
                      {(selectedNote.pdfLink || selectedNote.sourcePdf) && (
                        <button type="button" className="action-btn" style={{ background: "var(--teal-soft)", color: "var(--teal)", borderColor: "var(--teal-border)" }} onClick={() => void openInObsidian(selectedNote.path)}>
                          📄 在 Obsidian 分屏阅读 PDF (PDF++) ↗
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              <section className="preview-summary" style={{ border: "1px solid var(--line)", borderRadius: 10, background: "#faf8f2", padding: 18, marginBottom: 18 }}>
                <span className="eyebrow">SUMMARY</span>
                <p style={{ margin: "6px 0 0", color: "#3d4844", fontSize: 14, lineHeight: 1.8 }}>{selectedNote.summary || "这篇导航笔记没有设置摘要，请在 Obsidian 中查看完整内容。"}</p>
              </section>

              <div className="drawer-columns" style={{ display: "grid", gridTemplateColumns: "1.2fr .8fr", gap: 14, marginBottom: 18 }}>
                <div style={{ background: "#faf8f3", borderRadius: 10, padding: 16 }}>
                  <span className="eyebrow">OUTLINE</span>
                  {selectedNote.headings.slice(1, 16).map((heading, index) => (
                    <span
                      className="outline-item"
                      key={`${heading.text}-${index}`}
                      style={{ display: "block", paddingBlock: 4, paddingLeft: `${Math.max(0, heading.level - 1) * 12}px`, color: "#54615c", fontSize: 12.5 }}
                    >
                      {heading.text}
                    </span>
                  ))}
                </div>
                <div style={{ background: "#faf8f3", borderRadius: 10, padding: 16 }}>
                  <span className="eyebrow">LINKS</span>
                  <p style={{ margin: "8px 0 0", color: "var(--muted)", fontSize: 13 }}>{selectedNote.links.length} 个出链 · {selectedNote.backlinks.length} 个反链</p>
                </div>
              </div>

              <div className="link-preview" style={{ borderTop: "1px solid var(--line)", paddingTop: 16 }}>
                <span className="eyebrow">OUTGOING LINKS</span>
                <div style={{ display: "grid", gap: 6, marginTop: 8 }}>
                  {selectedNote.links.slice(0, 18).map((link) => link.path ? (
                    <button type="button" style={{ border: 0, background: "transparent", textAlign: "left", color: "var(--teal)", fontSize: 13, padding: "4px 0", cursor: "pointer" }} key={`${link.target}-${link.path}`} onClick={() => void openNote(link.path!)}>
                      → {link.label}
                    </button>
                  ) : (
                    <span key={link.target} style={{ color: "var(--muted)", fontSize: 13 }}>· {link.label}</span>
                  ))}
                </div>
              </div>

              <div className="backlinks" style={{ borderTop: "1px solid var(--line)", paddingTop: 16, marginTop: 14 }}>
                <span className="eyebrow">BACKLINKS</span>
                <div style={{ display: "grid", gap: 6, marginTop: 8 }}>
                  {selectedNote.backlinks.slice(0, 16).map((note) => (
                    <button type="button" style={{ border: 0, background: "transparent", textAlign: "left", color: "var(--teal)", fontSize: 13, padding: "4px 0", cursor: "pointer" }} key={note.path} onClick={() => void openNote(note.path)}>
                      ← {note.title}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </aside>
      )}

      {/* Quick Citation Modal */}
      {quickCitationNote && (
        <div className="modal-backdrop" onClick={() => setQuickCitationNote(null)}>
          <div className="api-modal quick-citation-modal" onClick={(event) => event.stopPropagation()} style={{ width: "min(640px, 94vw)", padding: 28 }}>
            <div className="modal-head">
              <div>
                <span className="eyebrow">2019 LEGAL CITATION · 一键引注与定位</span>
                <h2 style={{ margin: "6px 0 4px", fontSize: 20, fontFamily: "Georgia, Songti SC, serif" }}>{quickCitationNote.title}</h2>
                <p className="quick-citation-authors" style={{ color: "var(--muted)", fontSize: 13, margin: 0 }}>
                  {quickCitationNote.authors.join("、") || "作者待核"} · {quickCitationNote.journal || "刊物待核"} {quickCitationNote.year ? `(${quickCitationNote.year})` : ""}
                </p>
              </div>
              <button type="button" onClick={() => setQuickCitationNote(null)}>×</button>
            </div>

            <div className="quick-citation-body" style={{ marginTop: 18 }}>
              <div className="quick-mode-tabs" style={{ display: "flex", gap: 6, marginBottom: 16, overflowX: "auto" }}>
                <button
                  type="button"
                  className={quickMode === "paraphrase" ? "action-btn action-select selected" : "action-btn"}
                  onClick={() => void updateQuickCitation(quickCitationNote, "paraphrase", quickPinpoint)}
                >
                  转述 (参见)
                </button>
                <button
                  type="button"
                  className={quickMode === "direct" ? "action-btn action-select selected" : "action-btn"}
                  onClick={() => void updateQuickCitation(quickCitationNote, "direct", quickPinpoint)}
                >
                  直接引语
                </button>
                <button
                  type="button"
                  className={quickMode === "general" ? "action-btn action-select selected" : "action-btn"}
                  onClick={() => void updateQuickCitation(quickCitationNote, "general", quickPinpoint)}
                >
                  整篇文献
                </button>
                <button
                  type="button"
                  className={quickMode === "short" ? "action-btn action-select selected" : "action-btn"}
                  onClick={() => void updateQuickCitation(quickCitationNote, "short", quickPinpoint)}
                >
                  前引文 (再次引用)
                </button>
              </div>

              <div className="quick-pinpoint-row" style={{ marginBottom: 16 }}>
                <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "var(--ink)", marginBottom: 6 }}>
                  具体引用页码 (Pinpoint Page)：
                  <input
                    type="text"
                    value={quickPinpoint}
                    placeholder={quickMode === "general" ? "整篇引用可留空" : "例如 15 或 15-18"}
                    style={{ width: "100%", padding: "10px 14px", borderRadius: 8, border: "1px solid var(--line)", marginTop: 6, fontSize: 14 }}
                    onChange={(event: ChangeEvent<HTMLInputElement>) => {
                      const val = event.target.value;
                      setQuickPinpoint(val);
                      void updateQuickCitation(quickCitationNote, quickMode, val);
                    }}
                  />
                </label>
              </div>

              {quickError && (
                <div className="quick-citation-error" style={{ color: "var(--terracotta)", background: "var(--terracotta-soft)", border: "1px solid var(--terracotta-border)", padding: "10px 14px", borderRadius: 8, marginBottom: 14, fontSize: 13 }}>⚠️ {quickError}</div>
              )}

              {quickResult && (
                <div className="quick-citation-preview-card" style={{ background: "var(--teal-soft)", borderLeft: "4px solid var(--teal)", padding: "16px 20px", borderRadius: "0 10px 10px 0", marginBottom: 18 }}>
                  <span className="eyebrow" style={{ color: "var(--teal)" }}>引注预览 (《法学引注手册》规范)</span>
                  <div className="quick-citation-text" style={{ font: "500 16px/1.8 Georgia, Songti SC, serif", color: "var(--ink)", marginTop: 6 }}>{quickResult.citation}</div>
                  {quickResult.shortCitation && quickMode !== "short" && (
                    <div className="quick-citation-short-text" style={{ marginTop: 10, paddingTop: 10, borderTop: "1px dashed var(--teal-border)", color: "#2d6357", fontSize: 13 }}>
                      <small>再次引用形式：</small>{quickResult.shortCitation}
                    </div>
                  )}
                </div>
              )}

              <div className="quick-citation-actions-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
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
                  className="outline-button"
                  disabled={!quickResult}
                  onClick={() => void copyText(quickResult?.markdownFootnote || quickResult?.obsidianDefinition || "", "Markdown 脚注已复制到剪贴板！")}
                >
                  📋 复制 Markdown 脚注
                </button>
                <button
                  type="button"
                  className="outline-button"
                  disabled={!quickResult}
                  onClick={() => void copyText(quickResult?.shortCitation || `${quickCitationNote.authors.join("、")}前引文。`, "前引文短注已复制！")}
                >
                  📋 复制前引文
                </button>
                <button
                  type="button"
                  className="outline-button"
                  onClick={() => void openInObsidian(quickCitationNote.path)}
                >
                  📄 在 Obsidian 查看 / PDF++ ↗
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {notice && (
        <button type="button" className="toast" onClick={() => setNotice("")}>
          {notice}<span>×</span>
        </button>
      )}
    </main>
  );
}
