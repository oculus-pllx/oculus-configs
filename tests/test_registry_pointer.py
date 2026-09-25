import unittest
from pathlib import Path

SOURCES = ("claude/CLAUDE.md", "codex/AGENTS.md", "gemini/GEMINI.md")


class TestRegistryPointer(unittest.TestCase):
    def test_every_tool_points_at_the_registry(self):
        root = Path(__file__).parents[1]
        for rel in SOURCES:
            text = " ".join((root / rel).read_text().replace("**", "").split())
            with self.subTest(source=rel):
                self.assertIn("## Credentials and Infrastructure Registry", text)
                self.assertIn("Meridian-VPS/docs/access-map.md", text)
                self.assertIn("Never print, log, or commit a secret value", text)


if __name__ == "__main__":
    unittest.main()
