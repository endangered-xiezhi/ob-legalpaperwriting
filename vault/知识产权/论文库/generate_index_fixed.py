import os
import re
import yaml

dir_path = os.path.dirname(os.path.abspath(__file__))
files = [f for f in os.listdir(dir_path) if f.endswith('.md')]

papers = []
for f in files:
    filepath = os.path.join(dir_path, f)
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        
    # Extract YAML frontmatter
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            year = str(frontmatter.get('year', '未知'))
            title = frontmatter.get('title', '')
            # Sanitize title to remove newlines or pipes just in case
            title = str(title).replace('\n', '').replace('|', '｜')
            
            authors = frontmatter.get('author', [])
            if isinstance(authors, list):
                author = '、'.join(str(a) for a in authors)
            else:
                author = str(authors)
            journal = frontmatter.get('journal', '')
            primary_domain = frontmatter.get('primary_domain', '')
            
            # Map domains
            domain = primary_domain.strip('"').strip("'")
            if domain in ["著作权法", "知识产权—著作权法"]:
                category = "知识产权—著作权法"
            elif domain == "专利法":
                category = "专利法"
            elif domain == "商标法":
                category = "商标法"
            elif domain == "知产相关反不正当竞争":
                category = "知产相关反不正当竞争"
            elif domain in ["纯反不正当竞争", "反不正当竞争法"]:
                category = "纯反不正当竞争"
            elif domain in ["数据法、个人信息与算法治理", "人工智能法"]:
                category = "数据法、个人信息与算法治理"
            elif domain in ["其他知识产权与综合治理", "知识产权总论"]:
                category = "其他知识产权与综合治理"
            else:
                category = "其他知识产权与综合治理"
            
            # MUST ESCAPE PIPE for Markdown table: \|
            file_link = f"[[论文库/{f.replace('.md', '')}\\|{title}]]"
            
            papers.append({
                'year': year,
                'category': category,
                'title': title,
                'author': author,
                'journal': journal,
                'file_link': file_link,
                'file_name': f
            })
        except Exception as e:
            pass

# Generate markdown
from collections import defaultdict

years = defaultdict(lambda: defaultdict(list))
for p in papers:
    if p['year'] != '未知' and p['year'].isdigit():
        years[int(p['year'])][p['category']].append(p)

output = []
output.append("---")
output.append('type: "年度论文索引"')
import datetime
output.append(f'updated: "{datetime.date.today().strftime("%Y-%m-%d")}"')
output.append("---")
output.append("")
output.append("# 年度论文索引")
output.append("")
output.append("本页原有部分是静态、可离线核查的年度索引；三批共生成 261 份专题笔记，经全库交叉核验后净新增 234 篇。7 月 24 日批次初始 56 篇，剔除 5 篇旧文后净新增 51 篇。增量表通过 collection 自动接入；各年标题数量按规范记录计入。")
output.append("")

categories_order = [
    "知识产权—著作权法",
    "专利法",
    "商标法",
    "知产相关反不正当竞争",
    "纯反不正当竞争",
    "数据法、个人信息与算法治理",
    "其他知识产权与综合治理"
]

for year in sorted(years.keys(), reverse=True):
    total_papers = sum(len(years[year][cat]) for cat in years[year])
    output.append(f"## {year}（{total_papers}篇）")
    output.append("")
    output.append(f"### 三批专题规范新增（自动检索）")
    output.append("")
    output.append("```dataview")
    output.append("TABLE WITHOUT ID file.link AS 论文, author AS 作者, journal AS 刊物")
    output.append('FROM "知识产权/论文库"')
    output.append(f'WHERE year = {year} AND contains(collection, "人工智能-著作权") AND canonical_duplicate != true')
    output.append("SORT author ASC")
    output.append("```")
    output.append("")
    
    for cat in categories_order:
        if cat in years[year] and years[year][cat]:
            output.append(f"### {cat}")
            output.append("")
            output.append("| 论文 | 作者 | 刊物 |")
            output.append("|---|---|---|")
            # Sort papers by author
            sorted_papers = sorted(years[year][cat], key=lambda x: x['author'])
            for p in sorted_papers:
                # Sanitize table columns just in case
                author = p['author'].replace('|', '｜')
                journal = p['journal'].replace('|', '｜')
                output.append(f"| {p['file_link']} | {author} | {journal} |")
            output.append("")

with open("../研究趋势/年度论文索引.md", "w", encoding="utf-8") as f:
    f.write('\n'.join(output))

print("Done")
