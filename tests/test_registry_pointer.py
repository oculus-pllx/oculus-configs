import unittest
from pathlib import Path

SOURCES = ("claude/CLAUDE.md", "codex/AGENTS.md", "gemini/GEMINI.md")
EQEMU_AI_SOURCES = ("claude/CLAUDE.md", "codex/AGENTS.md")


class TestRegistryPointer(unittest.TestCase):
    def test_every_tool_points_at_the_registry(self):
        root = Path(__file__).parents[1]
        for rel in SOURCES:
            text = " ".join((root / rel).read_text().replace("**", "").split())
            with self.subTest(source=rel):
                self.assertIn("## Credentials and Infrastructure Registry", text)
                self.assertIn("/etc/ccc/registry/access-map.md", text)
                self.assertIn("Never print, log, or commit a secret value", text)

    def test_codex_and_claude_point_to_canonical_eqemu_loader(self):
        root = Path(__file__).parents[1]
        for rel in EQEMU_AI_SOURCES:
            text = (root / rel).read_text(encoding="utf-8")
            with self.subTest(source=rel):
                self.assertIn("/srv/ccc/projects/parallax-emu-coordinator", text)
                self.assertIn("/srv/ccc/projects/parallax-eqemu", text)
                self.assertIn("python3 deploy/sysmap.py rag-load-operations", text)


if __name__ == "__main__":
    unittest.main()
