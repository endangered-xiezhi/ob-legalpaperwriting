---
type: daily_ip_jurisprudence_corpus
day: 1
topic: "AIGC作品性：客观结果还是人类创作过程"
date: 2026-08-17
status: completed
language: zh-en
source_scope: "七大专题正式目录 + 王迁知产教程重构版 + 官方法源校核"
---

# Day 01｜AIGC 作品性：客观结果还是人类创作过程？

> [!abstract] 今日命题
> AIGC 可版权性真正争议的不是“机器能不能产出漂亮内容”，而是：**作品资格能否仅由结果的外观决定，还是必须存在能够归因于自然人的创作行为；如果必须，人对最终表达的控制和贡献应达到何种程度？**

## 0. 材料定位与法源校核

### 本地材料

- 专题入口：[[知识产权/研究工作台/七大专题/00_七大专题研究工作台]]
- 快速入门：[[知识产权/研究工作台/七大专题/01_AIGC可版权性_快速入门]]
- 学说全景：[[知识产权/研究工作台/七大专题/01_AIGC可版权性_学说争议全景]]
- 六阶段详版：[[知识产权/研究工作台/七大专题/01_AIGC_六阶段逻辑合并样稿]]
- 制度基础：[[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体]]、[[法书/03王迁-知产教程-重构版/著作权法✅/05著作权主体和著作权的归属]]、[[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅]]

### 现行法校核（截至 2026-08-17）

1. 《著作权法》第 3 条将作品界定为文学、艺术和科学领域内，具有独创性并能以一定形式表现的智力成果；第 11 条规定“创作作品的自然人是作者”。现行法没有专门规定 AIGC 输出的作品性或 AI 作者资格。[中国人大网：《中华人民共和国著作权法》](https://www.npc.gov.cn/c2/c30834/202011/t20201119_308796.html)
2. 现行《著作权法实施条例》第 3 条将“创作”界定为直接产生作品的智力活动。2026 年 7 月公布的修订草案征求意见稿拟将该定义移至第 2 条，并继续排除组织、咨询、提供物质条件及其他辅助工作；该草案尚非生效法。[现行实施条例](https://xzfg.moj.gov.cn/law/download?LawID=935&type=pdf)；[国家版权局：2026 年修订草案征求意见稿](https://www.ncac.gov.cn/xxfb/ywxx/202607/t20260709_998362.html)
3. 详版 Stage 4 将现行法的作品定义误标为“第 2 条”；正确条文是第 3 条。该处不影响专题的理论结构，但正式面试中不应沿用错误条号。
4. 比较法上，美国版权局 2025 年报告认为：纯 AI 生成材料不受版权保护；只有当人决定了足够的表达性要素，或者对输出作了具有创造性的选择、编排或修改时，才可能保护人的贡献；单纯提示通常不足。该立场仅作比较材料，不是中国法规则。[U.S. Copyright Office, Copyright and Artificial Intelligence, Part 2](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf)

---

## 1. Core Institution & Terminology｜核心制度与术语

| 中文制度／知识点    | 规范含义                                               | Precise English Terminology                                    |
| ----------- | -------------------------------------------------- | -------------------------------------------------------------- |
| 作品          | 具有独创性并能以一定形式表现的文学、艺术或科学领域智力成果；“像作品”并不自动完成作者与创作来源判断 | work; copyrightable work                                       |
| 作品性／可版权性    | 某项成果是否跨过著作权客体门槛                                    | copyrightability                                               |
| 创作行为        | 直接产生作品表达的智力活动；组织、投资、提供设备或一般性意见通常不是创作               | act of authorship; creative act                                |
| 人类作者性       | 著作权原则上保护可归因于人的创作，而不是自然现象、动物行为或纯机器自主输出              | human authorship                                               |
| 作者          | 实施创作并使作品产生的自然人；法人作品是法定拟制，不能反向证明无需人的创作事实            | author; legal attribution of authorship                        |
| 独创性         | “独”指独立完成而非抄袭；“创”指存在最低程度的智力选择和安排                    | originality; independent creation plus a modicum of creativity |
| 最低限度创造性     | 不要求艺术高度、质量或新颖性，但必须存在真实而非机械的表达选择                    | minimal creativity; a modicum of creativity                    |
| 思想／表达二分     | 主题、构思、需求和风格不受保护；具体文字、构图、线条、色彩等表达才可能受保护             | idea–expression dichotomy                                      |
| 表达性要素       | 能够具体承载作者选择的用词、结构、构图、光影、色彩、造型等要素                    | expressive elements                                            |
| 作品语言        | 不同作品类型用以形成表达的媒介性符号，例如文字作品的措辞、美术作品的线条和色彩            | medium-specific expressive language                            |
| 可归因的人类表达贡献  | 人的选择能够从操作记录映射到最终输出中的具体表达，而非只有事实因果或审美偏好             | attributable human expressive contribution                     |
| 创作控制        | 人能够设定、选择、修正并固定最终表达的重要特征；不等于控制每个像素                  | creative control; sufficient control over expressive elements  |
| 单回合生成／多回合迭代 | 一次提示后随机输出，与围绕中间结果进行方向明确的连续选择和修改                    | single-pass generation; iterative generation                   |
| 版本链／生成溯源记录  | 提示词、参数、种子值、中间版本、局部重绘和后期修改形成的证据链                    | version history; provenance trail                              |
| 薄版权         | 作品门槛可以较低，但保护只覆盖人的可识别贡献，不扩张到思想、风格和机器自动部分            | thin copyright; narrow scope of protection                     |
| 公有领域        | 不满足作品要件或保护期届满的表达资源原则上可供公众自由使用                      | public domain                                                  |

### 1.1 王迁教程具体知识点索引｜Targeted Reading Map

下面只列本争议真正会用到的知识点。建议按“客体门槛 → 创作行为 → 独创性 → 表达边界 → 作者 → 正当性”阅读，而不必泛读整章。

#### A. 作品成立与创作行为

| 基础知识 | 为什么与 AIGC 直接相关 | 王迁教程具体入口 |
|---|---|---|
| 作品定义的四个要件 | 确定 AIGC 首先面对的是“智力成果、表达、领域、独创性”的客体门槛 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#1.1 法定定义的四个要件\|1.1 法定定义的四个要件]] |
| 人类智力成果 | 回答自然现象、动物行为、机器自主生成为什么不能仅凭外观成为作品 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#1.2 人类智力成果\|1.2 人类智力成果]] |
| 外在表达 | 区分用户头脑中的构思、提示词表达与最终图像表达 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#1.3 可被客观感知的外在表达\|1.3 可被客观感知的外在表达]] |
| 独创性总标准 | 建立“独立完成＋最低创造性”的基本公式 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#1.5 独创性：核心要件\|1.5 独创性：核心要件]] |
| 创作行为 | 判断提示、点击、筛选、局部重绘中哪些属于直接产生表达的智力活动 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#2.1 创作的核心标准\|2.1 创作的核心标准]] |
| 生成式 AI 专题 | 直接阅读王迁对“提示词只是要求”“相同提示产生不同结果”“摄影类比”的分析 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#2.2 生成式人工智能内容 ⭐⭐⭐\|2.2 生成式人工智能内容]] |

#### B. 独创性与表达边界

| 基础知识 | 为什么与 AIGC 直接相关 | 王迁教程具体入口 |
|---|---|---|
| “独”：独立创作 | 结果与既有作品不同，不等于该差异来源于用户本人 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#3.1 "独"的含义：独立创作\|3.1 “独”的含义]] |
| “创”：智力创造性 | 判断人的选择是否超出机械操作、随机接受和惯常方案 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#4.1 "创"的含义：智力创造性\|4.1 “创”的含义]] |
| 智力创作空间 | 分析用户是否面对多种表达可能，并实际作出自由选择 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#4.2 智力创作空间\|4.2 智力创作空间]] |
| 反对“额头流汗” | 防止把提示词长度、生成轮次、订阅费用和劳动时间直接等同于作品性 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#4.3 "额头流汗"标准的批判 ⭐⭐\|4.3 “额头流汗”标准的批判]] |
| 质量、价值与创造性分离 | 防止用“输出很精美、很畅销”证明人的独创性 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#4.4 "创"与成果质量、价值无关\|4.4 成果质量、价值与创造性无关]] |
| 思想／表达二分 | 判断提示词是在提出题材、风格和需求，还是已经形成可归因的具体表达 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#6.1 思想表达二分法\|6.1 思想表达二分法]] |
| 为什么不保护思想 | 理解保护提示中的抽象构思为何会增加交易成本并封锁后续创作 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#6.2 为什么不保护思想？\|6.2 为什么不保护思想]] |
| 思想与表达的分界 | 用具体程度和抽象层级判断跨媒介提示是否进入图像表达 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#6.3 思想与表达的分界线 ⭐⭐\|6.3 思想与表达的分界线]] |

#### C. 作者、摄影类比与制度正当性

| 基础知识 | 为什么与 AIGC 直接相关 | 王迁教程具体入口 |
|---|---|---|
| 摄影作品的独创性来源 | 检验“AI 是新相机”的类比：取景、光线、时机和后期为何构成人的表达选择 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#14.1 摄影作品\|14.1 摄影作品]] |
| 自然人作者 | 现行制度把作者连接到“直接产生作品”的自然人创作事实 | [[法书/03王迁-知产教程-重构版/著作权法✅/05著作权主体和著作权的归属#2.1 自然人作者\|2.1 自然人作者]] |
| 法人作者拟制 | 法人可以被视为作者，但前提仍是存在人的创作，不能用归属拟制填补创作缺失 | [[法书/03王迁-知产教程-重构版/著作权法✅/05著作权主体和著作权的归属#2.2 视为作者的法人或非法人组织\|2.2 视为作者的法人或非法人组织]] |
| 对最终表达的实质性贡献 | 可类比理解：只有对最终表达作出独创贡献者，才有作者资格 | [[法书/03王迁-知产教程-重构版/著作权法✅/05著作权主体和著作权的归属#（二）合作事实：实质性贡献 ⭐⭐⭐\|合作事实：实质性贡献]] |
| 劳动自然权及其局限 | 解释“我付出了劳动，所以我应拥有输出”为什么不足以成立排他权 | [[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#3.1 劳动自然权学说详解\|3.1 劳动自然权学说]] |
| 人格学说 | 说明作者资格为何要求表达与人的意志、判断和人格存在联系 | [[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#3.2 人格学说详解 ⭐⭐\|3.2 人格学说]] |
| 功利主义 | 检验赋权是否真的增加人类创作，以及排他权造成的社会成本 | [[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#3.3 功利主义学说详解 ⭐⭐⭐\|3.3 功利主义学说]] |
| 利益平衡 | 把创作者激励、公众获取、后续创作和权利拥堵放入同一框架 | [[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#4.1 利益平衡机制 ⭐⭐⭐\|4.1 利益平衡机制]] |
| 技术改变成本结构 | 解释为何 AI 技术既可能改变创作方式，也可能打破旧有保护平衡 | [[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#4.2 技术发展对著作权制度的影响 ⭐⭐⭐\|4.2 技术发展对著作权制度的影响]] |

---

## 2. Jurisprudential Controversy Analysis｜法哲学争议分析

### 2.1 真正的争点：著作权保护“有创意的结果”，还是保护“人的创作行为”？

严格过程说与客观结果说的分歧，表面上是独创性判断方法不同，实质上是对著作权正当性的不同理解。客观结果说把作品视为一种具有独立存在的客体：只要输出表现出最低程度的表达差异，作品性即可成立，作者及归属另行解决。严格过程说则认为，作品不是任何稀有、美观或具有市场价值的信息产品；它是法律为了人的创作而设立的规范资格。若没有自然人的创作来源，仅凭结果外观确权，著作权就会从“激励和承认人的表达”转化为“奖励机器制造的稀缺结果”。

王迁教程中的制度链支持后一路径：作品须是智力成果，独创性须包含独立创作与最低创造性，作者是创作作品的自然人，创作又是直接产生作品的智力活动。这四个环节不宜被完全割裂。**客体与主体可以分步审查，但不能彼此失去规范联系**：如果一个输出成为作品，却没有任何人对其中的表达负责，作品资格就缺少权利来源；再以投资、平台控制或合同便利指定权利人，容易把著作权降格为一种产业性收益分配工具。

### 2.2 私权基础：贡献原则，而不是因果原则或“额头流汗”

AIGC 用户当然是结果产生链条中的原因：他选择模型、输入提示、点击生成、筛选结果，甚至为订阅服务付费。但私法上的因果参与不等于著作权法上的创作贡献。委托人提出主题、投资者提供资金、编辑提出方向，均可能是作品得以产生的必要条件，却不因此成为作者。若以“没有用户就没有结果”为确权理由，著作权会变成广义的不当得利法：凡对价值产生作出投入者都可要求排他控制。这与教程反复拒绝的“劳动投入即权利”或“额头流汗”逻辑相同。

因此，应采取**可归因的表达贡献原则**：法律所保护的不是用户投入了多少劳动，而是其自由选择是否进入了最终表达。提示词长度、迭代轮数、参数数量和筛选次数都只能作为证据；它们必须进一步说明，用户决定了哪些具体的构图、光线、人物位置、措辞或结构。简单地在多个机器结果中挑选“最好看”的一张，通常只显示审美判断；围绕同一中间结果进行局部重绘、方向明确的修正和人工后期编辑，则更可能使人的选择固定为表达。

### 2.3 思想／表达二分：提示词的跨媒介断裂

“雨夜中的旧书店”“暖色灯光”“孤独的红伞人物”可以是具体构思，但仍可能只是对美术作品提出的内容要求。文字提示何时跨过思想而成为对图像表达的参与，不能由提示词是否复杂单独决定。真正的标准应是**稳定映射与可修正性**：用户能否让这些文字选择稳定地对应到输出中的构图、线条、色彩和空间关系；出现偏差时，用户能否针对具体表达单元作定向修正；最终版本能否显示一条从人的选择到表达结果的可追踪路径。

这也解释了摄影类比为何既有力量又有限。摄影师不控制每一个光子，也可能利用偶然瞬间，但他通常在按下快门前后直接决定视角、取景、曝光、时机和后期处理。AIGC 用户同样无须控制每个像素；然而，他至少要证明自己承担了与摄影师相当的规范角色——不是只提出主题，而是对成品的重要表达特征作出足以归责的选择。**争论的焦点不是人工执行还是机器执行，而是人是否对表达承担了作者意义上的决定责任。**

### 2.4 人格论与功利主义的张力

从人格论看，作品保护的正当性来自表达与人的意志、判断和人格之间的联系。纯机器输出缺少这种联系；把权利配置给点击者或投资者，会使“作者”成为方便分配收益的空壳。但人格论也不能被解释为只有亲手落笔才算创作，否则摄影、导演、数字编辑和其他间接创作都会被不合理排除。更适当的理解是：人的人格必须能够通过可识别的表达选择显现，而不要求人完成全部物理固定。

从功利主义看，也不能因为 AIGC 有市场价值就当然赋权。著作权是以社会成本换取创作激励的制度：排他权会提高后续使用、检索、许可和诉讼成本。AIGC 具有低边际成本、海量供给和相似输出概率，如果每个自动结果都获得完整版权，可能造成权利拥堵，挤压公有领域，并允许平台通过规模化生成占据表达空间。反之，一概否定又会遗漏真实的人机协作。因此最合比例的制度不是“全有或全无”，而是**贡献敏感的薄版权**：只保护能够证明的人类表达增量；机器自动生成、思想、风格、惯常元素和公共素材继续自由流通。

### 2.5 推荐立场：过程相关，但不要求像素级控制

我的结论是：**作品性判断必须保留人类创作这一规范门槛，但应以可归因的表达贡献而非物理执行或绝对可预测性来识别人类创作。**审查顺序如下：

1. **切分客体**：区分第一轮纯生成图、多轮迭代版本、人工后期完成图和提示词本身。
2. **识别人类行为**：列出提示、参数、筛选、局部重绘、编排和后期编辑，但不预设这些行为都是创作。
3. **完成表达映射**：判断人的选择是否进入最终作品的具体表达，而不是只停留在主题、风格、需求或一般审美偏好。
4. **审查最低创造性**：被映射的表达是否体现自由选择，而非机械转换、随机接受或惯常方案。
5. **限定保护范围**：仅保护可归因的人类贡献；贡献较薄，权利范围亦应较薄。
6. **分配举证责任**：主张权利者应提供版本、参数、提示和修改记录。日志证明操作事实，但仍须由法院完成表达归因这一规范判断。

适用于“雨夜书店”案例：第一轮简单提示形成的图像通常不足以证明用户创作；第二至第六轮只有在版本链显示构图、灯光、人物位置等被连续而定向修正时，才增强作者性；最后由用户直接完成的局部重绘和图像编辑最容易获得保护。即便最终成品构成作品，权利也不当然覆盖全部机器生成细节。

### 2.6 本争议涉及内容全链条｜Complete Issue Map

| 审查节点 | 核心问题 | 推荐处理 | 典型误区 |
|---|---|---|---|
| 1. 客体切分 | 讨论的是首轮图、多轮图、后期图，还是提示词？ | 分版本、分表达单元判断 | 把所有阶段混成一个“AIGC 作品” |
| 2. 人类作者性 | 是否存在自然人的创作事实？ | AI 不作为作者；继续寻找人的表达贡献 | AI 不是作者，所以用户自动是作者 |
| 3. 创作行为 | 提示、参数、筛选和修改中哪些直接产生表达？ | 区分创作、辅助、组织、投资和机械操作 | 有因果参与或劳动投入就等于创作 |
| 4. 思想／表达 | 用户给出的是主题需求，还是具体表达？ | 检验跨媒介选择能否稳定映射到结果 | 提示词越长越接近表达 |
| 5. 独创性 | 被映射的人类贡献是否独立且有最低创造性？ | 审查选择空间、自由取舍与非机械性 | 结果新颖、美观或有价值即独创 |
| 6. 控制程度 | 是否必须预测每个像素？ | 不要求绝对控制，但要求对重要表达特征具有可归责的决定作用 | 黑箱存在即永远无作者；或使用工具即当然有作者 |
| 7. 证据 | 如何证明人的选择进入最终表达？ | 版本链、提示、参数、种子、局部重绘与后期文件相互印证 | 日志存在即自动证明独创性 |
| 8. 作者与归属 | 谁作出贡献，财产权又归谁？ | 先认作者，再依职务、委托或合同处理财产权 | 用合同约定反推非作品变成作品 |
| 9. 保护范围 | 成立作品后保护整个输出还是人的部分？ | 贡献敏感的薄版权；过滤思想、风格、惯常及机器部分 | 作品成立即获得对全部画面和风格的控制 |
| 10. 制度出口 | 不构成作品是否必须另设权利？ | 原则上进入公有领域；合同、竞争法、邻接权分别证明自身要件 | “没有版权”就等于“必须另设排他权” |

---

## 3. English Jurisprudential Analysis & Interview Corpus｜英文学理分析与面试语料

### 3.1 Result-Oriented Copyrightability v. Process-Sensitive Authorship

The controversy between the result-oriented and process-sensitive approaches is ultimately a dispute about the normative object of copyright. A result-oriented theory treats the work as an autonomous informational object: once an output displays sufficient expressive distinctiveness, copyrightability is established and authorship may be allocated at a later stage. A process-sensitive theory rejects that separation when it becomes absolute. On this view, a work is not merely an aesthetically impressive or commercially valuable artefact; it is a legal category constructed around acts of human authorship. If an output qualifies solely because it resembles a conventional work, copyright risks becoming a system for privatizing machine-produced scarcity rather than a system for recognizing human expression.

The preferable position is that copyrightability and authorship may be examined separately but must remain normatively connected. The existence of a work should presuppose an intelligible source of original expression. Otherwise, the law would first recognize an ownerless copyright object and then assign it to a user, developer, or investor for reasons of convenience. Such an allocation would confuse the justification of an entitlement with the subsequent distribution of that entitlement. Ownership rules can determine who holds copyright after authorship has been established; they should not manufacture authorship where no human creative contribution exists.

### 3.2 Contribution, Causation, and the Rejection of a Sweat-of-the-Brow Theory

An AIGC user is undoubtedly a factual cause of the output. The user chooses a model, supplies prompts, pays for access, initiates generation, and selects a preferred result. Yet factual causation is not equivalent to authorship. A commissioner, financier, editor, or technical assistant may be indispensable to the production of a work without becoming its author. Copyright is therefore governed by a contribution principle rather than a broad but-for causation principle. What matters is not whether the output would have existed without the claimant, but whether the claimant made original choices that became part of its protected expression.

This distinction also prevents the revival of a sweat-of-the-brow theory. Long prompts, repeated attempts, substantial expense, and extensive time may demonstrate effort, but effort does not by itself create copyright. The claimant must identify a legally relevant transformation from conduct into expression. Iterations acquire evidentiary weight only when they reveal a directed sequence of expressive decisions; selection matters only when it involves creative arrangement or modification rather than the passive acceptance of an attractive machine-generated result.

### 3.3 The Cross-Media Gap Between Ideas and Expression

Prompts expose a difficult cross-media problem within the idea–expression dichotomy. A phrase such as “an old bookshop in the rain, lit by warm lamps, with a solitary figure under a red umbrella” may be highly specific as an idea, yet still function merely as a request addressed to the system. The legal question is not whether the prompt is detailed, poetic, or laborious. It is whether the user’s verbal choices can be mapped onto concrete visual elements—such as composition, spatial relations, lighting, colour, and form—in a sufficiently stable and attributable manner.

A useful test combines stable mapping with directed revisability. First, the user’s instructions should correspond to identifiable features of the output rather than merely influence an unpredictable probability distribution. Second, when the system deviates from the intended design, the user should be able to correct particular expressive features through directed iteration, inpainting, compositional constraints, or post-editing. This test does not require perfect predictability. It asks whether the user occupies the normative position of an author who determines important expressive features, rather than that of a client who merely communicates a desired theme to an independent producer.

### 3.4 Personality Theory, Utilitarianism, and the Private-Law Balance

Personality theory explains why human authorship remains important. Copyright protects more than economically valuable information; it recognizes a relationship between expression and a person’s will, judgment, and creative identity. Purely machine-determined output lacks that relationship. However, personality theory should not be reduced to a requirement of manual execution. Photographers, film directors, and digital artists frequently create through complex tools and collaborative processes. The relevant question is whether human personality is manifested through identifiable expressive choices, not whether the person physically fixed every element.

Utilitarian analysis points in the same direction but for different reasons. Exclusive rights are justified only when their incentive benefits exceed the social costs of restricted access, licensing, enforcement, and follow-on creation. AIGC dramatically lowers the marginal cost of producing expressive material and can generate enormous volumes of similar outputs. Full copyright in every automated result could create rights congestion and allow industrial-scale actors to occupy large areas of the expressive commons. Yet a categorical denial of protection would disregard genuine human–machine collaboration. A contribution-sensitive, narrowly tailored entitlement therefore offers a more proportionate balance.

### 3.5 Preferred Doctrinal Framework: Attributable Expressive Contribution

My preferred approach retains human authorship as a normative threshold but defines it through attributable expressive contribution. The court should first separate the relevant objects: the initial output, later iterations, human modifications, and the prompt itself. It should then identify the claimant’s acts and determine whether those acts concern unprotected ideas or protected expression. The decisive step is to map the claimant’s choices onto specific expressive features in the final version and ask whether those choices display at least a minimal degree of creativity.

Protection, if established, should remain commensurate with the proven contribution. Human-authored modifications, creative arrangements, and demonstrably controlled expressive features may receive copyright, while machine-determined details, styles, themes, standard elements, and public-domain material remain free. The claimant should bear the initial burden of producing prompts, version histories, parameters, control images, and editing files. These records prove what the claimant did; they do not eliminate the court’s separate responsibility to decide whether that conduct amounted to authorship.

### 3.6 Four-Paragraph Interview Answer｜四段式口述成稿

The copyrightability of AI-generated content should not be reduced to the superficial question of whether the output looks creative. Copyright does not operate as a general reward for novelty, beauty, effort, or market value. Its basic institutional function is to recognize and regulate human acts of authorship. Accordingly, the decisive inquiry is whether a natural person made original expressive choices that can be attributed to the final output. A visually impressive image may therefore remain outside copyright if its expressive elements were determined entirely by the model rather than by a human author.

The strongest argument for a process-sensitive approach is that copyrightable subject matter and authorship cannot be completely severed. They may be examined in separate analytical stages, but a “work” must still have a normatively intelligible source of authorship. If objective appearance alone were sufficient, wholly automated outputs could become protected works before any human creator had been identified. The law would then be forced to allocate exclusive rights on the basis of investment, platform control, or contractual convenience. That would transform copyright from a law of authorship into a general law against free riding.

At the same time, human authorship should not be equated with pixel-by-pixel control or physical execution. A photographer does not control every feature of reality, yet may still author a photograph through choices concerning framing, timing, lighting, exposure, and post-production. The proper test for AIGC should therefore be attributable expressive contribution. Prompts, parameters, selection, and repeated iterations are evidentiary factors, not legal conclusions. They matter only insofar as they establish a traceable connection between the user’s choices and particular expressive elements in the final output.

My preferred solution is a contribution-sensitive model of thin copyright. Simple prompting followed by the passive acceptance of a random output will ordinarily be insufficient. By contrast, directed iteration, inpainting, compositional control, and creative post-editing may demonstrate authorship when they fix the user’s choices in the final expression. Even then, the scope of protection should be commensurate with the human contribution. Ideas, styles, standard elements, and machine-determined details should remain available to the public. This approach preserves the human foundation of copyright while avoiding both technological discrimination and the over-privatization of the expressive commons.

### 3.7 Reusable Jurisprudential Phrases｜可复用学理表达

- **the normative object of copyright** — 著作权保护的规范对象
- **a normatively intelligible source of authorship** — 在规范上可解释的作者性来源
- **to distinguish factual causation from normative authorship** — 区分事实因果与规范作者性
- **ownership rules cannot manufacture authorship** — 权利归属规则不能凭空制造作者性
- **evidentiary factors rather than legal conclusions** — 证据因素，而非法律结论
- **a traceable connection between human choices and final expression** — 人的选择与最终表达之间可追踪的联系
- **protection should be commensurate with the proven contribution** — 保护范围应与已证明的贡献相称
- **a contribution-sensitive model of thin copyright** — 贡献敏感的薄版权模式
- **rights congestion and the over-privatization of the expressive commons** — 权利拥堵与表达公域的过度私有化
- **technological neutrality without collapsing commissioning into authorship** — 在不把委托误作创作的前提下保持技术中立

### 一句立场句｜One-sentence position

> I would retain human authorship as a normative threshold, but define it through attributable expressive contribution rather than physical execution or absolute control over every detail.

---

## 4. Future Testing Angle｜未来面试追问

### Question 1

**中文：**如果摄影师不需要控制每一个光影细节，为什么 AIGC 用户必须能够预测具体输出？请提出一个既不歧视新技术、又不会把“委托要求”误认为创作的标准。

**English:** If a photographer need not control every detail of light and reality, why should an AIGC user be required to predict the precise output? Formulate a standard that is technologically neutral without collapsing mere commissioning into authorship.

### Question 2

**中文：**假设某个 AIGC 输出具有高度独特的客观表达，但没有任何自然人能够证明对其具体表达作出贡献。它应进入公有领域，还是应将权利拟制给用户、开发者或投资者？你的选择如何分别回应人格正当性、激励缺口与权利拥堵？

**English:** Suppose an AIGC output is objectively distinctive, yet no natural person can demonstrate a contribution to its specific expression. Should it enter the public domain, or should the law assign rights by legal fiction to the user, developer, or investor? How would your answer address personality-based legitimacy, incentive failure, and rights congestion?

---

## 5. 复习抓手

- **最强反方**：王迁的过程论——作品样外观不能替代人的创作行为。
- **最强修正**：蒋舸的最低创造性与宽进宽出——不能因为工具先进而抹去真实的人类贡献。
- **事实工具**：崔国斌的初始输入／后续调整、单回合暗箱／多回合线性改进。
- **最终标准**：不是“提示了几次”，而是“人的选择能否对应并固定到最终表达”。
- **制度出口**：符合门槛则薄保护；不符合门槛原则上进入公有领域，另有合同、竞争法或其他制度问题时分别审查，不自动创设排他权。
