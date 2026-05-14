import sys
import os
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestConstants(unittest.TestCase):
    def test_import(self):
        import configure
        self.assertEqual(configure.PORT, 4827)
        self.assertTrue(configure.CLAUDE_DIR.name == ".claude")
        self.assertTrue(configure.TEMPLATES_DIR.name == "Templates")
        self.assertTrue(configure.STARTER_DIR.name == "claude-code-starter")


class TestGetStatus(unittest.TestCase):
    def test_returns_items_list(self):
        import configure
        result = configure.get_status()
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)

    def test_item_has_required_keys(self):
        import configure
        result = configure.get_status()
        for item in result["items"]:
            self.assertIn("label", item)
            self.assertIn("status", item)
            self.assertIn("message", item)
            self.assertIn(item["status"], ("ok", "warn", "err"))

    def test_missing_claude_dir_returns_err(self):
        import configure
        with patch.object(configure, "CLAUDE_DIR", Path("/nonexistent/path/.claude")):
            result = configure.get_status()
        claude_item = next(i for i in result["items"] if "CLAUDE.md" in i["label"])
        self.assertEqual(claude_item["status"], "err")

    def test_placeholder_token_returns_warn(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            mcp_path = Path(tmp) / "claude_desktop_config.json"
            mcp_path.write_text(json.dumps({"mcpServers": {"github": {"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "REPLACE_WITH_YOUR_TOKEN"}}}}))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "mcp": mcp_path}):
                result = configure.get_status()
        mcp_item = next(i for i in result["items"] if "MCP" in i["label"])
        self.assertEqual(mcp_item["status"], "warn")


class TestReadWriteConfig(unittest.TestCase):
    def test_read_existing_file(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "CLAUDE.md"
            p.write_text("# hello")
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "CLAUDE.md": p}):
                result = configure.read_config("CLAUDE.md")
        self.assertEqual(result["content"], "# hello")
        self.assertTrue(result["exists"])

    def test_read_missing_file(self):
        import configure
        with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "CLAUDE.md": Path("/no/such/file.md")}):
            result = configure.read_config("CLAUDE.md")
        self.assertFalse(result["exists"])
        self.assertEqual(result["content"], "")

    def test_read_unknown_name_returns_error(self):
        import configure
        result = configure.read_config("totally-unknown")
        self.assertFalse(result.get("exists", True))
        self.assertIn("error", result)

    def test_write_creates_file(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "CLAUDE.md"
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "CLAUDE.md": p}):
                result = configure.write_config("CLAUDE.md", "# new content")
            self.assertTrue(result["ok"])
            self.assertEqual(p.read_text(), "# new content")

    def test_write_creates_parent_dirs(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "sub" / "dir" / "file.md"
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "CLAUDE.md": p}):
                result = configure.write_config("CLAUDE.md", "content")
            self.assertTrue(result["ok"])
            self.assertTrue(p.exists())


class TestGetPlugins(unittest.TestCase):
    def _make_plugins_file(self, tmp, plugins_dict):
        p = Path(tmp) / "plugins" / "installed_plugins.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"version": 2, "plugins": plugins_dict}))
        return p

    def test_returns_known_list(self):
        import configure
        result = configure.get_plugins()
        self.assertIn("known", result)
        ids = [p["id"] for p in result["known"]]
        self.assertIn("superpowers@claude-plugins-official", ids)

    def test_installed_plugin_marked_correctly(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            self._make_plugins_file(tmp, {"superpowers@claude-plugins-official": [{"version": "5.1.0"}]})
            settings_path = Path(tmp) / "settings.json"
            settings_path.write_text(json.dumps({"enabledPlugins": {"superpowers@claude-plugins-official": True}}))
            with patch.object(configure, "CLAUDE_DIR", Path(tmp)):
                with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings_path}):
                    result = configure.get_plugins()
        sp = next(p for p in result["known"] if p["id"] == "superpowers@claude-plugins-official")
        self.assertTrue(sp["installed"])
        self.assertTrue(sp["enabled"])
        self.assertEqual(sp["version"], "5.1.0")

    def test_missing_plugins_file_returns_not_installed(self):
        import configure
        with patch.object(configure, "CLAUDE_DIR", Path("/nonexistent")):
            result = configure.get_plugins()
        for p in result["known"]:
            self.assertFalse(p["installed"])


class TestUpdatePlugins(unittest.TestCase):
    def test_toggle_does_not_touch_other_keys(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / "settings.json"
            settings_path.write_text(json.dumps({
                "hooks": {"SessionStart": []},
                "theme": "dark",
                "enabledPlugins": {"superpowers@claude-plugins-official": True}
            }))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings_path}):
                configure.update_enabled_plugins({"claude-mem@thedotmack": True})
                result = json.loads(settings_path.read_text())
        self.assertIn("hooks", result)
        self.assertEqual(result["theme"], "dark")
        self.assertTrue(result["enabledPlugins"]["superpowers@claude-plugins-official"])
        self.assertTrue(result["enabledPlugins"]["claude-mem@thedotmack"])

    def test_toggle_creates_settings_if_missing(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / "settings.json"
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings_path}):
                result = configure.update_enabled_plugins({"superpowers@claude-plugins-official": False})
            self.assertTrue(result["ok"])
            self.assertTrue(settings_path.exists())


class TestMcpConfig(unittest.TestCase):
    def test_get_mcp_returns_servers(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "mcp.json"
            p.write_text(json.dumps({"mcpServers": {"github": {"command": "npx"}}}))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "mcp": p}):
                result = configure.get_mcp_config()
        self.assertIn("github", result.get("servers", {}))

    def test_write_mcp_saves_file(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "mcp.json"
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "mcp": p}):
                result = configure.write_mcp_config({"mcpServers": {"context7": {"command": "npx"}}})
            self.assertTrue(result["ok"])
            saved = json.loads(p.read_text())
            self.assertIn("context7", saved["mcpServers"])


class TestHtmlJs(unittest.TestCase):
    def test_js_syntax(self):
        import configure
        import subprocess
        import shutil
        if not shutil.which("node"):
            self.skipTest("node not available")
        html = configure.HTML
        js = html[html.find("<script>") + 8:html.find("</script>")]
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
            f.write(js)
            name = f.name
        try:
            r = subprocess.run(["node", "--check", name], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"JS syntax error:\n{r.stderr}")
        finally:
            Path(name).unlink(missing_ok=True)


class TestWhichGh(unittest.TestCase):
    def test_returns_gh_and_code_keys(self):
        import configure
        result = configure.which_gh()
        self.assertIn("gh", result)
        self.assertIn("code", result)
        self.assertIsInstance(result["gh"], bool)
        self.assertIsInstance(result["code"], bool)

    def test_gh_false_when_not_in_path(self):
        import configure
        with patch("configure.shutil") as mock_shutil:
            mock_shutil.which.return_value = None
            result = configure.which_gh()
        self.assertFalse(result["gh"])
        self.assertFalse(result["code"])


if __name__ == "__main__":
    unittest.main()
