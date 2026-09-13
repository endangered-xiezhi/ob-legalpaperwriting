---
type: daily_ip_jurisprudence_corpus
day: 3
topic: "AIGC输出侵权与生成链归责：表达、法律联系与多主体责任"
date: 2026-08-17
status: completed
language: zh-en
source_scope: "专题08 + 王迁知产教程重构版 + 官方法源校核"
---

# Day 03｜AIGC 输出侵权与生成链归责

> [!abstract] 今日命题
> 输出“很像”只是事实印象，不是侵权结论。真正的问题是：**相似部分是否属于受保护表达；原作与输出之间是否存在可评价的法律联系；用户、基础模型商、微调者与 API 接入商分别对生成、选择和利用行为承担何种责任。**

> [!info] 系列位置
> 训练数据的复制、例外与许可见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 02 - 训练数据的版权入口与制度出口|Day 02]]。本页不展开传播平台的安全港条件；通知、目标过滤与程序保障见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 04 - 安全港的功能性改造：具体知情、目标过滤与程序保障|Day 04]]。共通原则见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/00 - AIGC版权责任链总图：训练、输出与平台|责任链总图]]。

## 0. 材料定位与现行法校核

### 本地材料

- 快速入门：[[知识产权/研究工作台/七大专题/08_AIGC输出侵权与责任分配_快速入门]]
- 学说全景：[[知识产权/研究工作台/七大专题/08_AIGC输出侵权与责任分配_学说争议全景]]
- 相邻专题：[[知识产权/研究工作台/七大专题/01_AIGC可版权性_快速入门]]、[[知识产权/研究工作台/七大专题/02_大模型训练数据版权_快速入门]]、[[知识产权/研究工作台/七大专题/03_平台过滤义务与避风港_快速入门]]
- 制度基础：[[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体]]、[[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用]]、[[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任]]

### 现行法底线（截至 2026-08-17）

1. 《著作权法》第 10 条分别规定复制权、改编权和信息网络传播权等专有权。AIGC 案件必须先锁定被诉行为：是在服务器上形成输出、根据原作形成演绎表达，还是由用户向公众提供；不能以一个笼统的“AI 侵权”覆盖不同权利。[中国人大网：《中华人民共和国著作权法》](https://www.npc.gov.cn/c2/c30834/202011/t20201119_308796.html)
2. 现行法没有专门规定“模型输出实质性相似即由模型商承担严格责任”，也没有以“风格模仿”作为独立的著作权侵权类型。风格、思想、题材和方法是否不受保护，具体人物、构图和表达组合是否受保护，仍依一般作品范围与侵权比对规则判断。
3. 《生成式人工智能服务管理暂行办法》要求服务提供者尊重知识产权、依法承担网络信息内容生产者责任等公法义务；这些规范可成为衡量注意义务的材料，但违反部门规章不当然等于侵犯某一项著作权，更不能跳过受保护表达、行为、损害和因果关系。[中国网信网：《生成式人工智能服务管理暂行办法》](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm?mhEnc=3d537d9731a15cfadd38e2d9f63e5491&mhType=2&pageId=1171717&publicId=3839645904b1b311ef1a85b3f3def5ca09f9&websiteId=602694&wfwfid=120336)
4. 《人工智能生成合成内容标识办法》已于 2025 年 9 月 1 日施行。显式与隐式标识有助于确认内容来源、服务提供者和传播链，但标识制度主要解决识别与溯源，不能替代版权侵权比对。[中国网信网：标识办法发布说明](https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm)

---

## 1. Core Institution & Terminology｜核心制度与术语

| 中文制度／知识点 | 精确含义 | Precise English Terminology |
|---|---|---|
| 受保护表达 | 剔除思想、事实、公有领域、惯常元素、场景原则与混同部分后，著作权实际控制的表达 | protectable expression |
| 风格 | 跨作品反复出现的创作方法、视觉气质或表达规律；通常不能作为抽象风格被单独垄断 | style; artistic style |
| 实质性相似 | 比较输出与原作受保护表达是否在数量、质量和组合上达到法律要求的相似程度 | substantial similarity |
| 接触可能性 | 被诉创作者或生成系统接触原作的机会；在模型场景中可涉及训练收录、用户上传或微调数据 | access; opportunity of access |
| 法律联系 | 将输出与原作连接起来的可评价事实，不等于仅凭高相似就锁定责任主体 | legally relevant connection; copying nexus |
| 输出类型化 | 区分独立生成、题材／风格模仿、训练材料抽取、记忆型稳定复现 | typology of outputs; independent generation, imitation, extraction, memorized reproduction |
| 稳定复现 | 在相同或近似提示下可重复、低成本地产生高度相似表达 | stable and repeatable reproduction |
| 定向诱导 | 用户上传原作、指定具体作品并要求复刻，或以特殊提示绕过限制 | targeted prompting; deliberate inducement |
| 用户选择与利用 | 用户从多个结果中选择、保存、发布、销售或用于商品化的行为 | selection, publication, and commercial exploitation by the user |
| 直接侵权 | 主体本人实施某项专有权控制的行为；原则上先于平台二级责任判断 | direct infringement |
| 间接责任 | 主体未直接完成全部受控行为，但在存在基础侵权时提供实质帮助、诱导，并具有相应过错 | secondary liability; indirect infringement |
| 过错推定 | 权利人完成初步证明后，由掌握信息的一方说明其已尽合理注意；不是严格责任 | rebuttable presumption of fault |
| 说明责任 | 因证据与技术信息集中而要求模型方说明来源、去重、复现测试和控制环节 | burden of explanation |
| 基础模型提供者 | 提供通用模型能力的主体；其责任取决于是否加入、知悉或控制特定侵权能力 | foundation-model provider |
| 微调者 | 用特定数据进一步训练模型并可能注入特定复现能力的主体 | fine-tuner; downstream model developer |
| API 接入商 | 通过接口提供终端服务，可能仅传输，也可能修改系统提示、选择输出或重新训练 | API integrator; application-layer provider |
| 传播平台 | 承载用户发布、推荐或销售输出的下游平台；其通知与免责另见 Day 04 | dissemination platform; content-sharing platform |
| 生成端救济 | 去重、限制特定提示、防过拟合、输出抑制或模型更新等面向再生成的措施 | generation-side remedies |

### 1.1 固定分析顺序

`确定权利作品 → 过滤不受保护元素 → 比较受保护表达 → 证明接触／法律联系 → 输出类型化 → 用户行为 → 模型链分工 → 直接／间接责任 → 比例化救济`

---

## 2. 王迁教程具体知识点｜Targeted Reading Map

| 本专题基础知识 | 具体用法 | 王迁教程入口 |
|---|---|---|
| 作品成立不等于侵权成立 | AIGC 输出有无自己的版权，不决定是否侵犯先作品 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#5.1 作品成立 ≠ 侵权成立\|5.1 作品成立不等于侵权成立]] |
| 侵权比对方法 | 先过滤思想、事实、公共和惯常元素，再比较剩余表达 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#5.2 侵权比对方法\|5.2 侵权比对方法]] |
| 思想／表达二分 | 风格、题材与抽象角色设定原则上不能直接私有化 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#6.1 思想表达二分法\|6.1 思想表达二分法]] |
| 思想与表达分界 | 用抽象层级识别角色、情节、构图何时具体到表达 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#6.3 思想与表达的分界线 ⭐⭐\|6.3 思想与表达分界]] |
| 情节相似四步法 | 排除不保护元素，判断充分描述结构，再看数量、质量、组合与接触 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#6.6 情节相似的判断步骤（王迁教授方法）\|6.6 情节相似判断]] |
| 混同原则 | 表达方式极有限时，避免通过保护表达间接垄断思想或功能 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#6.7 混同原则（Merger Doctrine）⭐\|6.7 混同原则]] |
| 场景原则 | 排除题材必然出现的标准元素，防止风格与类型垄断 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#6.8 场景原则（Scènes à Faire）\|6.8 场景原则]] |
| 复制权及非精确复制 | 输出不必逐字逐像素相同；仍须证明受保护表达被再现 | [[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#8.1 复制行为的构成\|8.1 复制行为]]；[[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#8.2 精确复制与非精确复制\|8.2 精确与非精确复制]] |
| 信息网络传播权 | 用户或平台向公众提供输出时，另行判断交互式网络传播 | [[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#12.2 信息网络传播权 ⭐⭐⭐\|12.2 信息网络传播权]] |
| 演绎行为 | 输出保留原作基本表达并形成新表达时，可能涉及改编等演绎权 | [[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#13.1 演绎行为的构成\|13.1 演绎行为]] |
| 直接与间接侵权 | 分开实施受控行为者与提供帮助、具有过错者 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#一、直接侵权与间接侵权的基本关系\|直接侵权与间接侵权]] |
| 侵权责任六步法 | 锁定行为—直接侵权—限制—间接责任—责任路径—结论 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#8.1 著作权侵权与责任六步法\|8.1 侵权与责任六步法]] |
| 救济比例 | 模型调整、停止服务等强措施须考虑侵权部分、替代措施与社会成本 | [[法书/03王迁-知产教程-重构版/著作权法✅/08著作权侵权及法律责任#5.3 销毁侵权复制品的比例限制 ⭐⭐\|5.3 救济的比例限制]] |

---

## 3. Jurisprudential Controversy Analysis｜法哲学争议分析（中文）

### 3.1 权利边界的第一功能：防止从“相似”滑向风格私有化

输出侵权的第一场争论发生在权利范围，而不是技术因果。著作权保护具体表达，却必须把思想、主题、事实、方法、风格、惯常元素和题材必然场景留给公众。若仅凭“像某位画家”认定侵权，先行创作者将获得对创作规律和审美语言的控制，后来者不仅不能复制作品，甚至不能在同一文化语法中继续创作。思想／表达二分因此不只是技术性过滤，而是一项反垄断原则：它防止私权封锁后续表达的生产条件。

但过滤不能走向另一极端。独创性经常存在于多个普通元素的独特选择、组合和安排；如果把面具、胸甲、姿态、光影和构图逐项拆成公有元素，整体仿制可能永远逃逸。正确方法是先排除确属公共或功能性的要素，再判断**剩余元素的具体组合**是否构成受保护表达，以及输出在数量、质量和结构关系上是否达到实质性相似。风格本身不受保护，不等于所有“风格化模仿”都安全；当所谓风格描述实际指向可识别的具体作品组合时，分析对象已经从风格进入表达。

### 3.2 黑箱中的认识正义：高度相似只能启动说明，不能自动锁定责任

传统“接触＋实质性相似”模式在模型场景中遇到信息不对称。权利人可以看到输出，却看不到训练清单、微调数据、系统提示和复现测试；要求其精确证明某个参数如何保存作品，等同于让权利在技术黑箱前失效。可是仅凭高度相似就让基础模型商承担责任，也可能误判：相似输出可能来自用户上传原图、接入商私自微调，甚至来自表达空间有限的独立生成。

更平衡的路径是**初步证明＋可推翻的说明责任**。权利人应先证明权属、受保护表达、高度对应、合理的接触可能以及稳定复现等外部事实。达到一定强度后，掌握信息的一方说明训练来源、微调主体、系统提示、去重措施和复现机制。该结构纠正证据不平等，但不把信息优势直接变成严格责任；结果相似启动解释，解释和技术证据再确定责任位于哪一层。

### 3.3 用户与平台之争：事实因果、行为控制与规范作者并不重合

用户输入提示，模型执行计算，平台交付结果，三者都是事实因果链的一部分。私法却需要进一步判断谁实施了专有权控制的行为、谁决定了侵权风险、谁从结果中选择并利用表达。一般性提示、私人查看与“上传原作—要求完整复刻—反复绕过限制—公开销售”之间存在巨大的规范距离。用户越能识别原作、定向要求复制并选择商业利用，其作为直接行为人的责任理由越强。

模型商也不能因用户点击按钮而当然退回中立工具地位。生成式服务与被动存储不同：服务商选择模型架构、训练或微调数据、系统提示、输出限制和投诉机制。但这种控制仍不足以推出每次输出都是平台的直接侵权。**控制能力应首先影响注意义务和过错，而不是自动重写直接侵权的行为要件。**只有平台主动提供特定作品复刻功能、植入定向系统提示、选择并以自身内容提供结果等情形，直接或共同实施的理由才显著增强。

### 3.4 生成链分责：责任应跟随“侵权能力是谁加入、谁能移除”

基础模型、微调模型、API 接入和传播平台不应被一个“平台”概念吞并。基础模型可能只提供通用能力；微调者用特定作者全集加入稳定模仿或复现能力；接入商可能修改系统提示并主动包装结果；用户最终选择、销售；传播平台再放大。按照合同名称分责会鼓励主体以“技术服务”自我标签逃避责任，按照财力分责又会把侵权法变成深口袋规则。

更具私法逻辑的标准是功能与控制：**谁把特定侵权能力加入链条，谁知道该能力，谁能以合理成本移除或限制它，谁就对相应风险承担更强义务。**基础模型商对无法预见的下游私自微调责任较弱；微调者对其注入的特定能力责任较强；接入商仅传递结果与主动添加复刻提示不同；用户明知并商业化与偶然得到相似结果也不同。责任强度随具体介入、知识和控制递增，而不是因主体类型一次性固定。

### 3.5 公法合规与私法责任：保护性规范只能有限转介

生成式 AI 监管规则强调数据来源、知识产权、内容标识和投诉机制。将这些规则完全排除在民事责任之外，会使行业注意标准失去作用；但把每项公法违规都直接转化为赔偿，又会绕过著作权法的专有权、因果关系和法源层级。适当路径是有限转介：只有当规范旨在保护可识别的私人版权、所防止的正是本案损害、违反义务与损害存在因果联系时，才可用于具体化过错。

例如，未添加 AI 标识可能妨碍溯源，却未必是复制原作的原因；收到权利人提供原图和稳定复现步骤后仍拒绝处理，与损害继续发生的联系则更直接。公法提供行为标准，私法仍负责决定权利是否受侵害、责任主体与赔偿范围。

### 3.6 推荐立场：输出先定权利，主体再按功能分责，救济由低到高升级

1. **表达审查。**明确原作品及权利基础，过滤思想、风格、事实、惯常与场景元素，评价剩余表达的数量、质量和组合。
2. **法律联系。**以接触可能、用户上传、训练或微调收录、特殊提示、稳定复现和生成记录建立联系。高度相似不是单独的责任结论。
3. **行为拆分。**分别列出用户提示与利用、基础模型能力、微调数据、API 系统提示、输出选择以及后续传播。
4. **责任路径。**直接侵权严格对应具体受控行为；间接责任须有基础侵权、实质帮助或诱导及相应过错。对掌握黑箱信息者可设置可推翻的说明责任，但不采每次输出的平台严格责任。
5. **救济阶梯。**先停止具体传播、保存日志、限制已验证的恶意提示和重复输出；再依复现稳定性、技术可行性及误伤评估去重、输出抑制或模型更新。只有较轻措施不足时，才进入更深模型调整。

### 3.7 输出责任矩阵｜Actor-by-Actor Allocation

| 主体 | 低责任事实 | 责任增强事实 | 首要责任问题 |
|---|---|---|---|
| 普通用户 | 一般提示、偶然相似、未发布 | 上传原作、指定复刻、绕过限制、选择并销售 | 是否实施生成、复制、改编或传播等直接行为 |
| 基础模型商 | 通用能力、无特定复现、合理去重与响应 | 知道稳定复现、以特定作品宣传、继续控制更新却不处理 | 是否直接参与；是否因具体知识和控制承担过错责任 |
| 微调者 | 使用独立、合法数据且无特定复现 | 用单一作者全集或盗版库加入可重复复刻能力 | 谁将特定侵权能力注入模型 |
| API 接入商 | 仅中性传递、无改动与选择 | 修改系统提示、私自微调、选择或包装输出为自有内容 | 实际功能是通道、帮助者还是内容提供者 |
| 商业利用者 | 未公开、无市场使用 | 印刷销售、广告利用、替代原作市场 | 末端直接利用与损害范围 |
| 传播平台 | 本页仅确认其承载／推荐事实 | 收到有效通知、反复传播、人工运营 | 具体知情与必要措施转入 Day 04 |

---

## 4. English Jurisprudential Analysis & Interview Corpus｜英文学理分析与面试语料

### 4.1 Protected Expression Before Technological Causation

The first inquiry in an AIGC infringement case is not whether the output was produced by a model or whether it looks generally similar to an earlier work. It is whether the similarity concerns protectable expression. Copyright must leave ideas, styles, genres, methods, standard elements, and scenes à faire available for subsequent creation. This exclusion performs an anti-monopolistic function: without it, an early creator could control the grammar of a genre rather than the author’s particular expression. At the same time, a court should not atomize a work so aggressively that an original combination of individually ordinary elements becomes unprotectable. The comparison must therefore focus on the selection, arrangement, and relational structure of the remaining expression.

Style imitation illustrates the point. An artistic style, taken at a high level of abstraction, should not become private property. Yet a defendant cannot avoid scrutiny merely by describing a near-reproduction of a particular composition as “stylistic.” Once the alleged style is specified through a distinctive mask, armour pattern, pose, lighting scheme, and spatial arrangement taken from an identifiable work, the legal object has shifted from an abstract method to concrete expression. The boundary protects both authorial entitlement and the expressive commons.

### 4.2 Evidentiary Justice in a Model Black Box

Traditional proof based on access and substantial similarity becomes difficult when training records, fine-tuning datasets, system prompts, and reproduction tests are controlled by different providers. Requiring the claimant to identify the precise parameter that encodes a work would make enforcement practically impossible. Conversely, treating high similarity as conclusive proof against the foundation-model provider would ignore alternative causes, including user uploads, downstream fine-tuning, constrained expressive choices, or independent generation.

A better structure combines an initial evidentiary threshold with a rebuttable burden of explanation. The claimant should identify the protected work, isolate its protectable expression, demonstrate a sufficiently close correspondence, and produce external facts suggesting access or stable reproduction. Once that threshold is met, the party with superior informational access should explain provenance, fine-tuning, safeguards, and the origin of the relevant system instructions. Similarity should trigger explanation, not automatic liability. This approach responds to epistemic inequality without converting informational control into strict liability.

### 4.3 Agency and Functional Allocation Across the Generation Chain

The user, model provider, fine-tuner, API integrator, and dissemination platform occupy different normative positions. A user who issues a general request and accidentally receives a similar image is not equivalent to a user who uploads the original, asks for an exact replica, circumvents safeguards, selects the result, and sells it. User liability should therefore be assessed at both ends of the transaction: targeted inducement at the input stage and deliberate selection, publication, or commercial exploitation at the output stage.

Model providers cannot automatically retreat behind the user’s click, because they design and control important parts of the generative environment. Yet control over a general-purpose system should not by itself make the provider the direct infringer of every unforeseeable output. Control is ordinarily more relevant to fault and preventive duties than to the basic definition of direct infringement. Responsibility should follow function: who introduced the particular infringing capability, who knew of it, who could remove it at proportionate cost, and who commercially exploited the resulting expression. This avoids both formal reliance on contractual labels and the economically crude rule that the deepest pocket must pay.

### 4.4 Preferred Liability and Remedy Framework

My preferred framework proceeds in four stages. First, the court should filter unprotected material and compare only protectable expression. Second, it should establish a legally relevant connection through access, uploaded references, training or fine-tuning evidence, special prompts, repeatability, and generation records. Third, it should allocate conduct across the chain and distinguish direct infringement from fault-based secondary responsibility. A rebuttable burden of explanation may correct informational asymmetry, but a provider should remain able to show independent downstream modification, unpredictability, and reasonable safeguards.

Remedies should then escalate from the least intrusive effective measure. Removing a published output, preserving logs, and blocking a verified malicious prompt may be appropriate before imposing dataset removal, output suppression, or model modification. A deeper intervention is justified only when reproduction is stable, the claimant’s evidence is precise, the provider retains meaningful control, and less restrictive measures are inadequate. Copyright remedies should prevent repeatable harm without transforming probabilistic systems into objects of absolute insurer liability or suppressing lawful criticism, parody, and independent creation.

### 4.5 Four-Paragraph Interview Answer｜四段式口述成稿

An AIGC output does not infringe merely because it resembles an existing work. The court must first identify protectable expression and exclude ideas, styles, facts, standard elements, merger, and scenes à faire. This filtering protects the public domain, but it should not ignore an original combination of ordinary elements. The relevant question is whether the output appropriates the author’s concrete selection and arrangement, not whether it shares the general atmosphere of a genre or artist.

The second difficulty is proof. A copyright owner can observe the output but normally cannot inspect the training corpus, fine-tuning data, system prompts, or model weights. I would therefore use a burden-shifting structure. The claimant should first establish ownership, protectable expression, close correspondence, and external facts suggesting access or stable repeatability. The provider or downstream developer should then explain the origin of the output and the safeguards used. Similarity may justify an explanation, but it should not automatically identify which actor in the model chain is liable.

The third step is functional allocation. A user who uploads an original work, requests an exact replica, circumvents restrictions, and commercially exploits the output presents the clearest direct liability case. A foundation-model provider should face stronger responsibility when it knowingly supplies or continues to control a stable reproduction capability. A downstream fine-tuner or API integrator may bear the principal responsibility if it introduced the relevant dataset or system prompt. Liability should follow the party that added, knew of, controlled, and exploited the particular risk—not simply the party labelled a “platform.”

Finally, remedies should be proportionate. A court should distinguish removing a published copy from preventing future generation. Targeted prompt blocking, logging, deduplication, output suppression, and model modification have very different costs and risks of overreach. The more intrusive the remedy, the stronger the required showing of stable reproduction, technical efficacy, specific notice, and inadequate alternatives. This framework protects authors against repeatable appropriation while preserving lawful style, independent creation, and innovation in general-purpose models.

### 4.6 Reusable Phrases｜可复用表达

- **protectable expression must precede technological causation** — 受保护表达判断先于技术因果判断
- **the anti-monopolistic function of the idea–expression dichotomy** — 思想表达二分的反垄断功能
- **to atomize a work beyond meaningful protection** — 将作品过度拆碎以至失去有效保护
- **similarity should trigger explanation, not automatic liability** — 相似只能启动说明，而非自动归责
- **a rebuttable burden of explanation grounded in informational control** — 以信息控制为基础的可推翻说明责任
- **responsibility should follow function rather than contractual labels** — 责任应跟随实际功能，而非合同标签
- **who introduced, knew of, controlled, and exploited the risk** — 谁加入、知悉、控制并利用风险
- **the least intrusive effective remedy** — 最小侵害的有效救济

### 一句立场句｜One-sentence Position

> I would begin with protectable expression, use stable reproduction and informational proximity to structure proof, allocate liability by each actor’s actual function and control, and escalate remedies only in proportion to demonstrated and repeatable harm.

---

## 5. Future Testing Angle｜未来面试追问

### Question 1

**中文：**如果一张生成图在整体观感上高度接近某画家，但没有复制任何一幅具体作品的构图，著作权法是否应保护“风格”？若不保护，权利人还有哪些不应被混同为版权的制度路径？

**English:** If a generated image strongly resembles an artist’s overall style but does not reproduce the composition of any identifiable work, should copyright protect the style itself? If not, what other legal avenues might remain, and why should they not be collapsed into copyright?

### Question 2

**中文：**权利人证明特定提示可稳定复现其作品后，基础模型商主张复现能力由下游微调者加入。请设计举证责任、主体分责和救济顺序，避免既让黑箱阻断维权，又把模型商变成严格责任保险人。

**English:** Once a claimant proves that a specific prompt reliably reproduces the work, the foundation-model provider argues that the capability was introduced by a downstream fine-tuner. Design a framework for burden shifting, actor-specific liability, and remedial sequencing that neither allows the black box to defeat enforcement nor turns the model provider into a strict-liability insurer.

---

## 6. 复习抓手

- **先表达、后相似**：相似对象必须是受保护表达，风格标签不能替代比对。
- **先初证、后说明**：权利人建立外部事实，信息控制者承担可推翻说明责任。
- **先行为、后主体**：不按“平台／用户”标签分责，按谁加入、控制、利用特定风险分责。
- **先轻后重**：删除具体输出与改模型是不同强度的救济。
- **与下一页交接**：一旦问题变成传播平台何时知情、是否过滤、怎样反通知，即进入 Day 04。

