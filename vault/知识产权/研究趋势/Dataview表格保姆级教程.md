---
type: "教程"
scope: "Obsidian Dataview"
updated: "2026-07-09"
---

# Dataview 表格保姆级教程

## 1. 这东西到底是什么
Dataview 表格不是普通 Markdown 表格，而是 Obsidian 里的“自动查询表”。

它会从每篇论文最上面的属性里读取信息，比如：

```yaml
teacher: "冯术杰"
year: "2019"
school: "清华大学"
research_area:
  - "搭便车规制"
  - "反不正当竞争法制度建构"
```

然后自动生成表格。以后新增论文，只要属性写对，表格会自动更新。

## 2. 第一次使用前要做什么
1. 打开 Obsidian 设置。
2. 找到“第三方插件”或“Community plugins”。
3. 关闭安全模式。
4. 搜索并安装 `Dataview`。
5. 启用 `Dataview`。
6. 如果要使用“导师-年份矩阵”“导师-研究领域矩阵”，进入 Dataview 设置，打开 `Enable JavaScript Queries`。

如果没有安装 Dataview，代码块只会显示成一段代码，不会变成表格。

## 3. 最简单的使用方式
打开这个页面：

[[研究趋势/年度论文索引|年度论文索引]]

然后切换到阅读模式。

如果你看到的是代码，不是表格，通常是这三个原因：

- 没有安装 Dataview。
- Dataview 没有启用。
- 页面还在编辑模式，没有切到阅读模式。

## 4. 普通 Dataview 表格怎么看
例如：

```dataview
TABLE year AS 年份, teacher AS 导师, research_area AS 研究领域
FROM "知识产权/论文库"
SORT year DESC
```

意思是：

- `TABLE`：我要做一个表。
- `year AS 年份`：显示 `year` 属性，列名叫“年份”。
- `teacher AS 导师`：显示 `teacher` 属性，列名叫“导师”。
- `research_area AS 研究领域`：显示研究领域。
- `FROM "知识产权/论文库"`：只从 `papers` 文件夹里找论文。
- `SORT year DESC`：按年份从新到旧排序。

你不用背语法，只要知道每一行大概在干什么。

## 5. 按导师看
适合回答：这个老师写了哪些文章，集中在哪些方向？

```dataview
TABLE rows.year AS 年份, rows.file.link AS 论文, rows.research_area AS 研究领域, rows.original_keywords AS 原文关键词
FROM "知识产权/论文库"
GROUP BY teacher
SORT key ASC
```

看法：

- 每一组就是一个导师。
- `年份` 看研究时间。
- `论文` 点进去看具体论文卡片。
- `研究领域` 看这个老师的主线。
- `原文关键词` 只是证据，不要把它当主分类。

## 6. 按年份看
适合回答：某一年哪些老师在写什么？

```dataview
TABLE rows.teacher AS 导师, rows.file.link AS 论文, rows.research_area AS 研究领域
FROM "知识产权/论文库"
GROUP BY year
SORT key DESC
```

看法：

- 先看最新年份。
- 再看同一年里哪些导师集中写数据、AI、平台、商标、竞争法。
- 如果某个方向在多个老师、多篇文章里出现，就是更值得关注的趋势。

## 7. 筛选某个导师
把 `冯术杰` 换成你要看的导师即可。

```dataview
TABLE year AS 年份, file.link AS 论文, research_area AS 研究领域, original_keywords AS 原文关键词
FROM "知识产权/论文库"
WHERE teacher = "冯术杰"
SORT year DESC
```

看法：

- 从上往下看，就是这个导师从新到旧的研究脉络。
- 如果近年反复出现同一 `research_area`，这就是稳定研究方向。

## 8. 筛选某个研究方向
把 `搭便车规制` 换成你要看的方向即可。

```dataview
TABLE year AS 年份, teacher AS 导师, file.link AS 论文, original_keywords AS 原文关键词
FROM "知识产权/论文库"
WHERE contains(research_area, "搭便车规制")
SORT year DESC
```

看法：

- 这个表不是看一个老师，而是看同一方向下有哪些老师、哪些论文。
- 适合找申请选题：如果一个方向既有导师论文，又能连接多个领域，就更好展开。

## 9. 筛选某个学校
把学校名换成清华大学、上海交通大学等。

```dataview
TABLE year AS 年份, teacher AS 导师, file.link AS 论文, research_area AS 研究领域
FROM "知识产权/论文库"
WHERE school = "清华大学"
SORT teacher ASC, year DESC
```

看法：

- 适合比较同一学校内部不同老师的研究分布。
- 申请时可以先看目标学校，再看导师，再看方向。

## 10. 导师-年份矩阵怎么看
这个表可与 [[研究趋势/年度论文索引|年度论文索引]] 对照使用。

横轴是年份，纵轴是导师。

看法：

- 某个导师近年格子里有论文，说明近期还在活跃发文。
- 某个导师某一年突然转向数据、AI、平台，就要回到具体论文看原因。
- 空格不是坏事，只是当前库里还没有收录该年份论文。

## 11. 导师-上位领域矩阵怎么看
横轴是九个统一上位领域，纵轴是导师。

看法：

- 一个格子显示 `2 篇`、`3 篇`，说明这个方向在该导师名下反复出现。
- 多个导师都在同一个方向下有论文，说明这个方向可能是热点。
- 申请时优先挑“导师本人持续写 + 学界也有人共同关注”的方向。

## 12. 你现在最该怎么用
建议按这个顺序：

1. 打开 [[研究趋势/年度论文索引|年度论文索引]]。
2. 先看“导师分组”。
3. 找到目标导师，例如孔祥俊、冯术杰、崔国斌。
4. 先看该导师反复出现的 `trend_domain`，再用 `research_area` 看具体子议题。
5. 点进论文卡片，看“问题的提出/分析/解决”。
6. 再打开 [[研究趋势/学者观点索引|学者观点索引]]，看这个方向还连接了哪些作者和论文。

## 13. 常见故障
- 表格不显示：安装并启用 Dataview，切换阅读模式。
- DataviewJS 不显示：在 Dataview 设置中打开 JavaScript 查询。
- 表格空白：检查 `FROM "知识产权/论文库"` 是否对应论文文件夹。
- 某篇论文没出现：检查论文属性里有没有 `teacher`、`year`、`trend_domain`、`research_area`。
- 年份排序怪：确认 `year` 写成统一的年份，例如 `"2019"` 或 `2019`。

## 14. 最重要的一句话
Dataview 表格不是让你手动维护表格，而是让你维护每篇论文的属性；属性越规范，表格和图谱就越自动、越好用。
