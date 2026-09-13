---
type: daily_ip_jurisprudence_corpus
day: 5
topic: "商业数据保护：确权、控制还是行为规制"
date: 2026-08-17
status: completed
language: zh-en
source_scope: "专题04 + 王迁知产教程重构版相邻知识点 + 官方法源校核"
---

# Day 05｜商业数据保护：确权、控制还是行为规制

> [!abstract] 今日命题
> 数据具有价值，并不回答谁对什么数据享有何种排他范围。真正的制度选择是：**以单一数据所有权降低交易不确定性，还是以来源、粒度、控制、贡献和使用场景分配利益，并只禁止不正当获取、实质替代与封锁竞争。**

> [!info] 系列位置
> 本页处理公开及半公开商业数据的保护结构。秘密数据和模型参数见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 09 - 数字商业秘密：替代成本、合理措施与动态退出\|Day 09]]；一般条款何时补充见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 06 - 一般条款的边界：补充保护还是准知识产权\|Day 06]]；总分流见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/01 - 非版权专题总图：数据、竞争法、商标与商业秘密\|非版权专题总图]]。

## 0. 材料定位与现行法校核

### 本地材料

- 快速入门：[[知识产权/研究工作台/七大专题/04_商业数据保护_快速入门]]
- 学说全景：[[知识产权/研究工作台/七大专题/04_商业数据保护_学说争议全景]]
- 六阶段详版：[[知识产权/研究工作台/七大专题/04_商业数据保护_六阶段逻辑合并]]
- 制度基础：[[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体]]、[[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅]]、[[法书/03王迁-知产教程-重构版/专利法✅/9专利法律制度概述]]

### 现行法底线（截至 2026-08-17）

1. 2025 年修订的《反不正当竞争法》已于 2025 年 10 月 15 日施行。第 13 条第 3 款禁止经营者以欺诈、胁迫、避开或破坏技术管理措施等不正当方式，获取、使用其他经营者合法持有的数据，损害其合法权益并扰乱竞争秩序；这是一项**行为规制**，不是一般数据所有权条款。[《反不正当竞争法（2025 年修订）》](https://www.cnipa.gov.cn/art/2026/5/20/art_104_206437.html)
2. 最高人民法院已明确，2025 年 10 月 15 日后相关数据行为应适用第 13 条第 3 款及相关规定。指导性案例同时展示三条边界：大规模搬运并实质替代平台服务可能不正当；经用户授权合理转移其数据可能正当；依法采集企业公开数据并加工成产品、未损害企业权益的，不应仅因原始来源而承担责任。[最高人民法院第 47 批指导性案例](https://ipc.court.gov.cn/zh-cn/news/view-4588.html)
3. 著作权只可能保护具有独创性的选择或编排，以及数据库中各自构成作品的内容；事实、单条数据和无独创性的机械集合不因此整体被垄断。
4. 未公开数据若满足具体秘密点、不为公众所知悉、具有商业价值并采取相应保密措施，应优先进入商业秘密规则；不得为降低举证门槛而把所有后台数据当然视为“数据权”。
5. 因此，合法持有、合同控制、技术控制、商业秘密、汇编作品和数据竞争利益是不同层次。**登记、入表、质押或交易可以证明可管理、可估值，却不当然证明对世排他权。**

---

## 1. Core Institution & Terminology｜核心制度与术语

| 中文制度／知识点 | 精确含义 | Precise English Terminology |
|---|---|---|
| 数据权益 | 对数据相关利益的概括称谓，本身不预设所有权或绝对权 | data-related interests; data interests |
| 数据所有权／确权 | 将数据界定为可对世排他的客体并确定权利主体 | data ownership; allocation of proprietary entitlements |
| 控制论 | 保护事实控制和基于控制形成的利益，但不当然创造新物权 | control-based approach; protection of factual control |
| 关系性配置 | 按来源者、处理者、平台、用户和商户的关系分配访问、使用、收益等权能 | relational allocation of data entitlements |
| 权能束 | 将访问、复制、分析、许可、收益、删除、携带等能力分别配置 | bundle of entitlements |
| 合法持有 | 数据的取得、保存与处理具有合法基础；不是无限排他权的同义词 | lawful possession or lawful holding of data |
| 数据粒度 | 单条数据、数据集合、结构化数据库、衍生数据产品等不同分析单位 | data granularity |
| 来源数据 | 由个人、商户、设备或公共活动直接产生的数据 | source data; originating data |
| 衍生数据／数据产品 | 经清洗、标注、聚合、分析或模型计算形成的新数据或产品 | derived data; data product |
| 数据集合经营利益 | 对合法组织、加工、维护的数据集合形成的竞争性利益 | competitive interest in a data collection |
| 数据专款 | 《反不正当竞争法》第 13 条第 3 款针对不正当取用数据的特别行为规则 | specific unfair-competition rule for data misappropriation |
| 实质性替代 | 被诉利用使用户无需使用原产品或服务即可获得其核心价值 | substantial substitution |
| 数据搬运 | 大规模复制并再提供他人数据集合，通常缺乏独立价值增量 | data scraping and wholesale republication; data appropriation |
| 价值增量 | 使用者通过清洗、分析、验证或新功能作出的独立贡献 | value added; transformative processing |
| 技术管理措施 | 用于管理访问、调用、复制、频率或范围的技术限制 | technical management measures; access controls |
| 数据可携权 | 数据主体将特定数据转移给自己或另一服务的请求权 | right to data portability |
| 必要数据／必需设施 | 竞争者开展有效竞争不可合理复制或替代的关键数据资源 | essential data; essential-facility doctrine |
| 弱排他权 | 客体、行为、期限与例外均受限的专门排他结构 | limited exclusionary right; weak proprietary right |
| 公开换权利 | 以法定有限保护诱导经营者披露数据，减少过度保密 | disclosure-for-rights bargain |
| 禁止权追及 | 来源者利益不当然随数据追及所有合法加工者和下游产品 | non-tracing principle for data entitlements |

### 1.1 八项事实核验

`数据是什么 → 粒度如何 → 谁贡献什么 → 是否合法持有 → 如何获取 → 如何使用 → 是否替代及损害竞争 → 是否存在开放或携带利益`

---

## 2. 王迁教程具体知识点｜Targeted Reading Map

> [!warning] 对应范围
> 教材没有独立数据法章节。下表链接的是可直接约束数据保护论证的知识点，而非把著作权或专利规则机械类推为数据权。

| 本专题基础知识 | 在数据问题中的具体用法 | 王迁教程入口 |
|---|---|---|
| 劳动自然权学说及其局限 | 投入、清洗和维护成本可以说明激励需求，却不能单独推出排他权 | [[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#3.1 劳动自然权学说详解\|劳动自然权学说]]、[[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#劳动自然权学说的问题\|劳动学说的问题]] |
| 汇编作品的构成 | 数据库仅在内容选择或编排体现独创性时构成汇编作品 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#17.1 汇编作品的定义\|汇编作品定义]]、[[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#17.2 汇编作品的独创性\|选择与编排的独创性]] |
| 汇编保护范围 | 保护选择编排，不把其中事实、数据或他人作品一并据为己有 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#17.3 汇编作品的保护范围\|汇编作品保护范围]] |
| 数据库特殊权 | 理解“实质性投资＋禁止提取主要部分＋有限期限”的设权方案 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#17.4 数据库的特殊保护 ⭐\|数据库特殊保护]] |
| 数据库政策争议 | 比较投资激励与数据流动、科研、后续创新的社会成本 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#17.5 🔍 数据库保护的政策争议\|数据库保护政策争议]] |
| 技术措施的独立性质 | 反爬措施可能影响获取手段评价，但不能把不受保护的数据自动变为版权客体 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#3.4 规避技术措施行为的性质 ⭐⭐\|规避技术措施的性质]] |
| 技术控制与合法使用冲突 | 防止平台借访问控制架空法定例外、公共领域或正当数据利用 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#3.6 技术措施保护与合理使用的冲突 ⭐⭐⭐\|技术措施与合理使用]] |
| 专利与商业秘密的选择 | 对照“公开换法定排他”与“保持秘密换有限保护”的制度交换 | [[法书/03王迁-知产教程-重构版/专利法✅/9专利法律制度概述#5.1 两种保护路径的差异 ⭐⭐⭐\|专利与商业秘密差异]] |

---

## 3. Jurisprudential Controversy Analysis｜法哲学争议分析（中文）

### 3.1 “数据有价值”不是权利论证，而只是制度问题的起点

将数据价值直接翻译为所有权，隐含了劳动自然权的跳跃：因为平台投入采集、清洗和存储，所以平台应排除他人。但市场中的许多有价值利益——客户注意力、商业机会、事实、方法和技能——并不因此成为绝对权客体。设权还会把他人的行为自由转化为普遍义务，故必须说明客体是否可界定、第三人能否获得公示、期限如何、例外为何以及交易成本是否真的下降。

数据尤其不适合“一物一主”的直觉。用户产生行为记录，商户提供交易信息，平台设计字段并完成聚合，处理者再清洗推断；同一数据还可被多人非竞争性利用。单一所有权看似清晰，实际上可能把多方贡献、隐私约束、合同义务和公共利益压缩成一个错误问题。较好的起点是**分解利益而非寻找唯一所有人**。

### 3.2 确权与行为规制代表两种不同的自由结构

专有权以“未经许可原则上不得实施”为基线，优势是降低权利识别和许可谈判成本；代价是把所有市场参与者置于事前许可义务下。行为规制则以自由利用为基线，仅在获取方式、利用规模、实质替代或竞争损害达到阈值时介入。它较少阻断后续创新，但个案事实和执法成本更高。

因此，争议不只是保护强弱，而是错误成本的分配。数据客体尚难稳定界定、来源贡献高度分散、用途快速变化时，过早赋予绝对权会产生反公地、许可堆叠与长期追及；完全依赖个案行为规制又可能让高成本数据库被即时搬运。有限排他权若要成立，必须具有狭窄客体、明确行为、有限期限和强制例外，而不能以“数据权”概念掩盖空白授权。

### 3.3 合法持有只建立受保护利益，不决定保护范围

第 13 条第 3 款要求“其他经营者合法持有的数据”，其功能是排除非法收集者以竞争法主张利益，并确认平台或处理者存在可受保护的经营基础。但合法持有不是所有权证书。它不能证明数据均由平台创造，不能消灭用户和商户的来源利益，也不能说明任何未经同意的取用都会扰乱竞争。

裁判仍须向后分析不正当方式、权益损害与竞争秩序。欺诈身份、突破认证、破坏限流与批量搬运通常增强不正当性；依用户授权转移本人数据、利用公开报价形成独立指数、只取必要少量信息且不替代原服务，则可能属于正常竞争。**合法性是入口，不是结论。**

### 3.4 公开与非公开不是二元开关，关键是可获得性与替代成本

后台数据可因访问限制、合同边界和合理保密措施进入商业秘密；公开网页上的单条事实通常不能仅凭平台声明恢复秘密性。但“条目可见”并不必然意味着结构化集合、历史快照、内部标签、关联关系或算法推断均已公开。应分别识别秘密点及普通业内人员能否以合法方式、合理成本重建。

技术措施同样不是权利开关。登录验证、调用频率、付费层级和反自动化设计可以证明平台划定了访问边界，也能影响获取方式是否不正当；但简单 robots 声明不能把公共事实变成绝对权。措施越接近防止越权进入或系统损害，其规范理由越强；越接近封锁公开信息和排除竞争，其正当性越弱。

### 3.5 “搭便车”必须转译为竞争机制损害

他人节省了收集成本，不能单独证明不正当。模仿、学习和利用公开事实本来就是竞争机制的一部分；竞争者经常通过观察市场降低信息成本。真正需要解释的是：被告是否搬运了足以替代原产品的核心集合，是否破坏数据更新和质量投资的可持续性，是否误导用户数据来源，是否造成系统负担，或者是否阻断用户、商户的自主选择。

实质性替代是重要但非唯一指标。它把“原告受损”与“竞争过程受损”连接起来：若被告以低成本复制全部核心功能，使原告无法回收持续维护成本，干预理由增强；若被告增加验证、分析和新用途，形成新的产品市场，禁止利用反而可能保护既有商业模式免受创新竞争。社会福利分析必须同时计算投资激励、数据流动、消费者便利和市场进入。

### 3.6 衍生产品不应被来源利益无限追及

数据流通的制度价值在于允许不同主体组合信息并创造新知识。若每一个来源者都能对所有推断、指标和模型结果主张持续许可，交易链会累积权利碎片，衍生创新可能因无法穷尽授权而停止。因此，合法来源、实质加工、独立功能和不替代原服务应构成“权利不追及”的强理由。

这不意味着加工能够洗白非法来源。若原始数据通过侵入、欺诈或违反保密义务取得，下游产品的价值增量不能当然消除前端违法。应把来源合法性与产品独立性分两步：前者决定能否进入利用，后者决定来源利益是否继续延伸。

### 3.7 平台投入必须与来源者访问、可携带及市场开放平衡

平台通过组织和维护创造价值，但数据也来自用户、商户与社会交易。绝对平台控制会造成锁定：用户无法转移关系和记录，商户无法复用自身经营信息，新服务无法获得形成有效竞争所需的最低输入。访问权的正当性不是否定平台投入，而是纠正平台同时控制基础设施、规则和数据所形成的结构优势。

开放义务必须分层。个人数据可携带应围绕本人提供或观察所得的可识别数据；商户访问应依合同目的、共同生成和合理信赖确定；竞争法或反垄断强制开放须证明数据不可合理替代、拒绝会排除有效竞争且共享具有技术和安全可行性。公共利益不能变成无限抓取许可，平台投入也不能变成无限封锁理由。

### 3.8 推荐立场：分层保护而非单一确权

1. 先按单条、集合、结构、推断和衍生产品确定数据粒度。
2. 分别识别用户、商户、平台和处理者的来源与增值贡献，不预设唯一所有人。
3. 有独创性选择编排的，保护汇编表达；有具体秘密点的，优先适用商业秘密。
4. 对公开或不满足秘密性的商业数据，依第 13 条第 3 款审查合法持有、获取方式、利用目的、数量、增值、替代及竞争影响。
5. 合法取得并形成独立功能的衍生产品，原则上不受来源利益无限追及。
6. 对可携带、商户访问和必要数据开放分别设置门槛，兼顾隐私、安全、投入回收与市场进入。

### 3.9 分层结论表

| 数据状态 | 优先规则 | 保护重点 | 主要边界 |
|---|---|---|---|
| 单条事实或公共信息 | 原则自由利用＋特定行为规制 | 防欺诈、系统破坏、规模性替代 | 事实不垄断、合理取用 |
| 独创性选择编排 | 汇编作品著作权 | 选择和编排 | 不延及数据事实本身 |
| 具体非公开数据／集合 | 商业秘密 | 秘密性、价值、措施与不当取得 | 独立研发、反向工程、公开退出 |
| 合法组织的公开数据集合 | 数据专款／竞争法 | 非法取用、实质替代、竞争秩序 | 价值增量、用户授权、数据流动 |
| 合法衍生数据产品 | 合同、竞争法及具体知识产权 | 独立投入和新功能 | 不洗白非法来源，也不被无限追及 |

---

## 4. English Jurisprudential Analysis & Interview Corpus｜英文学理分析与面试语料

The first mistake in data law is to move directly from value to ownership. Considerable expenditure on collection, cleaning, and maintenance may establish a need for legal protection, but it does not identify the object, holder, scope, duration, or exceptions of an exclusionary right. Data are often co-produced by users, merchants, platforms, devices, and downstream processors, and they can be used non-rivally by several actors. A single ownership model may therefore conceal rather than resolve the relevant distributional questions. The more defensible starting point is to disaggregate entitlements—access, use, portability, licensing, and revenue—according to contribution, control, and context.

Property and conduct regulation also embody different baselines of freedom. A property rule requires outsiders to obtain permission in advance and may reduce bargaining uncertainty, but it can generate fragmented licences, entry barriers, and the over-protection of facts. Conduct regulation leaves data use presumptively free and intervenes when acquisition is deceptive or technically intrusive, when use substantially substitutes for the original service, or when the competitive process is otherwise impaired. Its disadvantage is greater adjudicative uncertainty. The choice is therefore not simply between strong and weak protection; it is a choice about which type of error the legal system is willing to bear.

Lawful holding should be treated as an entry condition, not as a title deed. It confirms that a platform or processor has a legitimate interest worthy of consideration, while leaving open whether a particular act of scraping or reuse is unfair. Courts should examine the granularity and source of the data, the means of acquisition, the scale and purpose of use, the defendant’s value added, the degree of substitution, and the effects on users and market entry. Technical restrictions are relevant to the fairness of acquisition, but they cannot by themselves convert public facts into private property.

My preferred position is a layered regime. Copyright may protect original selection or arrangement, trade-secret law may protect specifically identified non-public information, and unfair-competition law may restrain improper acquisition and market-substituting appropriation of lawfully held data collections. Lawfully acquired and substantially transformed data products should generally be free from perpetual tracing claims. At the same time, portability and narrowly tailored access duties may be necessary where platform control produces lock-in or excludes effective competition. The governing principle is that value justifies inquiry, not exclusivity; protection should target a defined legal interest and stop at the point where it would suppress legitimate reuse and follow-on innovation.

### Reusable Phrases｜可复用表达

- **value justifies inquiry, not exclusivity** — 价值触发审查，但不自动产生排他权
- **to disaggregate entitlements according to contribution and context** — 按贡献与场景拆分权能
- **different baselines of market freedom** — 不同的市场自由基线
- **lawful holding as an entry condition rather than a title deed** — 合法持有是入口而非权属证书
- **market-substituting appropriation** — 造成市场替代的数据攫取
- **technical control cannot privatize public facts** — 技术控制不能使公共事实私有化
- **a non-tracing principle for substantially transformed products** — 对实质转化产品实行权利不追及
- **to protect investment without freezing the informational inputs of competition** — 保护投入而不冻结竞争的信息投入

### 一句立场句｜One-sentence Position

> I favour a layered, conduct-sensitive regime that protects original structures, genuine secrets, and identifiable competitive interests, while rejecting any inference from commercial value to a general and perpetual property right in data.

---

## 5. Future Testing Angle｜未来面试追问

### Question 1

**中文：**甲平台公开展示商品价格并设置 robots 禁止抓取。乙公司每天少量抓取，结合线下数据制作独立价格指数。请分别从数据专款、技术措施、实质替代和社会福利分析是否构成不正当竞争。

**English:** Platform A publicly displays product prices but prohibits scraping through its robots protocol. Company B collects a limited amount each day and combines it with offline information to produce an independent price index. Analyse the conduct under the specific data rule, technical-control doctrine, substantial substitution, and social welfare.

### Question 2

**中文：**若建立商业数据有限排他权，应如何限定客体、主体、受控行为、期限和例外，才能避免把公共事实和用户贡献永久私有化？

**English:** If a limited exclusionary right in commercial data were introduced, how should its object, holder, controlled acts, duration, and exceptions be designed so that public facts and user contributions are not permanently privatized?

---

## 6. 复习抓手

- **第一句**：数据有价值不等于数据有所有权。
- **八事实**：粒度、来源、贡献、合法持有、获取、使用、替代、开放。
- **三入口**：独创性编排走版权，具体非公开信息走商业秘密，公开集合的不当取用走数据专款。
- **两分开**：合法来源与独立产品分开；技术措施与底层权利分开。
- **竞争法问题**：不是被告是否节省成本，而是其是否扭曲竞争机制或实质替代。
- **开放问题**：用户可携带、商户访问和反垄断开放是三套不同门槛。
