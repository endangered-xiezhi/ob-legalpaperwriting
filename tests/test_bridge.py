import tempfile
import time
import unittest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from local_bridge import server


DOMAIN_FILES = [
    ("01_著作权法.md", "知识产权—著作权法"),
    ("02_专利法.md", "专利法"),
    ("03_商标法.md", "商标法"),
    ("04_知产相关反不正当竞争.md", "知产相关反不正当竞争"),
    ("05_纯反不正当竞争.md", "纯反不正当竞争"),
    ("06_数据法、个人信息与算法治理.md", "数据法、个人信息与算法治理"),
    ("07_其他知识产权与综合治理.md", "其他知识产权与综合治理"),
]


def write_note(path: Path, metadata: str, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{metadata}\n---\n\n{body}\n", encoding="utf-8")


class BridgeIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.vault = Path(self.temporary.name) / "Obsidian Vault"
        self.knowledge = self.vault / "知识产权"
        self.original_vault = server.VAULT_ROOT
        self.original_knowledge = server.KNOWLEDGE_ROOT
        self.original_obsidian_config = server.OBSIDIAN_CONFIG_PATH
        server.VAULT_ROOT = self.vault
        server.KNOWLEDGE_ROOT = self.knowledge
        server.OBSIDIAN_CONFIG_PATH = Path(self.temporary.name) / "obsidian.json"
        server.OBSIDIAN_CONFIG_PATH.write_text(
            json.dumps({"vaults": {"test-vault-id": {"path": str(self.vault)}}}),
            encoding="utf-8",
        )
        for file_name, domain in DOMAIN_FILES:
            write_note(
                self.knowledge / "领域" / file_name,
                f'type: "知识产权领域索引"\nprimary_domain: "{domain}"',
                f"# {domain}\n\n## 领域边界\n测试边界。",
            )

    def tearDown(self) -> None:
        server.VAULT_ROOT = self.original_vault
        server.KNOWLEDGE_ROOT = self.original_knowledge
        server.OBSIDIAN_CONFIG_PATH = self.original_obsidian_config
        self.temporary.cleanup()

    def add_paper(self, name: str, domain: str, *, complete: bool = True, folder: str = "论文库") -> Path:
        metadata = [
            f'title: "{name}"',
            "author:",
            "- 测试作者",
            "year: 2026",
            f'primary_domain: "{domain}"',
            'source_txt: "/tmp/source.txt"',
            'review_status: "fulltext_verified"',
            'warning: ""',
        ]
        if complete:
            metadata.insert(4, 'journal: "测试法学"')
        path = self.knowledge / folder / f"{name}.md"
        write_note(
            path,
            "\n".join(metadata),
            f"# {name}\n\n## 原文摘要\n这是{name}的摘要。\n\n## 问题的提出\n测试。\n\n[[领域/01_著作权法|领域入口]]",
        )
        return path

    def test_navigation_separates_formal_pending_unclassified_and_archive(self) -> None:
        self.add_paper("规范论文", "知识产权—著作权法")
        self.add_paper("字段待补", "专利法", complete=False)
        self.add_paper("领域待归类", "著作权法")
        self.add_paper("归档论文", "商标法", folder="论文库/_archive")

        payload = server.navigation_payload()
        self.assertEqual(payload["stats"]["papers"], 3)
        self.assertEqual(payload["stats"]["formal"], 2)
        self.assertEqual(payload["stats"]["pending"], 1)
        self.assertEqual(payload["stats"]["unclassified"], 1)
        self.assertEqual(payload["stats"]["domains"], 7)
        self.assertFalse(any("归档论文" in note["title"] for note in payload["searchNotes"]))

    def test_version_changes_when_markdown_is_added(self) -> None:
        first = server.vault_version()["version"]
        time.sleep(0.002)
        self.add_paper("新增论文", "知识产权—著作权法")
        second = server.vault_version()["version"]
        self.assertNotEqual(first, second)

    def test_note_preview_omits_full_content_and_resolves_links(self) -> None:
        paper = self.add_paper("预览论文", "知识产权—著作权法")
        payload = server.note_payload(paper.relative_to(self.vault).as_posix())
        note = payload["note"]
        self.assertNotIn("content", note)
        self.assertIn("这是预览论文的摘要", note["summary"])
        self.assertTrue(note["headings"])
        self.assertEqual(note["localPath"], str(paper.resolve()))
        self.assertEqual(note["links"][0]["path"], "知识产权/领域/01_著作权法.md")

    def test_obsidian_uses_registered_vault_id(self) -> None:
        self.assertEqual(server.obsidian_vault_identifier(), "test-vault-id")

    def test_path_cannot_escape_knowledge_root(self) -> None:
        outside = self.vault / "outside.md"
        outside.parent.mkdir(parents=True, exist_ok=True)
        outside.write_text("outside", encoding="utf-8")
        with self.assertRaises(ValueError):
            server.safe_knowledge_path("outside.md")

    def test_intake_stub_is_visible_but_not_formal(self) -> None:
        path = self.knowledge / "论文库" / "新采集样板.md"
        write_note(
            path,
            '\n'.join([
                'schema_version: 2',
                'record_id: "CNKI-TEST-1"',
                'record_status: "intake"',
                'metadata_status: "ready"',
                'screening_status: "pending"',
                'analysis_status: "not_started"',
                'citation_status: "metadata_ready"',
                'title: "新采集样板"',
                'author:',
                '  - "测试作者"',
                'year: "2026"',
                'journal: "中国法学"',
                'issue: "3"',
                'page_range: "10-20"',
                'source_pdf: "/tmp/source.pdf"',
                'review_status: "intake_pending"',
                'warning: ""',
            ]),
            "<!-- LEXTRACE:GENERATED-STUB -->\n\n# 新采集样板\n\n## 原文摘要\n测试摘要。",
        )
        payload = server.navigation_payload()
        self.assertEqual(payload["stats"]["intake"], 1)
        self.assertEqual(payload["stats"]["formal"], 0)
        self.assertEqual(payload["intake"][0]["recordId"], "CNKI-TEST-1")

        result = server.update_intake_screening(
            path.relative_to(self.vault).as_posix(),
            "included",
            "符合研究画像",
        )
        self.assertTrue(result["ok"])
        updated = path.read_text(encoding="utf-8")
        self.assertIn('screening_status: "included"', updated)
        self.assertIn('screening_reason: "符合研究画像"', updated)

    def test_legal_citation_requires_issue_and_pinpoint(self) -> None:
        paper = self.add_paper("引注论文", "知识产权—著作权法")
        text = paper.read_text(encoding="utf-8")
        text = text.replace('journal: "测试法学"', 'journal: "测试法学"\nissue: "2"')
        paper.write_text(text, encoding="utf-8")
        relative = paper.relative_to(self.vault).as_posix()
        missing = server.render_legal_citation(relative, "paraphrase")
        self.assertFalse(missing["ok"])
        self.assertIn("具体页码", missing["missing"])
        rendered = server.render_legal_citation(relative, "paraphrase", "15-16")
        self.assertEqual(
            rendered["citation"],
            "参见测试作者：《引注论文》，载《测试法学》2026年第2期，第15-16页。",
        )


if __name__ == "__main__":
    unittest.main()
