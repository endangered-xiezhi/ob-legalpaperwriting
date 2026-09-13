---
type: daily_ip_jurisprudence_corpus
day: 4
topic: "安全港的功能性改造：具体知情、目标过滤与程序保障"
date: 2026-08-17
status: completed
language: zh-en
source_scope: "专题03 + 专题08交叉部分 + 王迁知产教程重构版 + 官方法源校核"
---

# Day 04｜安全港的功能性改造：具体知情、目标过滤与程序保障

> [!abstract] 今日命题
> 真正的问题不是抽象地“保留还是废除安全港”，而是：**在不设普遍监控义务的前提下，何种具体知识、重复风险和技术能力足以使平台义务从被动删除升级为目标过滤；又应如何用反通知、人工复核和比例原则约束私人算法执法。**

> [!info] 系列位置
> 本页以存在网络用户侵权或已初步证明的输出风险为前提。训练输入见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 02 - 训练数据的版权入口与制度出口|Day 02]]；受保护表达、输出侵权和模型链行为见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 03 - AIGC输出侵权与生成链归责|Day 03]]；共通规则见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/00 - AIGC版权责任链总图：训练、输出与平台|责任链总图]]。

## 0. 材料定位与现行法校核

### 本地材料

- 快速入门：[[知识产权/研究工作台/七大专题/03_平台过滤义务与避风港_快速入门]]
- 学说全景：[[知识产权/研究工作台/七大专题/03_平台过滤义务与避风港_学说争议全景]]
- 六阶段详版：[[知识产权/研究工作台/七大专题/03_平台过滤义务与避风港_六阶段逻辑合并]]
- GAI 交叉专题：[[知识产权/研究工作台/七大专题/08_AIGC输出侵权与责任分配_快速入门]]、[[知识产权/研究工作台/七大专题/08_AIGC输出侵权与责任分配_学说争议全景]]
- 制度基础：[[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任]]、[[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用]]

### 现行法底线（截至 2026-08-17）

1. 《民法典》第 1195 条规定：有效通知应包含侵权初步证据和权利人真实身份信息；服务提供者应转送用户，并依初步证据和服务类型采取必要措施；未及时采取的，就损害扩大部分承担责任。第 1196 条设置用户不侵权声明与恢复机制；第 1197 条处理服务提供者知道或应知而未采取必要措施的连带责任。[中国网信网：《中华人民共和国民法典》](https://www.cac.gov.cn/2020-06/01/c_15925617772683196.htm)
2. 《信息网络传播权保护条例》第 14—17 条规定通知、删除／断链与书面说明机制；第 20—23 条分别对自动接入传输、缓存、信息存储、搜索链接设定赔偿责任限制条件。以信息存储为例，条件包括未改变内容、不知道也无合理理由应知、未从具体内容直接获利、收到通知后删除等。[《信息网络传播权保护条例》](https://www.itsec.gov.cn/fgbz/xgfg/201711/t20171130_17941.html)
3. 最高人民法院关于信息网络传播权纠纷的司法解释要求区分网络服务提供者实际提供作品与提供自动接入、传输、存储、搜索等服务，并以服务性质、明显程度、主动选择编辑推荐、技术能力等事实判断知道或应知。司法解释同时强调兼顾权利人、网络服务提供者与社会公众利益。[最高人民法院：2020 年修正的知识产权类司法解释](https://www.court.gov.cn/xinshidai/xiangqing/282641.html)
4. 因此必须保留两条体系底线：**不满足安全港条件，不等于当然构成直接或间接侵权；使用推荐算法，也不等于当然知道具体内容未经授权。**前者仍须证明责任构成，后者仍须结合通知、人工运营、内容明显性、重复侵权和实际识别能力。
5. 对生成式 AI，现行规则尚未明文建立“改模型型安全港”。将通知后的必要措施解释为特定提示拦截、输出抑制或参数调整，属于新型服务下的解释论与制度设计问题，必须说明类推基础、技术可行性与限度。

---

## 1. Core Institution & Terminology｜核心制度与术语

| 中文制度／知识点 | 精确含义 | Precise English Terminology |
|---|---|---|
| 安全港／赔偿责任限制 | 满足法定条件时限制特定网络服务提供者的赔偿责任；不是“平台行为合法”的一般许可 | safe harbour; limitation on monetary liability |
| 两赛道分析 | 平台是否实施直接侵权或构成间接责任，与其能否获得责任限制分开判断 | two-track analysis: liability and safe-harbour eligibility |
| 通知—必要措施 | 权利人提出合格通知后，平台依证据和服务类型删除、屏蔽、断链或采取其他相称措施 | notice and necessary measures; notice-and-takedown |
| 不侵权声明／反通知 | 被采取措施的用户提交不侵权初步证据，启动转送、争议解决与可能恢复 | counter-notice; statement of non-infringement |
| 实际知道 | 平台对特定侵权内容具有事实认知 | actual knowledge |
| 应当知道／红旗标准 | 具体事实使侵权明显到合理平台不应忽视；不是对站内一般风险的抽象认知 | constructive knowledge; red-flag knowledge |
| 具体知情 | 知识对象能够定位到特定作品、链接、账号、复现路径或其他可操作事实 | specific knowledge |
| 一般监控义务 | 主动审查全部用户内容、主动寻找所有侵权的一般性义务；现行框架原则上不要求 | general monitoring obligation |
| 特殊审查 | 在高风险、反复通知、热播内容或成熟识别条件下对特定对象升级注意 | specific or heightened review duty |
| 目标过滤 | 针对已识别作品、指纹、账号、提示或重复侵权路径的定向拦截 | targeted filtering |
| 普遍过滤 | 对所有内容、所有权利状态持续事前审查，易产生表达和竞争风险 | general filtering; upload filtering |
| 重复侵权／再次上传 | 同一或高度相同内容在删除后重新传播，可能增强采取防再传措施的理由 | repeat infringement; re-upload |
| 必要措施阶梯 | 转通知、删除、屏蔽、断链、账号限制、目标过滤等依控制能力与风险递进 | graduated ladder of necessary measures |
| 算法推荐中立 | 推荐识别兴趣与传播概率，不当然识别授权状态、合理使用或侵权 | neutrality of recommendation algorithms |
| 直接经济利益 | 从特定侵权内容直接获利，与一般平台商业收益区分 | direct financial benefit attributable to the infringing material |
| 过度删除 | 平台因避责而错误或过宽移除合法内容 | over-removal; over-blocking |
| 私人执法 | 平台以自动通知、过滤和账号措施实际执行版权边界 | private enforcement of copyright |
| 程序性保障 | 理由说明、反通知、人工复核、快速恢复、通知数据透明和外部测试 | procedural safeguards; due-process safeguards |
| 规则迁移 | 将传统平台责任的功能移植到生成式服务，同时改变具体措施 | functional transplantation; rule migration |

### 1.1 三个必须分开的判断

`平台是否亲自提供作品？ → 如未直接提供，是否因帮助、诱导及过错承担责任？ → 即使可能承担责任，是否满足赔偿责任限制条件？`

---

## 2. 王迁教程具体知识点｜Targeted Reading Map

| 本专题基础知识 | 具体用法 | 王迁教程入口 |
|---|---|---|
| 直接与间接侵权关系 | 防止从“不符合安全港”直接跳到平台侵权 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#一、直接侵权与间接侵权的基本关系\|直接侵权与间接侵权]] |
| 网络服务三类型 | 接入、存储、定位服务的控制力和通知措施不同 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#2.1 网络服务提供商的三类服务\|2.1 网络服务三类型]] |
| 无一般监控义务 | 过滤义务的制度基线：不能只因未主动发现即推定过错 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#2.2 网络服务商没有一般监控义务 ⭐⭐⭐\|2.2 无一般监控义务]] |
| 通知—移除规则 | 合格通知、必要措施和扩大损害责任的基本结构 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#2.3 通知-移除规则 ⭐⭐⭐\|2.3 通知—移除规则]] |
| 客观帮助与主观过错 | 提供技术条件不当然构成帮助侵权，仍须证明知情或应知 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#8.2 网络服务商答题模板\|8.2 网络服务商判断模板]] |
| 通用技术与 Sony 原则 | 技术具有大量实质性非侵权用途时，避免仅凭可被滥用而全面禁止 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#2.6 🔍 崔国斌补充：通用技术与Sony原则\|2.6 通用技术与 Sony 原则]] |
| 风险配置与实质性帮助 | 从预防成本、风险效用和帮助强度校准平台责任 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#2.5 🔍 崔国斌补充：帮助侵权的三层门槛\|2.5 帮助侵权门槛]] |
| 信息网络传播权 | 先判断究竟是谁向公众提供作品，避免把所有技术服务视为传播者 | [[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#12.2 信息网络传播权 ⭐⭐⭐\|12.2 信息网络传播权]] |
| 侵权责任六步法 | 将直接侵权、限制、间接责任与责任路径按序书写 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#8.1 著作权侵权与责任六步法\|8.1 侵权与责任六步法]] |
| 救济比例限制 | 整体下架、封禁账号、关停服务和改模型均须考虑合法用途与替代措施 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#5.3 销毁侵权复制品的比例限制 ⭐⭐\|5.3 救济的比例限制]] |

---

## 3. Jurisprudential Controversy Analysis｜法哲学争议分析（中文）

### 3.1 安全港不是平台特权，而是规模化网络中的风险配置装置

安全港的正当性不在于平台天然无辜，而在于网络传播把直接侵权主体扩展到海量用户。若平台对每个未知内容承担严格责任，它会选择全面预审、压缩合法表达或退出市场；若平台在任何情况下都不负责，权利人又必须逐一追索匿名、分散且可能无偿付能力的用户。安全港以条件性责任限制交换平台合作，把发现责任、通知成本、阻断能力和错误风险分配给最接近各类信息的主体。

因此，安全港既不是绝对免责，也不是对平台创新的补贴。它是一种制度化分工：权利人提供权属与具体定位信息，平台利用集中控制采取低成本措施，用户通过反通知保护合法表达，法院最终判断争议。其合法性取决于这套分工是否仍能降低总治理成本，同时避免某一方把全部风险外部化给作者、平台或用户。

### 3.2 “知道或应知”的认识论边界：能力不等于知识

算法推荐、流量分成和技术过滤能力会增强平台的传播和治理能力，但不当然使平台知道具体内容未经授权。推荐系统通常识别用户偏好、停留时间和相似主题，版权判断却需要确认作品权属、许可链、合理使用、地域和期限。把“能够推荐”直接等同于“应当知道侵权”，会把技术能力误写成法律知识，并以概括风险替代对具体侵权的证明。

反过来，坚持具体知识也不能成为平台有意失明的庇护。若平台人工置顶完整热播剧，收到多次精确通知，掌握作品指纹与重复账号，仍持续主动放大同一内容，其认识已不再只是“站内可能有侵权”的抽象状态。合理标准应以可操作的事实组合判断：通知是否精确、侵权是否明显、是否重复、平台是否人工介入、能否低成本定位，以及先前措施是否已经失败。

### 3.3 从通知删除到目标过滤：义务升级必须有触发阈值

传统单链接删除面对重复上传和生成式 AI 稳定再生成时可能失效。权利人每次都重新通知，会形成永无止境的执法循环；平台明知同一侵权不断返回却只机械删除，也不符合“必要措施”的实效要求。由此产生目标过滤的正当性：当权利人提供可靠比对样本、侵权反复、技术准确且成本可承受时，平台防止同一内容再次出现，可能仍是针对具体风险的必要措施，而非普遍监控。

关键在于阈值。目标过滤至少应要求：**对象具体、权属初步清楚、重复风险可验证、匹配技术适合该类表达、误报可控、存在人工纠错。**如果平台必须主动识别全站所有作品、判断全球许可与合理使用，义务已经越过具体风险而成为一般监控。特殊审查不能只是普遍审查的新名字；其范围、期限、作品样本和触发事实都必须可被法院复核。

### 3.4 过滤是一种私人版权执法，效率必须受表达程序约束

自动过滤把复杂的版权判断压缩为指纹、相似度、片段时长和账号历史。它擅长识别整部复制，却难以理解评论、戏仿、引用、授权状态和公共领域。平台又有“宁删勿留”的激励：误删合法内容通常由用户分散承担，漏删侵权却可能使平台承担集中责任。若只要求过滤效率，不要求程序保障，版权人和平台将共同获得未经充分审理即可压制表达的私人权力。

因此，算法执法的正当性必须由程序补足：通知人提供真实身份和初步证据；用户能够获得具体理由、提交反通知；争议性表达进入人工复核；错误措施及时恢复；平台记录通知、误报、申诉和恢复情况，并允许在不泄露源代码的前提下进行外部测试。程序不是实体保护的附属物，而是过滤技术能够合法使用的条件。

### 3.5 普遍强制过滤的竞争与分配效应

过滤义务不仅影响版权与表达，也会重塑市场结构。大型平台可以购买指纹库、训练审核模型和雇佣复核团队；中小平台可能因固定合规成本退出，内容识别技术则集中在少数供应商。统一强制过滤表面上同等适用，实质上可能强化既有平台和大型权利人的优势，并使小型创作者、公共领域项目和新进入者承担更高误伤。

这意味着“技术已经可用”不是立法强制化的充分理由。还要比较侵权减少的边际收益、误删和申诉成本、产业集中、数据控制与创新损失。较稳妥的路径是合作差序：权利人提供的权属、样本和指纹越完整，平台对特定重复侵权承担的义务越强；平台规模、服务性质与技术能力不同，措施强度也应不同。

### 3.6 生成式 AI：应保留安全港的功能，而不是机械保留删链接的外形

生成式模型与 UGC 存储平台不同。后者接收用户已经制作的固定内容，通知后可以删除文件或断开链接；前者参与运算并可能反复生成相似内容，删除一次聊天记录未必降低未来风险。这削弱的是传统措施的适配性，不必然否定条件免责本身的制度价值。

可以保留安全港的功能结构——以可检查的注意义务换取有条件的责任限制——但把措施改写为生成场景的比例阶梯：保存复现证据、限制已验证的恶意提示、阻止特定输出重复生成、调整局部安全层，必要时才讨论数据或参数层修改。是否升级取决于稳定复现、通知精度、平台控制、技术成本和合法输出误伤。**安全港应从“删除一个位置”转译为“降低一个已知、具体且可控的风险”，而不是变成模型必须绝对无侵权输出的保证。**

### 3.7 推荐立场：保留框架，重构触发与措施，强化程序

1. **先做两赛道判断。**平台是否实际选择、编辑并向公众提供作品，先按直接侵权分析；如仅提供技术服务，再判断基础侵权、实质帮助、诱导和过错；安全港只在责任限制层出现。
2. **以具体知识为入口。**算法推荐、商业获利和一般过滤能力只是相关因素，不能单独证明应知；精确通知、人工运营、重复侵权、明显性和可定位性形成组合判断。
3. **以措施阶梯替代“删或审全网”。**转通知、删除、屏蔽、断链、限制账号、目标过滤和模型调整依服务架构、风险与成本逐级配置。
4. **目标过滤须具六项条件。**特定作品、初步权属、可靠样本、重复风险、可控误报和有效申诉。缺少这些条件，不应由个案司法创设普遍过滤义务。
5. **程序与实体同等重要。**理由说明、反通知、人工复核、快速恢复、通知数据和外部测试应成为平台是否尽责的指标。
6. **对 GAI 作功能迁移。**保留“合作换免责”的制度逻辑，但不机械沿用链接删除；生成端措施仍须避免严格责任化。

### 3.8 必要措施阶梯｜Graduated Measures

| 风险与知识状态 | 可能措施 | 不应直接跳到的措施 |
|---|---|---|
| 通知模糊、权属不清 | 要求补充、转送用户、保存记录 | 全面删除同类内容、封禁账号 |
| 单一链接且初步证据充分 | 删除、屏蔽或断链，通知用户 | 审查全站全部作品 |
| 同一作品反复上传，已有可靠指纹 | 对特定作品目标过滤、处置重复账号 | 对所有作品设置一般监控 |
| App 或云服务中仅有局部侵权 | 优先定位具体内容、转通知或限制相关功能 | 整体下架 App、关停服务器 |
| GAI 特定提示稳定复现 | 保存测试、限制特定提示、抑制已验证输出 | 一收到通知即重训整个模型 |
| 轻措施无效且模型商能局部修正 | 去重、安全层更新或局部模型调整 | 无技术证据地命令“彻底遗忘” |

---

## 4. English Jurisprudential Analysis & Interview Corpus｜英文学理分析与面试语料

### 4.1 Safe Harbour as Institutional Risk Allocation

Safe harbour should not be understood as a privilege granted to platforms because technology firms are presumptively innocent. Its justification lies in the structure of networked infringement. Digital networks disperse direct infringement among enormous numbers of users, while platforms remain concentrated points of control. Strict platform liability would predictably induce universal screening, excessive removal, and market exit; unconditional immunity would force right holders to pursue anonymous and often judgment-proof users one by one. A conditional limitation on liability allocates discovery, notice, intervention, and error costs to the actors best placed to bear them.

This institutional function also explains why failure to satisfy a safe harbour cannot itself establish infringement. The court must still determine whether the platform directly provided the work or incurred fault-based secondary responsibility. Safe harbour limits a form of liability; it does not replace the elements of that liability. Maintaining this two-track analysis preserves legality and prevents a procedural condition for immunity from becoming an unarticulated form of strict liability.

### 4.2 Knowledge, Recommendation, and the Threshold for Targeted Filtering

The use of recommendation algorithms is relevant but not conclusive evidence of knowledge. A recommendation system may predict attention and similarity without determining ownership, licensing, fair use, territorial scope, or the public-domain status of a work. Technological capacity should not be confused with legal knowledge. At the same time, a platform should not benefit from deliberate ignorance where it repeatedly receives precise notices, possesses reliable fingerprints, manually promotes the material, and observes the same infringement returning through identifiable accounts.

The defensible middle position is specific knowledge combined with graduated duties. Targeted filtering may remain a necessary measure where the protected work is identified, ownership is prima facie established, repeat infringement is demonstrated, matching technology is suitable, and error correction is effective. A duty becomes general monitoring when the platform must independently discover all protected works, determine every licence and exception, and screen the entire service without a defined object or endpoint. The difference is not merely quantitative; it concerns whether the duty remains tied to an adjudicable risk.

### 4.3 Private Enforcement, Expression, and Competition

Automated filtering is a form of private copyright enforcement. It converts contextual legal judgments into fingerprints, similarity thresholds, duration limits, and account scores. Such systems can identify exact duplication efficiently, but they are poor at evaluating quotation, criticism, parody, authorization, and public-domain material. Platforms also face asymmetric incentives: the costs of wrongful removal are dispersed among users, whereas the costs of under-removal may be concentrated on the platform. Without procedural safeguards, automation can therefore create a private censorship regime under the language of copyright compliance.

Legitimate filtering requires notice integrity, reason giving, counter-notice, meaningful human review, prompt restoration, and auditable information about error and appeal outcomes. Competition must also enter the analysis. A universal filtering mandate may appear formally equal while imposing fixed costs that only dominant platforms and large right holders can absorb. The resulting concentration can suppress new services and smaller creators. The proportionality inquiry should therefore consider not only accuracy and infringement reduction, but also entry barriers, dependency on proprietary fingerprint databases, and the distribution of compliance costs.

### 4.4 Functional Translation to Generative AI

Generative AI does not make the institutional logic of safe harbour obsolete, but it does make traditional remedies incomplete. A storage platform can remove a fixed file; a generative service may reproduce similar expression after the visible output has been deleted. The law should preserve the exchange at the heart of safe harbour—verifiable cooperation in return for conditional protection—while translating necessary measures into the architecture of generation. Possible measures include preserving reproduction logs, blocking a verified malicious prompt, suppressing a repeatable output, updating a localized safety layer, and only in stronger cases modifying data or model parameters.

The provider should not be required to guarantee a model free of every infringing output. More intrusive intervention should depend on stable repeatability, precise notice, meaningful control, technical efficacy, and the inadequacy of less restrictive measures. In short, safe harbour should evolve from removing a location to reducing a known, specific, and controllable risk. That functional translation preserves innovation without allowing a provider to invoke the randomness of generation after a concrete risk has become predictable and manageable.

### 4.5 Four-Paragraph Interview Answer｜四段式口述成稿

I would not frame the issue as a binary choice between preserving and abolishing safe harbour. Safe harbour is an institutional mechanism for allocating enforcement costs in a network where direct infringers are numerous and platforms are concentrated control points. It limits liability when providers cooperate under defined conditions, but it does not determine whether they directly or secondarily infringed in the first place. Accordingly, failure to qualify for the safe harbour should never be treated as an automatic finding of infringement.

The key issue is the knowledge threshold. Recommendation, monetization, and technical capacity are relevant facts, but none independently proves that a platform knew a particular item was unauthorized. Copyright status depends on ownership, licensing, exceptions, and context. Nevertheless, where a platform receives repeated precise notices, possesses reliable reference material, manually promotes the content, and can identify recurring uploads at low cost, its duty may properly escalate beyond removing a single link.

I therefore support targeted filtering but reject a general monitoring obligation. Targeted filtering should require an identified work, prima facie ownership, reliable comparison material, demonstrable repetition, manageable error rates, and an effective appeal process. These conditions keep the duty connected to a concrete risk. A universal obligation to determine the legal status of all content would encourage over-removal, privatize adjudication, and impose compliance costs that entrench dominant platforms.

For generative AI, the logic of conditional protection can survive even though the traditional remedy cannot simply be copied. Deleting one output may not prevent the model from generating it again. Necessary measures may therefore include blocking a verified prompt, suppressing stable reproduction, or updating a localized safety layer. More invasive model modification should require stronger proof of repeatability, control, technical efficacy, and inadequate alternatives. The correct reform is thus a functional translation of safe harbour, combined with procedural safeguards—not its wholesale abolition or mechanical extension.

### 4.6 Reusable Phrases｜可复用表达

- **safe harbour as an institutional allocation of enforcement costs** — 安全港作为执法成本配置机制
- **a limitation on liability rather than a substantive licence** — 责任限制而非实体许可
- **technological capacity should not be confused with legal knowledge** — 技术能力不能与法律知识混同
- **specific knowledge combined with graduated duties** — 具体知情与阶梯式义务
- **a duty tied to an adjudicable risk** — 与可裁判的具体风险相连接的义务
- **private copyright enforcement and asymmetric incentives to remove** — 私人版权执法与偏向删除的非对称激励
- **procedural safeguards against over-removal** — 防止过度删除的程序保障
- **a functional translation rather than mechanical transplantation** — 功能性转译而非机械移植
- **from removing a location to reducing a known and controllable risk** — 从删除位置转向降低已知且可控风险

### 一句立场句｜One-sentence Position

> I would preserve safe harbour as a conditional allocation of enforcement responsibility, require specific knowledge before duties escalate, permit proportionate targeted filtering, and subject automated copyright enforcement to meaningful procedural and competition safeguards.

---

## 5. Future Testing Angle｜未来面试追问

### Question 1

**中文：**某短视频平台已经收到权利人提供的完整作品指纹，但大量相关视频可能构成评论、戏仿或适当引用。平台是否应防止再次上传？请设计目标过滤的阈值、人工复核和错误恢复机制。

**English:** A short-video platform has received a complete fingerprint of the claimant’s work, but many matching videos may constitute criticism, parody, or lawful quotation. Should the platform prevent re-uploading? Design the thresholds for targeted filtering, human review, and restoration after error.

### Question 2

**中文：**生成式 AI 在收到通知后仍可由特定提示稳定复现原作。传统安全港应否类推适用？如果适用，哪些义务是获得免责的条件；如果不适用，你如何避免模型提供者承担事实上的严格责任？

**English:** After notice, a generative service can still reproduce a protected work through a specific prompt. Should traditional safe-harbour logic apply by analogy? If so, which duties should condition protection? If not, how would you avoid imposing de facto strict liability on the model provider?

---

## 6. 复习抓手

- **不是存废，而是功能改造**：保留合作换免责的逻辑，改变生成环境下的措施。
- **两赛道**：责任构成与安全港资格分开；不符合安全港不等于侵权。
- **知识阈值**：推荐与获利只是因素，具体通知、重复侵权和人工介入更关键。
- **措施边界**：目标过滤须绑定特定作品与可复核风险；一般监控不得借“特殊审查”复活。
- **程序底线**：反通知、人工复核、理由说明、快速恢复与错误数据共同决定过滤正当性。
- **GAI 迁移句**：从删除固定链接，转向降低已知、具体、可控的稳定再生成风险。

