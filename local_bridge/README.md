# LexTrace 本机桥接

服务只监听 `127.0.0.1`，不建立第二套论文数据库。普通导航保持只读；写入仅限爬虫创建的新样板和样板筛选状态。

- `GET /api/vault/version`：返回目录版本指纹，用于10秒自动更新检查。
- `GET /api/vault/navigation`：返回领域、争议、路径、最近新增、待整理和搜索索引。
- `GET /api/vault/note?path=`：仅返回元数据、摘要、标题目录、出链和反链，不返回全文。
- `GET /api/intake/items`：返回新采集的 Obsidian 样板。
- `POST /api/obsidian/open`：调用 Obsidian 打开原笔记。
- `POST /api/cnki/start`：把研究画像与期刊清单交给升级后的爬虫，并创建待审核样板。
- `POST /api/intake/screening`：仅更新 LexTrace 样板的纳入、排除或待定状态。
- `POST /api/citations/render`：根据 Obsidian 元数据生成法学脚注，不补猜缺失字段。

旧版模型调用、API密钥和自动写回接口均返回 `410 Gone`。路径检查限制在 `知识产权` 目录内。

打开原笔记时，服务会从本机 Obsidian 配置识别注册 vault ID，避免文件夹名与登记名称不一致；预览同时提供可复制的绝对本地路径。
