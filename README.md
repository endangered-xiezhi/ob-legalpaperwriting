<div align="center">

# ⚖️ 法脉 LexTrace (ob-legalpaperwriting)
### **新一代法学研究智能工作台与内生化学术知识中枢**
*An End-to-End Legal Academic Knowledge Base & AI-Assisted Research Operating System*

<br/>

[![GitHub Private Repo](https://img.shields.io/badge/Security-Private%20Repository-success?style=for-the-badge&logo=github&logoColor=white&color=0d1117)](https://github.com/endangered-xiezhi/ob-legalpaperwriting)
[![Academic Standards](https://img.shields.io/badge/Standards-CLSCI%2016%20Core%20Law%20Journals-blue?style=for-the-badge&logo=googlescholar&logoColor=white&color=1e3a8a)](https://github.com/endangered-xiezhi/ob-legalpaperwriting)
[![License](https://img.shields.io/badge/License-LGPL%20v2.1-orange?style=for-the-badge&color=b45309)](LICENSE)
[![Zero Config](https://img.shields.io/badge/Obsidian-Zero%20Config%20Turnkey-purple?style=for-the-badge&logo=obsidian&logoColor=white&color=4c1d95)](https://obsidian.md)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey?style=for-the-badge)](https://github.com/endangered-xiezhi/ob-legalpaperwriting)

<br/>

> **麦肯锡咨询式架构 · 本地化离线隐私保障 · 学术观点可核验追溯 · 小白零门槛开箱即用**
> 
> 本系统专为法学研究生、高校法学学者、知识产权律师及跨学科法律科技研究者打造。通过全自动数据挖掘采集器、逐页标柱精准引注引擎、Obsidian PDF++ 原版分屏穿透，以及基于 Next.js 的 AI 学术争议工作台，构建从**文献采集 ➔ 转化性卡片提炼 ➔ 体系化图谱沉淀 ➔ 论点推演验证**的全流程研究闭环。

<br/>

| 📊 **已收录法学核心文献卡** | 🏛️ **涵盖部门法体系** | 🎯 **权威学术期刊范式** | 🔒 **数据合规与隐私姿态** | ⚡ **小白上手配置耗时** |
| :---: | :---: | :---: | :---: | :---: |
| **538+ 篇精萃卡片** | **7 大知识产权领域** | **16 种 CLSCI 法学核心** | **100% 本地运行 / 零数据泄露** | **< 3 分钟一键启动** |

</div>

---

## 📑 麦肯锡架构总览与执行摘要 (Executive Summary)

### 1. 核心战略背景与痛点破解 (Strategic Imperative)

在传统法学学术研究、学位论文写作与前沿司法实务中，研究者普遍面临三大结构性瓶颈：

```
传统法学文献研究三大瓶颈                         法脉 LexTrace 闭环解决方案
┌─────────────────────────┐                     ┌─────────────────────────┐
│  检索碎片化与下载割裂   │ ───────────────►    │  CNKI 双模自动化全量摄入│
│(繁琐逐篇导出，命名混乱) │  [自动采集合成]     │(免登状态/EndNote自动解析)│
└─────────────────────────┘                     └─────────────────────────┘
             │                                               │
┌─────────────────────────┐                     ┌─────────────────────────┐
│  文献阅读卡与原版脱节   │ ───────────────►    │  PDF++ 原生分屏双向穿透 │
│ (只抄笔记，难以页码溯源)│  [逐页标柱锚定]     │(双击直达原版高亮指定行) │
└─────────────────────────┘                     └─────────────────────────┘
             │                                               │
┌─────────────────────────┐                     ┌─────────────────────────┐
│  AI 辅助生成"学术幻觉"  │ ───────────────►    │  显式页码约束+学说对比盘│
│(捏造引注页码/虚构学者论点│  [严格可溯源验证]   │(忠实提炼问题、理论与方案│
└─────────────────────────┘                     └─────────────────────────┘
```

1. **文献获取与元数据割裂**：知网手动检索下载极度繁琐，引注卷期号、起止页码、DOI 经常丢失或格式不一。
2. **文献阅读笔记与原文割裂**：笔记记在 Word 或传统软件中，想核验原作者具体论述时需要重新在几百个 PDF 中翻页找寻。
3. **大模型辅助写作的“伪学术幻觉”**：通用大语言模型缺乏法学专属知识切片，容易虚构学说观点或编造不存在的《法学研究》《中国法学》页码。

**法脉 LexTrace** 坚持**“转化性使用（Transformative Use）”**与**“显式标柱精准溯源”**原则，系统自带经过严谨学术转化的 538+ 篇法学阅读卡与学科图谱，同时配备完全自动化的知网全量抓取工具与本地 AI 桥接器，让学者在完全离线、隐私受控的环境中实现高水平学术生产。

---

## 🏛️ MECE 体系架构矩阵 (System Architecture Matrix)

系统严格按照咨询业界互不重叠、完全穷尽（MECE）原则划分为四大支撑层级：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      用户交互与学术推演工作台 (Layer 4)                     │
│   Web 仪表盘 (Next.js 15)  │  AI 学说争议对照台  │  学术思维导图 (Mindmap)   │
├─────────────────────────────────────────────────────────────────────────────┤
│                      知识沉淀与双向穿透中枢 (Layer 3)                       │
│   Obsidian 本地双链网络    │  PDF++ 分屏精准联动 │  Dataview 学术元数据查询 │
├─────────────────────────────────────────────────────────────────────────────┤
│                      转化性学术文献与图谱库 (Layer 2)                       │
│   538+ 篇文献阅读卡        │  7 大部门法专题网络 │  4 大清华导师学说路径    │
├─────────────────────────────────────────────────────────────────────────────┤
│                      数据摄入与逐页标柱引擎 (Layer 1)                       │
│   CNKI 学术双模采集器      │  EndNote 元数据解析 │  PyMuPDF 显式页码标柱    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 矩阵明细拆解

| 层次维度 | 核心组件 | 技术底座 | 业务价值与学术赋能 |
| :--- | :--- | :--- | :--- |
| **Layer 1: 摄入层** | `cnki_crawler/` | Selenium + PyMuPDF | 自动完成作者全量与 CLSCI 筛选论文下载，自动生成带有 `[[PDF_PAGE:n]]` 显式分页标柱的结构化文本。 |
| **Layer 2: 资产层** | `vault/知识产权/` | Markdown + YAML 前言 | 沉淀 538+ 篇精读卡片（问题的提出、学术批评、制度方案、核心金句），覆盖著作权、专利、商标、反不正当竞争等。 |
| **Layer 3: 沉淀层** | `vault/.obsidian/` | Obsidian Native Plugins | 预装 **PDF++**、**Dataview**、**Enhancing Mindmap**、**Article Annotator**，实现阅读卡与原版 PDF 视窗并排联动。 |
| **Layer 4: 展现层** | `local_bridge/` + Web | Python 3 + Next.js 15 | 提供极速浏览器界面、实时动态同步、导师学说脉络梳理及本地化大模型 API 交互接口。 |

---

## 🚀 小白零基础 3 分钟极速上手指南 (Novice Quickstart)

> [!TIP]
> **为零代码基础学者量身定制**：本项目已将所有 Obsidian 插件、样式配置及环境检查完全打包。即使您从未打开过终端或写过一行代码，也只需点击一次即可完整运行！

```
                     小白 0 基础启动决策树 (Decision Tree)
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
              【场景 A：使用网页版工作台】       【场景 B：使用 Obsidian 原生笔记】
                      │                                 │
           双击运行根目录脚本:                  打开 Obsidian 官方客户端
    `一键安装与启动_小白专属.command`                    │
                      │                         点击「打开本地仓库 (Open Vault)」
      [自动检测/安装 Node.js 与依赖]                    │
                      │                         选择进入本项目的 `vault/` 目录
                      ▼                                 │
           浏览器自动弹窗并进入:                         ▼
        http://localhost:3000/               所有插件与 538+ 篇论文卡即刻可用！
```

### 步骤详解（macOS / Windows / Linux 通用）

<details open>
<summary><b>▶ 点击展开：超详细图文级操作步骤</b></summary>

#### 第一步：克隆或下载私有代码仓库到本机
使用 Git 克隆当前私有仓库（或直接在 GitHub 页面点击绿色的 **Code ➔ Download ZIP** 解压）：
```bash
git clone https://github.com/endangered-xiezhi/ob-legalpaperwriting.git
cd ob-legalpaperwriting
```

#### 第二步：一键运行自动化装配器
- **macOS 用户（最简模式）**：
  直接在访达（Finder）中找到项目根目录下的 **`一键安装与启动_小白专属.command`**，**鼠标双击**即可！
  - 脚本会自动检查您的 Python 3 与 Node.js 环境；
  - 若检测到缺少 Node.js，脚本会**自动调用 Homebrew 安装**或**直接打开官方极速下载页面**，只需点击下一步即可；
  - 脚本会自动安装所需依赖包（自动接入国内清华大学与 npmmirror 镜像源高速下载）；
  - 完成后，脚本会自动启动服务，并在默认浏览器中为您打开 `http://localhost:3000/`。
- **命令行用户 / Linux / Windows WSL**：
  只需执行以下两行命令：
  ```bash
  chmod +x install_dependencies.sh
  ./install_dependencies.sh
  ./启动LexTrace.command
  ```

#### 第三步：在 Obsidian 中打开知识库（100% 免配置）
1. 下载并安装 [Obsidian 官方客户端](https://obsidian.md/)（完全免费）；
2. 启动 Obsidian，在弹出的欢迎界面中选择 **“打开本地文件夹作为仓库 (Open folder as vault)”**；
3. 点击浏览，选中本项目中的 **`vault/`** 文件夹并打开；
4. **无需手动搜索下载任何插件！** 本项目已在 `vault/.obsidian/plugins/` 预装了所有必需插件并已开启：
   - 🌟 **Dataview**：学术文献元数据统计与动态检索看板；
   - 📄 **PDF++**：原版 PDF 视窗联动，高亮与论文笔记无缝跳转；
   - 🧠 **Enhancing Mindmap**：学术学说与部门法思维导图可视化；
   - ✏️ **Article Annotator**：文献批注与深度评注工具。
5. 打开 `vault/知识产权/00_知识产权研究导航.md`，即可开启您的学术研读之旅！

</details>

---

## 📚 知识资产库全景分布 (Knowledge Base Taxonomy)

本项目内置的 `vault/知识产权/` 知识库组织严密，各子目录职责清晰：

```
vault/
└── 知识产权/
    ├── 00_知识产权研究导航.md            # 全局交互式学术导航首页
    ├── 论文库/                           # 538+ 篇深度学术精读卡 (带页码/学说提炼)
    ├── 领域/                             # 7 大部门法分类看板 (著作权/商标/专利/竞争法等)
    ├── 导师/                             # 权威学者学说图谱 (崔国斌/蒋舸/冯术杰/吴伟光等)
    ├── 清华研究路径/                     # 考前速览、修法对照、前沿制度精讲与法域总目录
    ├── 北大知产/                         # 6 大专题图谱 (AIGC、标准必要专利、平台治理等)
    ├── 法律法规与典型案例/               # 司法审判参考、典型指导性案例与修法沿革
    ├── 知产英语/                         # WIPO 通识读物与国际知识产权法专业口语表达
    ├── 研究工作台/                       # 学位论文大纲、模拟辩论交接文档与学术工作台
    └── PDF/                              # 原版文献存储中心 (支持软链接零磁盘冗余挂载)
```

### 538+ 篇文献阅读卡标准结构示例
每篇文献卡均遵循严格的法学实证研究格式，保证学术严谨性与论点可复现：

```markdown
---
title: "论视听作品的范围及权利归属"
author: "王迁"
journal: "法学研究"
year: 2021
issue: "第3期"
pages: "102-120"
doi: "10.13415/j.cnki.fxyj.2021.03.007"
tags: [著作权法, 视听作品, 权利归属]
---

# 论视听作品的范围及权利归属

> [!info] 📄 原版文献阅读与分屏跳转
> 本文关联的原版 PDF 文献：[[论视听作品的范围及权利归属_王迁.pdf]]

## 📌 一、问题的提出与核心焦点
修法后“视听作品”取代“电影作品和以类似摄制电影的方法创作的作品”，如何准确认定其外延边界...

## ⚖️ 二、学说争议与理论分析
- **否定说观点**：...
- **肯定说观点**：...

## 💡 三、本文核心结论与制度建构方案
根据《著作权法》第十七条之立法意旨...

## 🎯 四、核心观点可核验金句及精确页码
- 观点1：认定视听作品必须具备“由一系列有伴音或者无伴音的画面组成”的实质要件（见第 106 页）。
```

---

## 🔒 私有仓库（Private Repo）与云端托管配置专题报告

针对使用者关心的核心疑问：**“将仓库设为私有（Private）后，还可以托管在 GitHub 并使用云端部署配置吗？”**

麦肯锡咨询团队通过技术可行性论证与矩阵评估，给出明确权威结论：

> [!NOTE]
> ### 🎯 核心结论：完全可以，且在学术安全与隐私保护上比公开仓库更具绝对优势！
> **将本仓库设置为私有仓库后，GitHub 原生生态与第三方现代化云平台（Vercel, Cloudflare, Render）完全支持私有仓库的免费无缝集成与全自动构建部署！**

### 1. 私有仓库云端集成能力矩阵 (Feasibility Matrix)

| 云端能力 / 平台 | 免费额度 / 权限状态 | 私有仓库支持度 | 运作机制与配置指引 |
| :--- | :--- | :---: | :--- |
| **▲ Vercel 云端部署** | **永久免费 (Hobby Plan)** | **100% 完全支持** | 通过 GitHub 账号登录 Vercel，直接 Import 私有仓库 `ob-legalpaperwriting`。Vercel 获得授权后拉取私有源码并在云端构建，生成独立的公开或受密码保护的 Web 访问地址（例如 `lextrace.vercel.app`）。**您的核心源码和论文数据库对公众完全保密不可见！** |
| **▲ Cloudflare Pages** | **永久免费 (无限带宽)** | **100% 完全支持** | 绑定私有仓库，全球 300+ 边缘节点极速分发，免费自带 HTTPS SSL 证书。 |
| **▲ GitHub Actions** | **每月 2,000 分钟免费运行** | **100% 完全支持** | 私有仓库享有每月 2,000 分钟免费的 CI/CD 云端虚拟机构建时间。可用于编写定时知网爬虫、自动化格式检查或构建静态报告。 |
| **▲ GitHub Codespaces** | **每月 60 小时免费** | **100% 完全支持** | 即使身边没有电脑，也可以在 iPad 或任意浏览器中一键打开完整的云端 VS Code 开发环境，直接在线编辑文献卡与调试代码。 |
| **▲ 团队协同 (Collaborators)**| **完全免费且不限人数** | **100% 完全支持** | 在仓库 `Settings ➔ Collaborators` 中可精准添加特定导师、师兄妹的 GitHub 账号赋予只读或读写权限，外人完全无法检索或查看。 |

### 2. 极简云端托管实操指南（Vercel / Codespaces / Actions）

> 📖 **完整详尽图文指引请查阅**：[《云端免费托管与部署实操手册（零门槛版）》](docs/云端免费托管与部署实操手册_零门槛.md)

#### 🚀 方案 A：Vercel 30 秒一键上线（永久免费 / 手机平板即用）
1. 访问 [https://vercel.com/signup](https://vercel.com/signup) 并使用您的 GitHub 账号登录；
2. 点击右上角 **"Add New..." ➔ "Project"**；
3. 在 Import Git Repository 列表中，选中私有仓库 **`ob-legalpaperwriting`**；
4. 项目已内置 `vercel.json`，无需修改任何设置，直接点击 **"Deploy"**；
5. 约 40 秒后即可获得永久在线的工作台网址（如 `https://ob-legalpaperwriting.vercel.app`），代码对公众完全保密！

#### 💻 方案 B：GitHub Codespaces 云端免装机工作台（浏览器即开 VS Code）
1. 在本私有仓库网页右上角点击绿色的 **"Code" ➔ "Codespaces"**；
2. 点击 **"Create codespace on main"**；
3. 浏览器即刻在云端启动完整的 VS Code，已为您全自动配置好 Python 3.11、Node.js 22 与全套依赖，免除任何本机安装！

#### ⚡ 方案 C：GitHub Actions 云端自动构建与核验（已全自动生效）
- 本项目已内置 `.github/workflows/ci.yml`；
- 每次您向私有仓库提交或更新论文笔记，GitHub 云端虚拟机会自动执行文献完整性核验、依赖测试与发布包构建，并保存在 Actions Artifacts 中。

---

## 🛠️ 知网学术双模采集器操作指南 (`cnki_crawler/`)

若您需要为本地知识库持续摄入最新发表的学者论文，可直接使用内置的高级知网爬虫：

```bash
# 进入爬虫目录
cd cnki_crawler

# 方式一：双击运行 macOS 专属脚本
./启动知网爬虫.command

# 方式二：命令行启动
python3 run_spider.py
```

### 两种采集模式
1. **作者全量模式 (Author Mode)**：
   - 专为整理特定法学权威学者（如王迁、崔国斌、蒋舸、冯术杰等）的学术全貌设计；
   - 自动突破期刊级别限制，抓取并归档作者历年所有核心成果。
2. **CLSCI 核心期刊筛选模式 (Journal Mode)**：
   - 内置 16 种法学核心期刊白名单（《中国法学》《法学研究》《中外法学》《法学家》《清华法学》等）；
   - 自动剔除书评、会议综述等杂质，精准捕获长篇法学原创论文。

---

## ⚖️ 学术伦理、合理使用与合规声明 (Academic Compliance)

1. **转化性使用（Transformative Use）原则**：
   本项目收录的所有 Markdown 文献卡片均系对公开发表学术文献的**学术分析、框架归纳、批判性反思与观点提炼**，属于我国《著作权法》第二十四条第一款第二项规定的**“为介绍、评论某一作品或者说明某一问题，在作品中适当引用他人已经发表的作品”**之法定合理使用范畴，绝非对原版期刊排版或全文的商业性原样兜售。
2. **隐私与数据不出本地安全保障**：
   本系统的一切数据检索、向量索引、文本切片均**默认纯本地计算**。在本地运行模式下，您的研究笔记、答辩提纲、草稿思路 100% 留存在您个人的电脑硬盘中，绝不上传至任何第三方商业云端服务器。
3. **署名与致谢**：
   引用本知识库中相关学者学说观点撰写学术论文时，请务必在正文与脚注中严格遵守法学学术规范，规范引用学者原发期刊文献。

---

<div align="center">

**法脉 LexTrace · 驱动法学研读与学术写作的数字化跃迁**

<sub>Developed with Academic Rigor & Engineering Excellence · Designed for Legal Scholars</sub>

</div>
