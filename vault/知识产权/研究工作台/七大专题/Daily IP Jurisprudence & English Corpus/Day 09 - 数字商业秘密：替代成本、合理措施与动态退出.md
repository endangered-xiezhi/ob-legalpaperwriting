---
type: daily_ip_jurisprudence_corpus
day: 9
topic: "数字商业秘密：替代成本、合理措施与动态退出"
date: 2026-08-17
status: completed
language: zh-en
source_scope: "专题07 + 专题04/05交叉部分 + 王迁知产教程重构版相邻知识点 + 官方法源校核"
---

# Day 09｜数字商业秘密：替代成本、合理措施与动态退出

> [!abstract] 今日命题
> 商业秘密不是对所有“内部数据”或“高投入模型”的自然权。它保护的是可具体识别、尚未被相关领域普遍知悉和容易获得、具有商业价值且被相应措施划定边界的信息。数字环境的核心问题是：**如何以合法替代成本理解秘密性，又不把公开元素、独立开发、反向工程和算法透明纳入永久控制。**

> [!info] 系列位置
> 本页处理非公开数据、模型参数、提示库和训练诀窍。公开数据抓取与数据专款见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 05 - 商业数据保护：确权、控制还是行为规制\|Day 05]]；商业秘密不成立后的竞争法边界见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 06 - 一般条款的边界：补充保护还是准知识产权\|Day 06]]；总分流见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/01 - 非版权专题总图：数据、竞争法、商标与商业秘密\|非版权专题总图]]。

## 0. 材料定位与现行法校核

### 本地材料

- 快速入门：[[知识产权/研究工作台/七大专题/07_商业秘密数字化_快速入门]]
- 学说全景：[[知识产权/研究工作台/七大专题/07_商业秘密数字化_学说争议全景]]
- 六阶段详版：[[知识产权/研究工作台/七大专题/07_商业秘密数字化_六阶段逻辑合并]]
- 数据交叉：[[知识产权/研究工作台/七大专题/04_商业数据保护_快速入门]]
- 一般条款交叉：[[知识产权/研究工作台/七大专题/05_一般条款与行为类型化_快速入门]]
- 制度基础：[[法书/03王迁-知产教程-重构版/专利法✅/9专利法律制度概述]]、[[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任]]

### 现行法底线（截至 2026-08-17）

1. 2025 年修订《反不正当竞争法》第 10 条将商业秘密定义为“不为公众所知悉、具有商业价值并经权利人采取相应保密措施的技术信息、经营信息等商业信息”，并禁止盗窃、贿赂、欺诈、胁迫、电子侵入等不正当获取，以及后续披露、使用、违反保密义务和教唆帮助。[《反不正当竞争法（2025 年修订）》](https://www.cnipa.gov.cn/art/2026/5/20/art_104_206437.html)
2. 该法第 39 条设置分层举证转换：权利人提供采取保密措施及合理表明被侵犯的初步证据后，涉嫌侵权人证明信息不构成商业秘密；权利人进一步合理表明接触机会＋实质相同、披露使用风险等情形时，涉嫌侵权人证明不存在侵权。[最高人民法院公报：2025 年《反不正当竞争法》](https://gongbao.court.gov.cn/Details/b0b878485fb87a8c81167932502dc2.html)
3. 最高人民法院 2020 年商业秘密司法解释明确：算法、数据、计算机程序及文档可构成技术信息，经营数据可构成经营信息；公开信息经整理、改进、加工形成的新信息，若不为相关人员普遍知悉和容易获得，仍可具秘密性；相应保密措施需结合载体、价值、可识别性、对应程度和保密意愿判断；独立开发和对公开渠道取得产品的合法反向工程不构成侵权。[最高人民法院法释〔2020〕7 号](https://www.court.gov.cn/fabu/xiangqing/254751.html)
4. “替代成本”是解释秘密性、合理措施、价值与救济的分析工具，**不是法条规定的第四个独立构成要件**。模型研发成本很高，也不能免除对具体秘密点和不当获取的证明。
5. 诉讼中保护秘密与对方程序权并非二选一。司法解释允许法院采取保密措施；权利人不能以“黑箱”为由只给结论、拒绝具体化秘密点，又要求法院全面倒置证明责任。

---

## 1. Core Institution & Terminology｜核心制度与术语

| 中文制度／知识点 | 精确含义 | Precise English Terminology |
|---|---|---|
| 商业秘密 | 具秘密性、商业价值和相应保密措施的技术、经营等商业信息 | trade secret |
| 秘密点 | 原告请求保护的具体信息内容、结构、组合或参数边界 | specifically identified trade-secret information; secret point |
| 不为公众所知悉 | 相关领域人员并非普遍知悉，且不能容易获得 | not generally known or readily ascertainable |
| 商业价值 | 信息因秘密性具有现实或潜在竞争优势 | commercial value derived from secrecy |
| 相应／合理保密措施 | 与信息性质、价值、载体及风险相称、能识别保密边界的措施 | reasonable or appropriate confidentiality measures |
| 替代成本 | 他人通过合法方式取得或重建相同信息所需的时间、金钱与技术投入 | lawful cost of substitution; replacement cost |
| 组合秘密 | 单个要素可能公开，但特定选择、关系和组合整体不易获得 | combination trade secret |
| 有限共享 | 信息在员工、供应商、客户等有限范围内披露但仍受明确保密边界控制 | limited disclosure under confidentiality |
| 获取—使用区分 | 分别审查信息如何获得，以及之后如何披露、利用或允许他人利用 | distinction between acquisition and use |
| 电子侵入 | 未经授权进入数字系统、账号、接口或存储环境取得信息 | electronic intrusion |
| 保密义务 | 源于法律、合同、关系性质、缔约过程或明确保密要求的义务 | duty of confidentiality |
| 接触加实质相同 | 以接触机会和信息高度相同构成侵权事实推断的证据结构 | access plus substantial similarity |
| 独立开发 | 未利用权利人秘密而自行研发相同或近似信息 | independent development |
| 反向工程 | 对从公开渠道合法取得的产品进行技术分析以获得信息 | reverse engineering |
| 知识蒸馏 | 以教师模型输出训练较小模型的技术，可构成合法学习或不当提取 | knowledge distillation; model extraction |
| 模型提取攻击 | 通过系统化查询复制模型功能、边界或参数信息的行为 | model extraction attack |
| 参数／权重 | 模型训练形成的数值状态；是否为秘密取决于可识别性、公开性与措施 | model parameters; weights |
| 提示库 | 经选择、测试、排序形成的内部提示集合和工作流 | prompt library; prompt repository |
| 推理日志 | 记录输入、输出、版本、调用与决策过程的数据 | inference logs; audit logs |
| 分层透明 | 向监管者、审计者、交易相对人和公众提供不同深度的信息 | tiered transparency |
| 动态退出 | 信息因公开、合法重建或技术普及失去秘密性后退出保护 | dynamic loss of trade-secret status |
| 头部期优势 | 仅保护竞争者合法重建所需时间，而非永久禁止使用同类信息 | head-start period; lead-time advantage |
| 诉讼保密令 | 在证据交换、庭审和裁判公开中限制秘密披露的程序措施 | protective order; confidentiality order |

### 1.1 八道门

`具体秘密点 → 秘密性／合法可获得性 → 商业价值 → 相应措施 → 获取路径 → 使用方式 → 证明与透明 → 动态退出与救济`

---

## 2. 王迁教程具体知识点｜Targeted Reading Map

> [!warning] 对应范围
> 王迁教材目录中没有商业秘密法专章。下列链接提供的是“专利公开—商业秘密保密”的制度选择、技术控制边界和权利正当性工具；法定三要件及侵权行为仍以《反不正当竞争法》和商业秘密司法解释为直接依据。

| 基础知识 | 对数字商业秘密的具体用法 | 王迁教程入口 |
|---|---|---|
| 专利公开要求的正当性 | 理解法定排他必须以公开、期限和明确边界交换；商业秘密采取不同制度交易 | [[法书/03王迁-知产教程-重构版/专利法✅/9专利法律制度概述#公开要求的正当性 ⭐⭐⭐\|专利公开要求]] |
| 专利与商业秘密差异 | 掌握授权产生／事实状态、强排他／有限保护、期限／秘密持续、反向工程等区别 | [[法书/03王迁-知产教程-重构版/专利法✅/9专利法律制度概述#5.1 两种保护路径的差异 ⭐⭐⭐\|两种保护路径]] |
| 技术保护策略 | 从反向工程难度、生命周期、独立研发、公开成本判断保护选择 | [[法书/03王迁-知产教程-重构版/专利法✅/9专利法律制度概述#5.2 技术保护策略的判断因素 ⭐⭐⭐\|技术保护策略]] |
| 技术措施的功能与分类 | 区分访问控制、复制控制与底层权利，辅助评价数字保密措施 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#3.1 技术措施的功能和分类\|技术措施功能与分类]] |
| 规避技术措施的性质 | 技术规避可能独立违法或证明不当获取，但不替代秘密三要件 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#3.4 规避技术措施行为的性质 ⭐⭐\|规避技术措施的性质]] |
| 技术控制与合法利用冲突 | 防止技术措施把独立开发、研究、兼容和公共信息完全封锁 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#3.6 技术措施保护与合理使用的冲突 ⭐⭐⭐\|技术措施与合法利用]] |
| 劳动正当性及局限 | 高研发成本证明价值，不自动证明秘密性或不当获取 | [[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#3.1 劳动自然权学说详解\|劳动自然权学说]]、[[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#劳动自然权学说的问题\|劳动学说的局限]] |

---

## 3. Jurisprudential Controversy Analysis｜法哲学争议分析（中文）

### 3.1 商业秘密保护的是诚实获取秩序，而非对信息的完全占有

专利可以对抗独立研发者，商业秘密通常不能。后一制度不以国家审查、公开和登记产生权利，而是保护权利人划定的保密边界，并禁止盗窃、电子侵入、违反保密义务等不当获取及后续利用。这说明其核心不是信息一旦“属于”企业，所有人都不得获得，而是竞争者必须通过独立开发、合法观察或反向工程承担自己的替代成本。

因此，商业秘密同时保护投入与维持竞争。它允许企业选择不公开，也保证竞争者通过正当路径到达相同结果。若保护延伸到独立研发或公开产品的合法分析，就会得到专利强度却没有专利公开、审查和期限的约束。

### 3.2 秘密点具体化是实体边界，也是程序正义要求

原告常以“整套算法”“客户数据”“模型能力”概括主张，但法院若不知道具体秘密是什么，就无法判断是否公开、措施是否对应、被告信息是否实质相同，也无法让被告进行不泄密条件下的有效答辩。笼统客体会把举证困难转化为事实垄断。

秘密点可以是具体参数区间、标签体系、特征工程、数据组合关系、未公开负样本、部署流程或提示工作流，但必须与一般知识、公有组件和从产品输出可观察的信息分开。具体化不要求权利人在公开判决中披露秘密；可通过保密令、限制查阅、密封材料和专业比对兼顾秘密保护与对抗程序。

### 3.3 替代成本连接三要件，但不能成为第四要件

“不为公众所知悉”不仅是网上能否搜索到，也包括相关人员能否通过合法渠道容易获得。替代成本因此可解释秘密性：若行业人员凭公开资料在短期低成本内即可重建，秘密性较弱；若需要长期试错、负面经验和高成本数据整理，集合即使包含公开元素，仍可能不易获得。

替代成本也帮助评价措施和价值。高价值、易泄露的信息通常要求更精细的访问控制；信息因能节省竞争者重建成本而具有商业价值；救济可围绕竞争者不当节省的头部期设置。但它不是独立法定要件，更不能仅凭“研发花费十亿元”替代秘密点、保密措施和不当获取。

### 3.4 公开元素可以形成组合秘密，但组合边界必须真实存在

单个客户名称、公开价格、开源代码或已发表论文不因企业重新收集而恢复秘密性。可是特定选择、清洗、历史变化、关联规则、排除标准和排序逻辑可能形成普通业内人员不能容易获得的组合信息。保护对象应是这一组合产生的非公开结构，而非其中每个公共元素。

组合秘密的风险在于权利人把“集合”作为口袋，间接禁止使用公共信息。法院应要求说明组合的内容、关系、形成方式和重建难度，并在比对时剔除公知部分。被告独立收集同样公开元素并以不同关系组织，原则上不应因结果相近而侵权。

### 3.5 相应保密措施的功能是告知边界，不是实现绝对不可破

商业活动需要员工、供应商、客户和云服务商接触信息；要求完全封闭会使秘密失去商业用途。相应措施的正当功能是表明保密意愿、限定知悉范围并使接触者可合理识别义务。分级权限、加密、日志、下载限制、保密协议、离职返还和供应商控制可组合使用。

措施应与价值、载体、组织规模和风险相称。把所有文件统一标“机密”却开放全员下载，形式上有标签、实质上没有边界；反之，小型企业未采用最昂贵技术，也不当然失去保护。数字系统尤其需要证明措施与具体秘密点相对应，而不是列举一套抽象网络安全制度。

### 3.6 爬虫、反向工程和蒸馏必须拆成“取得—对象—使用”三层

爬虫可能抓取公开信息，也可能绕过认证进入后台；蒸馏可能学习公开输出的功能，也可能通过异常查询提取决策边界、隐藏标签或参数信息。技术名称不能决定合法性。应分别判断取得是否经授权或规避真实访问边界，对象是否满足秘密三要件，以及之后是否披露或使用实质相同的秘密。

合法反向工程保障竞争性学习，但其前提是产品从公开渠道合法取得，且行为人未先通过不当方式接触秘密。服务接口不同于可购买实体产品：调用规模、合同安排、身份欺骗、限流规避和系统负担会影响取得评价，但服务条款也不能任意消灭所有观察和兼容空间。蒸馏的关键不是“学生像老师”，而是其是否不当节省了法律要求其自行承担的替代成本。

### 3.7 模型、参数和提示词必须逐层判断，不能以“模型”作为单一秘密

闭源模型的权重、架构细节、训练数据配比、调参记录和安全策略可能分别构成秘密，也可能因论文、开源发布、本地部署、API 可推断性或行业常识而失去秘密性。权利人必须逐项说明秘密点与措施。模型体积巨大不等于每个参数都有独立商业意义；整体比对也不能掩盖公有架构和开源组件。

提示词亦然。用户随手输入的一句提示通常容易获得；经长期测试形成、按任务分类、结合内部数据和评估规则的提示库可能具有组合秘密。是否归属于员工、雇主、平台或客户，还需合同和职务成果规则处理，不能只凭“存放在公司账号”确定。

### 3.8 AI 会动态降低替代成本，秘密性因此不是永久状态

过去需要专家数月试验的信息，可能因开源模型、自动化搜索或公开基准而快速重建。判断“容易获得”应以侵权行为发生时相关领域人员的能力为基准，并考虑合法工具的普及程度。不能因被告本人技术特别强就否定秘密，也不能以权利人历史成本冻结已经普及的知识。

保护应随信息状态退出：公开发布、标准化、产品可观察、合法反向工程或行业普及会终止秘密性。禁令一般持续到信息合法进入公开领域；损害赔偿或不当节省成本可参考头部期，而非形成超过合法重建时间的永久排除。

### 3.9 透明、举报与诉讼证明需要分层披露

算法透明的目的可能是解释风险、审计歧视、保障监管和允许当事人质疑决定，并不必然要求向全社会公开源代码或权重。可按公众、受影响用户、独立审计者、监管机关和法院配置不同深度，使用摘要、受控访问、保密审查和结果验证。

同样，举报公共违法、依法向监管机关提供信息与向竞争者商业披露性质不同。商业秘密不能成为掩盖违法和阻断司法的盾牌，但公共利益例外必须要求目的、对象、范围和必要性相称，避免以举报名义向市场扩散全部商业信息。

### 3.10 推荐立场：具体化、替代成本解释、路径分层、动态退出

1. 权利人先列明具体秘密点，剔除公知信息和抽象功能。
2. 以相关领域人员通过合法手段能否容易重建判断秘密性；替代成本只作贯穿性工具。
3. 公开条目可形成组合秘密，但保护只及于非公开的选择、关系和结构。
4. 保密措施须与具体秘密、价值、载体和风险对应，并能合理告知边界。
5. 分别审查获取路径、受保护对象和后续使用；合同违约、技术规避、商业秘密和一般条款不得混同。
6. 独立开发和合法反向工程必须保留；蒸馏依对象、访问和替代成本判断。
7. 模型、数据、参数、提示和日志逐层识别，不以“AI 黑箱”整体设权。
8. 以分层透明、诉讼保密和动态退出兼顾问责、程序与竞争自由。

### 3.11 三层分流

| 问题 | 核心判断 | 不得替代的事项 |
|---|---|---|
| 是否有商业秘密 | 秘密点＋秘密性＋价值＋相应措施 | 高投入不能替代秘密性，NDA 不能创造不存在的秘密 |
| 是否侵犯 | 不当获取／违反义务／披露使用＋实质相同 | 相似结果不能替代接触与行为证明 |
| 如何救济 | 禁令期限、头部期损失、保密程序、公共利益 | 禁令不能超过秘密存续，透明不等于公开源代码 |

---

## 4. English Jurisprudential Analysis & Interview Corpus｜英文学理分析与面试语料

Trade-secret law is not a complete property right in valuable information. Its distinctive function is to preserve an honest process of acquisition: competitors remain free to arrive at the same information through independent development, lawful observation, or reverse engineering, but they may not obtain it through electronic intrusion, deception, or breach of confidence. This structure protects investment while retaining competitive pathways to the same result. Extending liability to independent creation would confer patent-like exclusivity without examination, disclosure, or a fixed term.

The identification of the alleged secret is both a substantive boundary and a requirement of procedural justice. A claimant cannot merely invoke an entire algorithm, customer database, or model capability. It should isolate the parameters, relationships, negative know-how, data architecture, workflow, or combination said to be non-public, while separating public components and general skill. Courts can protect the information through confidentiality orders and restricted access, but secrecy cannot justify depriving the defendant of a meaningful opportunity to contest the claim.

Replacement cost is a useful unifying concept, but not an additional statutory element. It helps determine whether relevant professionals could lawfully and readily reconstruct the information, whether protective measures were proportionate, why secrecy creates commercial value, and how long an unlawful head start should be neutralized. Public elements may constitute a combination secret when their selection, historical structure, and interrelationships are not readily ascertainable. Yet the protected object must remain the non-public combination, not each public datum within it.

In AI disputes, courts should separate the means of access, the informational object, and the subsequent use. Knowledge distillation through public outputs may be competitive learning; systematic queries that circumvent meaningful controls and extract a protected decision structure may be misappropriation. Model weights, training recipes, prompt libraries, and logs require separate analysis because their secrecy changes with publication, open-source release, local deployment, and advances in lawful reconstruction. My preferred approach therefore combines specific identification, proportionate safeguards, preserved rights of independent development and reverse engineering, tiered transparency, and dynamic loss of protection once lawful substitution becomes readily available.

### Reusable Phrases｜可复用表达

- **an honest process of acquisition rather than complete ownership of information** — 诚实取得秩序而非信息完全所有权
- **patent-like exclusivity without examination, disclosure, or term** — 无审查、公开和期限的专利式排他
- **identification as both a substantive and procedural boundary** — 秘密点具体化兼具实体与程序边界
- **replacement cost as an interpretive tool, not a fourth element** — 替代成本是解释工具而非第四要件
- **the non-public combination rather than each public component** — 非公开组合而非每个公共要素
- **to separate access, informational object, and subsequent use** — 区分取得、信息对象与后续使用
- **competitive learning versus model extraction** — 竞争性学习与模型提取
- **dynamic loss of protection as lawful substitution becomes feasible** — 随合法替代可行而动态退出保护

### 一句立场句｜One-sentence Position

> Digital trade-secret law should protect specifically identified information against improper acquisition while preserving lawful substitution, independent development, reverse engineering, tiered accountability, and dynamic entry into the public domain.

---

## 5. Future Testing Angle｜未来面试追问

### Question 1

**中文：**某闭源模型只能通过付费 API 访问。竞争者注册多个账号，高频查询后蒸馏出功能近似的小模型。请分别判断秘密点、保密措施、合同、技术规避、反向工程、实质相同和替代成本；“输出可见”是否意味着模型秘密已经公开？

**English:** A closed model is accessible only through a paid API. A competitor creates multiple accounts, submits high-volume queries, and distils a smaller model with similar functionality. Analyse the secret, safeguards, contract, circumvention, reverse engineering, substantial identity, and replacement cost. Does the visibility of outputs mean that the model’s secrets are public?

### Question 2

**中文：**监管机关要求高风险算法说明训练数据类别、关键特征和风险控制。企业主张全部属于商业秘密。请设计一套分层透明方案，并说明哪些信息应向公众、受影响者、审计者、监管机关和法院分别披露。

**English:** A regulator requires a high-risk algorithm to disclose training-data categories, key features, and risk controls. The company claims that all such information is secret. Design a tiered-transparency regime specifying what should be disclosed to the public, affected persons, auditors, regulators, and courts.

---

## 6. 复习抓手

- **第一步永远是秘密点**，不是先说公司花了多少钱。
- **替代成本不是第四要件**，但可贯穿秘密性、措施、价值和救济。
- **公开单项不等于组合公开**，但组合保护不得反向垄断公共要素。
- **合理措施重在告知边界**，不要求绝对不可破解。
- **三层拆解**：取得路径、受保护对象、后续使用。
- **两条合法路径**：独立开发与合法反向工程。
- **AI 分层**：权重、架构、数据配比、调参、提示库和日志分别判断。
- **动态退出**：信息一旦可合法容易获得，保护即应缩减或终止。

