#!/usr/bin/env python3
"""
自动检索本机论文 PDF 并无冗余软链接至 Obsidian 库的 PDF 目录
专为 Obsidian PDF++ 插件设计：零磁盘空间占用，实现双链点击即时分屏高亮跳转
"""
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
VAULT_PDF_DIR = REPO_ROOT / "vault" / "知识产权" / "PDF"
NOTES_DIR = REPO_ROOT / "vault" / "知识产权" / "论文库"

VAULT_PDF_DIR.mkdir(parents=True, exist_ok=True)

search_dirs = [
    Path.home() / "Downloads",
    Path.home() / "Documents",
]

all_pdfs = []
print("🔍 正在全盘扫描可能的法学论文 PDF 文件...")
for s_dir in search_dirs:
    if not s_dir.exists():
        continue
    for root, _, files in os.walk(s_dir):
        if any(skip in root for skip in ["Obsidian Vault", ".git", "node_modules", "runtime"]):
            continue
        for f in files:
            if f.lower().endswith(".pdf"):
                all_pdfs.append(Path(root) / f)

def normalize_title(t: str) -> str:
    t = re.sub(r'__[\w\-]+$', '', t)
    t = re.sub(r'[\s_]+', '', t)
    t = re.sub(r'[《》【】“”\"\'：:？\?——\-\(\)（）·\.]', '', t)
    return t.lower()

norm_pdf_map = {}
for p in all_pdfs:
    norm = normalize_title(p.stem)
    if norm not in norm_pdf_map:
        norm_pdf_map[norm] = p

print(f"✓ 扫描到 {len(all_pdfs)} 个 PDF，提炼出 {len(norm_pdf_map)} 个唯一标准标题。")

linked_count = 0
notes = sorted(list(NOTES_DIR.glob("*.md")))
for note in notes:
    norm_note = normalize_title(note.stem)
    target_pdf = None
    if norm_note in norm_pdf_map:
        target_pdf = norm_pdf_map[norm_note]
    else:
        for norm_p, p_path in norm_pdf_map.items():
            if norm_note in norm_p or norm_p in norm_note:
                target_pdf = p_path
                break
    if target_pdf and target_pdf.exists():
        symlink_name = f"{note.stem}.pdf"
        symlink_path = VAULT_PDF_DIR / symlink_name
        if symlink_path.is_symlink() or symlink_path.exists():
            symlink_path.unlink()
        try:
            symlink_path.symlink_to(target_pdf.resolve())
            linked_count += 1
        except Exception as e:
            pass

print(f"🎉 链接完成！成功建立 {linked_count}/{len(notes)} 篇论文的 PDF 软链接至 vault/知识产权/PDF/")
