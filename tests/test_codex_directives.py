import unittest
from pathlib import Path


class TestCodexDirectives(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directives = (
            Path(__file__).parents[1] / "codex" / "AGENTS.md"
        ).read_text()

    def test_requires_direct_communication(self):
        self.assertIn("## Communication Discipline", self.directives)
        self.assertIn("Lead with the result", self.directives)
        self.assertIn(
            "Default to under 150 words when that is enough", self.directives
        )

    def test_requires_minimum_sufficient_context(self):
        self.assertIn("## Context Discipline", self.directives)
        self.assertIn("minimum context needed", self.directives)
        self.assertIn("Correctness and completion override brevity", self.directives)


if __name__ == "__main__":
    unittest.main()
