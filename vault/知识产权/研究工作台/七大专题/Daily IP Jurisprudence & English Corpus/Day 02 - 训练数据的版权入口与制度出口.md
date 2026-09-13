---
type: daily_ip_jurisprudence_corpus
day: 2
topic: "训练数据的版权入口与制度出口：复制权、权利限制与许可"
date: 2026-08-17
status: completed
language: zh-en
source_scope: "专题02 + 王迁知产教程重构版 + 官方法源校核"
---

# Day 02｜训练数据的版权入口与制度出口

> [!abstract] 今日命题
> 本专题不笼统追问“机器能否学习”，而是把训练拆成数据取得、数据集制作、投喂、参数学习和可能的记忆化：**哪些节点属于复制权控制的行为；如果进入专有权范围，应由现行权利限制、专门 TDM 例外，还是许可与补偿机制提供制度出口？**

> [!info] 系列位置
> 共通理论与防重复规则见[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/00 - AIGC版权责任链总图：训练、输出与平台|AIGC版权责任链总图]]。本页止于模型形成及训练救济；具体输出侵权转入[[知识产权/研究工作台/七大专题/Daily IP Jurisprudence & English Corpus/Day 03 - AIGC输出侵权与生成链归责|Day 03]]。

## 0. 材料定位与现行法校核

### 本地材料

- 快速入门：[[知识产权/研究工作台/七大专题/02_大模型训练数据版权_快速入门]]
- 学说全景：[[知识产权/研究工作台/七大专题/02_大模型训练数据版权_学说争议全景]]
- 六阶段详版：[[知识产权/研究工作台/七大专题/02_大模型训练数据版权_六阶段逻辑合并]]
- 制度基础：[[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用]]、[[法书/03王迁-知产教程-重构版/著作权法✅/07对著作权的限制]]、[[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅]]

### 现行法底线（截至 2026-08-17）

1. 《著作权法》第 10 条第 1 款第 5 项将复制权界定为以印刷、复印、录音、录像、翻拍、数字化等方式将作品制作一份或者多份的权利。下载并长期保存受保护作品，原则上存在进入复制权范围的强理由；“训练目的不同”不能自动抹去前端副本。[中国人大网：《中华人民共和国著作权法》](https://www.npc.gov.cn/c2/c30834/202011/t20201119_308796.html)
2. 第 24 条列举合理使用情形并设置类似三步检验的附加边界，但没有明文规定一般性的文本与数据挖掘例外。将商业大模型训练直接纳入现有条文，属于有争议的解释问题，不能当作已经明确的现行规则。
3. 《生成式人工智能服务管理暂行办法》第 7 条要求使用具有合法来源的数据和基础模型，涉及知识产权的不得侵害他人依法享有的知识产权。**“来源合法”与“获得版权许可”仍是两层问题**：公开可访问、合法购买或未违法获取，不当然授予制作训练副本的许可。[中国网信网：《生成式人工智能服务管理暂行办法》](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm?mhEnc=3d537d9731a15cfadd38e2d9f63e5491&mhType=2&pageId=1171717&publicId=3839645904b1b311ef1a85b3f3def5ca09f9&websiteId=602694&wfwfid=120336)
4. 因此，面试中应区分三种表述：**现行法的可确认底线、解释论上的可能路径、立法论上的制度建议。**尤其不要把“非作品性使用”“传播性复制”或“商业训练法定许可”误说成中国现行法已经采纳。

---

## 1. Core Institution & Terminology｜核心制度与术语

这里只列训练专题新增概念；思想／表达、法定权利、比例原则等共通概念见总图。

| 中文制度／知识点    | 精确含义                                            | Precise English Terminology                                      |
| ----------- | ----------------------------------------------- | ---------------------------------------------------------------- |
| 训练语料／训练数据   | 用于预训练、微调或优化模型的数据；其中可能包含作品、事实、个人信息及非版权材料         | training corpus; training data                                   |
| 数据取得        | 抓取、下载、购买、接收或调用数据的前端行为；取得合法不等于版权授权               | data acquisition; lawful access                                  |
| 公开可访问       | 无需绕过访问限制即可接触，不等同于作品进入公有领域或默示许可                  | publicly accessible; not necessarily licensed                    |
| 数据集制作       | 将资料下载、清洗、切分、标注、去重并长期保存的行为组合                     | dataset creation; corpus compilation                             |
| 数据投喂        | 将预处理数据输入模型计算流程，可能产生内存、缓存或中间副本                   | data ingestion                                                   |
| 参数／模型权重     | 训练后形成的数值结构；是否为原作复制件取决于能否固定、再现受保护表达，不能只凭“含有信息”判断 | model parameters; model weights                                  |
| 记忆化         | 模型对训练样本中的具体表达保留到足以被触发、恢复或稳定复现的程度                | memorization                                                     |
| 过拟合         | 模型过度贴合训练样本，降低泛化并提高复现具体样本的可能                     | overfitting                                                      |
| 复制权         | 控制将作品制作一份或多份的法定专有权；数字化副本可进入其范围                  | right of reproduction                                            |
| 临时／中间复制     | 为技术过程产生、持续时间短且通常无独立利用价值的副本；我国法下是否及如何排除控制存在争议    | temporary copy; intermediate copy                                |
| 非作品性／非表达性使用 | 主张训练利用统计规律、语言结构而非供人感知的作品表达，因而不进入专有权范围           | non-expressive use; non-consumptive use                          |
| 文本与数据挖掘     | 以自动化方法分析大量文本或数据，发现模式、关联和信息                      | text and data mining (TDM)                                       |
| 合理使用／权利限制   | 中国法下更稳妥地表述为法定限制与例外；不能不加说明地移植美国开放式四要素 fair use   | statutory limitations and exceptions; fair use in the U.S. sense |
| 三步检验法       | 例外须限于特定情形，不与作品正常利用冲突，不不合理损害权利人合法利益              | the three-step test                                              |
| 自愿许可        | 权利人与训练者经协商授权并确定报酬、范围和条件                         | voluntary licensing                                              |
| 法定许可        | 无需事前同意但须依法付酬的责任规则；是否用于商业训练属于立法建议                | statutory licence; compulsory licence                            |
| 集体管理        | 由组织集中许可、收取并分配使用费，以降低大规模交易成本                     | collective rights management                                     |
| 选择退出／权利保留   | 默认允许特定使用，但权利人可通过机器可读方式保留权利或拒绝训练                 | opt-out; reservation of rights                                   |
| FRAND 条件    | 公平、合理、无歧视的许可条件，用于约束关键数据控制者的市场力量                 | fair, reasonable and non-discriminatory (FRAND) terms            |
| 机器遗忘        | 试图消除特定训练样本对模型的影响；目前首先是待验证的技术性救济，而非当然可执行的法律答案    | machine unlearning                                               |

### 1.1 一条不混淆的审查顺序

`来源与取得手段 → 数据集副本 → 投喂中的临时副本 → 参数是否可再现表达 → 权利限制 → 许可或补偿 → 删除、遗忘或输出抑制`

---

## 2. 王迁教程具体知识点｜Targeted Reading Map

| 本专题基础知识 | 具体用法 | 王迁教程入口 |
|---|---|---|
| 专有权只控制特定行为 | 先识别下载、长期存储、临时缓存等行为，不从“AI有益／有害”直接跳到结论 | [[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#1.1 专有权控制特定行为\|1.1 专有权控制特定行为]] |
| 复制行为三要素 | 检验有形载体再现、相对稳定固定和新复制件；数据集长期保存最典型 | [[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#8.1 复制行为的构成\|8.1 复制行为的构成]] |
| 数字环境复制 | 说明下载、服务器存储和数字化同样可能产生复制件 | [[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#8.5 数字环境中的复制\|8.5 数字环境中的复制]] |
| 临时复制争议 | 王迁路径承认技术上可能构成复制，倾向通过合理使用等制度排除不合理控制；不能把技术副本直接等同侵权 | [[法书/03王迁-知产教程-重构版/著作权法✅/04著作权的内容与利用#8.6 理论研究：临时复制 ⭐⭐⭐\|8.6 临时复制]] |
| 限制的正当性 | 解释交易成本、公众获取、后续创新为何可能要求限制专有权 | [[法书/03王迁-知产教程-重构版/著作权法✅/07对著作权的限制#1.1 著作权限制的必要性与正当性\|1.1 限制的必要性与正当性]] |
| 三步检验法 | 检验未来 TDM 例外是否限定场景、是否冲突正常利用、是否过度损害作者 | [[法书/03王迁-知产教程-重构版/著作权法✅/07对著作权的限制#1.2 三步检验法（Three-Step Test）⭐⭐\|1.2 三步检验法]] |
| 合理使用与法定许可 | 区分“无需许可且无需付费”与“无需许可但须付费”的风险分配 | [[法书/03王迁-知产教程-重构版/著作权法✅/07对著作权的限制#1.3 合理使用与法定许可的区分 ⭐⭐\|1.3 合理使用与法定许可]] |
| 科研合理使用 | 检验现行科研条款的目的、主体、数量与使用范围，避免直接等同于商业训练 | [[法书/03王迁-知产教程-重构版/著作权法✅/07对著作权的限制#2.5 教学、科研中的合理使用（第22条第6项）\|2.5 教学、科研中的合理使用]] |
| 法定许可原理 | 为商业训练的付酬型制度建议提供财产规则／责任规则基础 | [[法书/03王迁-知产教程-重构版/著作权法✅/07对著作权的限制#3.1 法定许可的基本原理\|3.1 法定许可基本原理]] |
| 禁止规避技术措施 | 分析绕过付费墙、访问控制或机器可读拒绝信号时的独立违法风险 | [[法书/03王迁-知产教程-重构版/著作权法✅/07对著作权的限制#4.2 禁止规避技术措施\|4.2 禁止规避技术措施]] |
| 数据库与汇编保护 | 区分单篇作品版权与数据库选择、编排的独创性，不把“数据”整体等同作品 | [[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#17.1 汇编作品的定义\|17.1 汇编作品]]；[[法书/03王迁-知产教程-重构版/著作权法✅/03著作权的客体#17.4 数据库的特殊保护 ⭐\|17.4 数据库保护]] |
| 技术改变成本结构 | 把海量许可、机器复制和权利人维权的成本变化纳入制度设计，而非代替法条解释 | [[法书/03王迁-知产教程-重构版/著作权法✅/02著作权法律制度概述✅#4.2 技术发展对著作权制度的影响 ⭐⭐⭐\|4.2 技术改变成本结构]] |

---

## 3. Jurisprudential Controversy Analysis｜法哲学争议分析（中文）

### 3.1 第一层争议不是“自由还是版权”，而是在哪一个规范层放行

三条主要路径给训练自由寻找了不同的法理位置。**非作品性使用说**认为模型利用的是统计规律而非供人阅读、欣赏的具体表达，因此训练原则上不进入专有权；**复制权功能重构说**承认技术副本存在，但主张复制权只应控制具有传播、公众接触或表达替代风险的副本；**严格入口说**则坚持先依现行复制权判断下载、存储和投喂，再在权利限制或新制度中决定是否放行。

这不是措辞差异，而是法治方法之争。如果在构成要件层放行，训练者获得较强的事前确定性，权利人必须证明训练利用了表达或产生传播风险；如果先认定复制再讨论例外，法定权利的边界更稳定，但海量技术副本会把大量正常计算先推入“未经许可”的状态。王迁教程对临时复制的分析提示了一条保守而清晰的路径：**技术上形成副本不等于最终侵权；但排除控制应当有权利限制或明确制度依据，而不宜只凭产业价值悄然增加复制权要件。**

### 3.2 “机器学习规律”说明了使用目的，却未完全回答副本的权利入口

训练与向公众提供电子书确有本质差异。前者通常以建立统计关联和生成能力为目的，不让人直接消费原作；这削弱了作者控制此类利用的功能理由，也解释了为何思想、事实和语言规律必须保持自由。但版权法控制的是法定行为，不只是行为人的最终目的。若企业先把整套付费图片库长期复制到服务器，之后再分析规律，**后端目的的非表达性不能自动使前端副本从未存在。**

因此，“机器像人一样学习”的类比只能证明训练具有值得保护的社会功能，不能直接完成法律定性。人阅读一本合法购买的书通常不制作可独立利用的海量数字副本；模型开发者却可能同时建立可检索、可复用、可交易的语料基础设施。较好的分析单位不是抽象的“学习”，而是每个副本的持续时间、可回取性、独立用途、取得方式以及与输出复现的关系。

### 3.3 权利限制的核心是市场失灵，而不是“技术越先进越应免费”

合理使用的最强理由是交易成本：通用模型可能涉及数以亿计的权利人，逐一发现、谈判和定价会使许可市场无法形成。若单篇作品只是可替换样本，训练产生重大社会增益，又不替代作品的消费或许可市场，允许某些训练可能增加总福利。可是市场失灵不能成为永久免费使用的口号。专业数据库、特定作者全集、可机器识别的权利保留以及已经成熟的训练许可市场，会显著降低交易成本；此时继续免费使用可能不是纠正市场失灵，而是把数据成本转嫁给创作者。

这又产生分配正义问题。单纯功利主义可能只看模型带来的总创新，却忽略收益与成本分布：少数大型企业掌握算力、数据和下游市场，分散作者缺乏议价能力；强制逐一许可又可能让大型内容平台垄断高质量数据并排斥中小模型企业。真正的制度目标不是在“作者”与“AI产业”之间选边，而是防止任何一方利用结构性优势把全部交易成本和风险外部化给另一方。

### 3.4 财产规则、责任规则与选择退出：谁承担寻找和拒绝的成本

事前自愿许可是一项**财产规则**：未经作者同意不得使用，最能保护自治，却要求训练者找到数量巨大的权利人。法定许可是一项**责任规则**：可以先使用但必须付酬，降低反垄断性的拒绝和孤儿作品成本，却把定价权部分交给国家或集体组织。选择退出把默认规则反转：作者未声明时允许训练，作者需要自行发现、表达拒绝并监督执行。

三者的深层争点是搜索成本由谁承担。默认禁止让模型开发者寻找作者；默认允许让作者寻找训练者；法定许可让管理机构承担归集与分配。没有任何方案能消灭成本，只能转移成本。因此，一项正当的制度必须同时回答：谁最接近信息、谁最能标准化权利声明、谁从使用中获益、谁最能承受错误，以及作者退出后技术上能否真正停止未来利用。

### 3.5 透明度是一种认识正义，而不只是附属合规

训练数据、模型测试和复现记录集中在开发者一侧。如果要求作者先证明其作品位于不可见的数据集中，再允许其请求说明，实体权利会因证据不可得而失效。透明度的法理基础不是惩罚企业掌握技术，而是**证据接近与认识正义**：最能控制信息的一方应承担相称的来源记录、保存和说明责任。

但说明责任不应变成公开全部语料、参数和商业秘密的无限义务。最小充分透明度可以包括来源类别、取得时间、许可状态、权利保留识别方式、去重与复现测试，以及在权利人完成初步证明后的定向核验。它的功能是使权利、例外与退出可被执行，而不是用“黑箱”本身推定侵权。

### 3.6 推荐立场：现行法上分节点审查，立法上类型化设置出口

我的立场分成解释论与立法论两层：

1. **现行法解释。**长期、可回取的数据集副本通常应先按复制权审查；训练目的非表达、参数不含可恢复原文，不能自动否定前端复制。纯临时、无独立利用价值的技术副本具有更强的排除控制理由，但应明确区分“构成复制”与“因权利限制而不侵权”。现行第 24 条没有一般 TDM 例外，商业大模型训练能否进入既有类型不宜被表述为定论。
2. **立法论设计。**应按来源、主体、数据集中度、许可可得性和输出复现风险设置分层出口：合法取得且非营利的科研 TDM 可获得较宽例外；通用商业训练可考虑机器可读权利保留、合理透明度和集体付酬的组合；已有集中许可的数据库、特定作者定向训练、盗版来源、绕过技术措施和高复现风险应获得较窄空间。
3. **许可结构。**大型模型企业和关键内容平台应承担较强的许可与谈判义务；中小企业、研究机构和开放社区需要集体管理、标准许可或公平数据接入降低门槛。制度不应以保护作者为名制造数据寡头，也不应以创新为名将创作投入变成免费公共原料。
4. **救济结构。**停止未来抓取、删除原始语料、限制特定输出、机器遗忘与赔偿不是同一措施。法院应依可执行性和比例原则逐级选择，不能在技术上无法验证时把“模型已经遗忘”写成空洞命令。

### 3.7 本专题终局表｜What Belongs Here

| 事实 | 本专题结论方向 | 转交其他专题的部分 |
|---|---|---|
| 抓取公开网页 | 公开访问不等于授权；继续查作品性、复制、访问限制和例外 | 输出是否相似转 Day 03 |
| 下载盗版电子书库 | 来源恶劣、主观过错和合法替代可得性削弱免责与合理使用 | 用户传播盗版输出另行判断 |
| 长期保存付费图片库 | 最典型的稳定数字副本；许可市场可得性强 | 不由模型通常创新输出而洗白 |
| 数据只短暂进入缓存 | 进入临时复制与权利限制争议；不能只凭“短暂”自动免责 | 与平台缓存安全港不要混同 |
| 模型参数不能恢复表达 | 削弱参数自身是复制件和市场替代的理由 | 不否定前端数据集曾发生复制 |
| 特定提示可稳定复现原作 | 会削弱非作品性、低风险训练的正当性并影响救济 | 具体侵权与主体归责由 Day 03 完成 |
| 作者声明退出 | 先判断其法源、机器可读性、训练前后时点和执行可能 | 平台收到具体侵权通知由 Day 04 处理 |

---

## 4. English Jurisprudential Analysis & Interview Corpus｜英文学理分析与面试语料

### 4.1 The Proper Location of Training Freedom

The central controversy is not simply whether copyright should favour authors or artificial intelligence. It concerns the doctrinal location at which training freedom should be recognized. A non-expressive-use theory excludes training from the scope of copyright because the model extracts statistical regularities rather than consuming protected expression. A functional theory of reproduction accepts that technical copies exist but argues that copyright should control only copies that expose the public to the work or create a meaningful substitution risk. A stricter approach first characterizes downloading and storage under the existing reproduction right, and then seeks an exception, licence, or legislative reform. Each route allocates uncertainty and the burden of justification differently.

In my view, the strictly sequential approach is the sounder interpretation of current Chinese law. A non-expressive purpose may be highly relevant to an exception, but it does not retroactively erase a durable copy placed on a training server. Likewise, the fact that model weights do not contain a readily recoverable image does not prove that no copy was made during dataset construction. This does not mean that every technical copy should attract liability. It means that the law should distinguish the scope of the right from the justification for limiting that right, rather than silently rewriting the definition of reproduction in response to industrial pressure.

### 4.2 Market Failure, Distribution, and the Limits of Free Use

The strongest justification for a training exception is market failure. General-purpose models may require millions of works owned by dispersed and frequently unidentifiable right holders. Individual negotiation can therefore consume more resources than the value of any single transaction, even where both sides would prefer a licence. Where the training is non-consumptive, produces substantial social value, and does not substitute for the market of the works, an exception may improve welfare by overcoming prohibitive transaction costs.

However, transaction costs are contingent facts, not a permanent entitlement to free inputs. They fall when a professional database has a centralized licensor, when a machine-readable reservation is available, or when a mature training-licensing market emerges. At that point, free use may cease to correct market failure and begin to externalize production costs onto creators. A complete analysis must therefore include distributive justice. The issue is not only whether society receives a more capable model, but also whether concentrated technology firms capture the gains while dispersed authors bear the uncompensated cost of producing the training material.

### 4.3 Property Rules, Liability Rules, and Opt-Out Systems

Voluntary licensing, statutory licensing, and opt-out regimes are different allocations of search and error costs. An ex ante consent requirement protects authorial autonomy but obliges the developer to locate an enormous number of right holders. A statutory licence permits use upon payment and reduces holdout and orphan-work problems, but it replaces some private control with administered pricing. An opt-out system lowers developers’ search costs by placing the initial burden on authors to discover the use, express a reservation, and verify compliance. None of these systems eliminates cost; each assigns it to a different institution and social group.

The legitimate choice should depend on informational proximity, bargaining power, and the reversibility of error. A party that controls training records is better placed to preserve and explain provenance. A large developer is better placed than an individual author to implement standardized rights-reservation protocols. Conversely, a mandatory licensing system may entrench large collecting organizations or data platforms if smaller developers cannot afford access. The law should therefore combine differentiated exceptions, collective mechanisms, and competition-sensitive access duties rather than impose one uniform rule on research institutions, start-ups, foundation-model firms, and concentrated content databases.

### 4.4 Preferred Framework

I would separate interpretation from reform. Under current law, durable and retrievable dataset copies should ordinarily be assessed under the reproduction right, while genuinely temporary and technically necessary copies present a stronger case for limitation. China’s current statutory list does not expressly provide a general text-and-data-mining exception, so the legality of mass commercial training should not be presented as settled. Legislatively, I would support a tiered system: a relatively broad exception for lawfully accessed, non-commercial research; a transparent and machine-readable reservation or remuneration mechanism for general commercial training; and a much narrower space for pirated sources, circumvention, concentrated licensable databases, author-specific imitation, and models with a demonstrated propensity to reproduce protected expression.

The governing principle is that copyright should neither grant authors control over facts, styles, and statistical regularities nor allow commercial developers to convert durable copies into cost-free inputs merely by describing their purpose as learning. A defensible regime must preserve the distinction between expression and knowledge, while ensuring that the economic value generated by legally relevant uses is not allocated entirely by technological possession. Transparency is essential to this balance: it should operate as a proportionate burden of explanation, not as an automatic presumption of infringement or a demand to disclose every trade secret.

### 4.5 Four-Paragraph Interview Answer｜四段式口述成稿

Copyright analysis of AI training should begin by disaggregating the technological process. Data acquisition, dataset construction, temporary ingestion, parameter learning, and output reproduction are not a single legal act. A publicly accessible work is not necessarily licensed, a lawful purchase does not necessarily authorize the creation of a training corpus, and the absence of recoverable expression in the final weights does not prove that no copy was made at an earlier stage. The first task is therefore to identify the relevant copy and the exclusive right it may implicate.

The principal theoretical dispute concerns where the law should create room for machine learning. Non-expressive-use theories place training outside copyright because the model extracts patterns rather than communicates works. Functional theories narrow the reproduction right to copies that create expressive access or substitution risk. A stricter position treats durable digital copies as reproduction and asks whether a statutory limitation, licence, or new TDM exception should apply. I prefer the third route under current Chinese law because it preserves the legality principle: industrial importance should influence the design of an exception, not silently alter the elements of an existing right.

That said, a pure permission-based system is also unsatisfactory. General-purpose training creates severe transaction costs, and copyright should not enable millions of fragmented vetoes over socially valuable, non-consumptive analysis. Yet the market-failure argument weakens where a database has a centralized licensor, where an author-specific model directly competes with the author, or where a viable training market already exists. The proper inquiry is therefore type-specific and dynamic: it should consider lawful access, concentration of rights, availability of licences, commercial purpose, memorization, and output substitution.

My preferred reform would combine a broad exception for lawfully accessed non-commercial research with a transparent reservation or remuneration mechanism for general commercial training, while denying favourable treatment to pirated sources, circumvention, targeted imitation, and high-reproduction-risk models. This structure distributes costs more fairly than either universal permission or universal prohibition. It protects the public domain of facts and styles, reduces impossible transaction burdens, and still requires firms that commercialize durable uses of protected expression to internalize an appropriate share of the creative cost.

### 4.6 Reusable Phrases｜可复用表达

- **to disaggregate training into legally distinct acts** — 将训练拆解为不同法律行为
- **a non-expressive purpose does not retroactively erase a durable copy** — 非表达性目的不会反向抹去稳定副本
- **the doctrinal location of training freedom** — 训练自由在教义体系中的安放位置
- **transaction costs are contingent facts, not a permanent licence for free use** — 交易成本是可变事实，不是永久免费使用的许可证
- **to externalize the cost of creative production onto authors** — 将创作成本外部化给作者
- **property rules, liability rules, and the allocation of search costs** — 财产规则、责任规则与搜索成本配置
- **a proportionate burden of explanation grounded in evidentiary proximity** — 基于证据接近的比例说明责任
- **interpretive discipline and legislative innovation** — 解释论克制与立法创新

### 一句立场句｜One-sentence Position

> Under current law, I would assess durable training copies within the reproduction right and seek lawful exits through clearly defined limitations or licences; legislatively, I favour a tiered TDM regime that responds to transaction costs, market concentration, lawful access, and demonstrable substitution risk.

---

## 5. Future Testing Angle｜未来面试追问

### Question 1

**中文：**如果模型训练只提取统计规律，且最终参数不能恢复任何原作，为什么著作权人仍可控制训练前端的数字副本？请分别用“权利构成”“合理使用正当性”和“制度创新边界”作答。

**English:** If training extracts only statistical regularities and the final model cannot reproduce any source work, why should copyright owners retain control over the digital copies made at the input stage? Answer separately in terms of the scope of the right, the justification for an exception, and the limits of judicial innovation.

### Question 2

**中文：**在“事前许可、法定许可、选择退出”三种默认规则中，哪一种最适合通用商业模型？请说明你的方案把搜索成本、错误成本、定价权和退出后的技术执行分别配置给谁。

**English:** Which default rule—prior authorization, statutory licensing, or opt-out—is most defensible for general-purpose commercial models? Explain how your proposal allocates search costs, error costs, pricing authority, and the technical burden of implementing a later withdrawal.

---

## 6. 复习抓手

- **入口之争**：训练自由放在“不进入复制权”，还是“进入后适用例外”。
- **事实四问**：来源是否合法、数据是否集中、许可是否可得、模型是否复现。
- **制度三选**：财产规则保护同意，责任规则降低交易成本，opt-out 转移发现与拒绝成本。
- **推荐立场**：现行法上严格分节点；立法上按科研／商业、通用／定向、分散／集中、低复现／高复现分层。
- **与下一页交接**：本页只说明输入使用；某个输出是否侵权及谁负责，进入 Day 03。

