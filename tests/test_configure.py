import sys
import os
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

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


class TestFsMkdir(unittest.TestCase):
    def test_mkdir_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            result = configure.fs_mkdir(tmp, "new-folder")
            self.assertTrue(result["ok"])
            self.assertTrue(Path(result["path"]).exists())
            self.assertEqual(Path(result["path"]).name, "new-folder")

    def test_mkdir_already_exists(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "existing").mkdir()
            result = configure.fs_mkdir(tmp, "existing")
        self.assertFalse(result["ok"])
        self.assertIn("already exists", result["error"])

    def test_mkdir_empty_name(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            result = configure.fs_mkdir(tmp, "")
        self.assertFalse(result["ok"])
        self.assertIn("empty", result["error"].lower())


class TestFsRename(unittest.TestCase):
    def test_rename_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "old-name"
            src.mkdir()
            result = configure.fs_rename(str(src), "new-name")
            self.assertTrue(result["ok"])
            self.assertTrue(Path(tmp, "new-name").exists())
            self.assertFalse(src.exists())

    def test_rename_conflict(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "old").mkdir()
            (Path(tmp) / "taken").mkdir()
            result = configure.fs_rename(str(Path(tmp) / "old"), "taken")
        self.assertFalse(result["ok"])
        self.assertIn("already exists", result["error"])

    def test_rename_empty_name(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "folder"
            src.mkdir()
            result = configure.fs_rename(str(src), "")
        self.assertFalse(result["ok"])
        self.assertIn("empty", result["error"].lower())


class TestFsDelete(unittest.TestCase):
    def test_delete_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "to-delete"
            target.mkdir()
            (target / "child.txt").write_text("hi")
            result = configure.fs_delete(str(target))
        self.assertTrue(result["ok"])
        self.assertFalse(target.exists())

    def test_delete_not_found(self):
        import configure
        result = configure.fs_delete("/nonexistent/path/that/does/not/exist")
        self.assertFalse(result["ok"])
        self.assertIn("not found", result["error"].lower())

    def test_delete_protected(self):
        import configure
        result = configure.fs_delete(str(Path.home()))
        self.assertFalse(result["ok"])
        self.assertIn("protected", result["error"].lower())


class TestFsMove(unittest.TestCase):
    def test_move_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src-folder"
            dest = Path(tmp) / "dest-parent"
            src.mkdir(); dest.mkdir()
            result = configure.fs_move(str(src), str(dest))
            self.assertTrue(result["ok"])
            self.assertTrue(Path(tmp, "dest-parent", "src-folder").exists())
            self.assertFalse(src.exists())

    def test_move_name_conflict(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "my-folder"
            dest = Path(tmp) / "dest"
            conflict = dest / "my-folder"
            src.mkdir(); dest.mkdir(); conflict.mkdir()
            result = configure.fs_move(str(src), str(dest))
        self.assertFalse(result["ok"])
        self.assertIn("already exists", result["error"])


class TestGetRepoPath(unittest.TestCase):
    def test_returns_path_when_present(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            settings = Path(tmp) / "settings.json"
            settings.write_text(json.dumps({"oculus": {"repo_path": "/some/repo"}}))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings}):
                result = configure.get_repo_path()
        self.assertEqual(result, "/some/repo")

    def test_returns_none_when_key_missing(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            settings = Path(tmp) / "settings.json"
            settings.write_text(json.dumps({}))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings}):
                result = configure.get_repo_path()
        self.assertIsNone(result)

    def test_returns_none_when_file_absent(self):
        import configure
        with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": Path("/nonexistent/settings.json")}):
            result = configure.get_repo_path()
        self.assertIsNone(result)


class TestCheckUpdate(unittest.TestCase):
    def test_no_repo_path_returns_error(self):
        import configure
        with patch.object(configure, "get_repo_path", return_value=None):
            result = configure.check_update()
        self.assertFalse(result["available"])
        self.assertIn("error", result)

    def test_git_not_found_returns_error(self):
        import configure
        with patch.object(configure, "get_repo_path", return_value="/repo"):
            with patch("configure.shutil.which", return_value=None):
                result = configure.check_update()
        self.assertFalse(result["available"])
        self.assertIn("error", result)

    def test_up_to_date(self):
        import configure
        with patch.object(configure, "get_repo_path", return_value="/repo"):
            with patch("configure.shutil.which", return_value="/usr/bin/git"):
                with patch("configure.subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(returncode=0, stdout="", stderr=""),
                        MagicMock(returncode=0, stdout="0\n", stderr=""),
                        MagicMock(returncode=0, stdout="abc1234\n", stderr=""),
                    ]
                    result = configure.check_update()
        self.assertFalse(result["available"])
        self.assertEqual(result["commits"], 0)

    def test_commits_available(self):
        import configure
        with patch.object(configure, "get_repo_path", return_value="/repo"):
            with patch("configure.shutil.which", return_value="/usr/bin/git"):
                with patch("configure.subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(returncode=0, stdout="", stderr=""),
                        MagicMock(returncode=0, stdout="3\n", stderr=""),
                        MagicMock(returncode=0, stdout="abc1234\n", stderr=""),
                    ]
                    result = configure.check_update()
        self.assertTrue(result["available"])
        self.assertEqual(result["commits"], 3)
        self.assertEqual(result["latest"], "abc1234")


class TestRestartService(unittest.TestCase):
    def test_linux_uses_systemctl(self):
        import configure
        with patch("configure.platform.system", return_value="Linux"):
            with patch("configure.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr="")
                result = configure._restart_service()
        self.assertTrue(result["restarting"])
        cmd = mock_run.call_args[0][0]
        self.assertIn("systemctl", cmd)
        self.assertIn("oculus-configure", cmd)

    def test_macos_uses_launchctl(self):
        import configure
        with patch("configure.platform.system", return_value="Darwin"):
            with patch("configure.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr="")
                result = configure._restart_service()
        self.assertTrue(result["restarting"])
        cmd = mock_run.call_args[0][0]
        self.assertIn("launchctl", cmd)

    def test_unknown_platform_no_restart(self):
        import configure
        with patch("configure.platform.system", return_value="Windows"):
            result = configure._restart_service()
        self.assertFalse(result["restarting"])
        self.assertIsNone(result["error"])


class TestApplyUpdate(unittest.TestCase):
    def test_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / "configure.py").write_text("# fake")
            with patch.object(configure, "get_repo_path", return_value=str(repo)):
                with patch("configure.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                    with patch.object(configure, "_restart_service", return_value={"restarting": True, "error": None}):
                        with patch("configure.shutil.copy2"):
                            result = configure.apply_update()
        self.assertTrue(result["ok"])
        self.assertTrue(result["restarting"])

    def test_pull_failure_aborts_before_copy(self):
        import configure
        with patch.object(configure, "get_repo_path", return_value="/repo"):
            with patch("configure.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="merge conflict")
                with patch("configure.shutil.copy2") as mock_copy:
                    result = configure.apply_update()
        self.assertFalse(result["ok"])
        self.assertIn("pull failed", result["error"])
        mock_copy.assert_not_called()

    def test_copy_failure_skips_restart(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / "configure.py").write_text("# fake")
            with patch.object(configure, "get_repo_path", return_value=str(repo)):
                with patch("configure.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                    with patch("configure.shutil.copy2", side_effect=PermissionError("denied")):
                        with patch.object(configure, "_restart_service") as mock_restart:
                            result = configure.apply_update()
        self.assertFalse(result["ok"])
        self.assertIn("copy failed", result["error"])
        mock_restart.assert_not_called()


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


class TestCreateProject(unittest.TestCase):
    def test_create_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            result = configure.create_project("My New Project", tmp, ["CLAUDE.md"])
            self.assertTrue(result["ok"])
            self.assertIn("path", result)
            self.assertIn("git_log", result)
            project_path = Path(result["path"])
            self.assertTrue(project_path.exists())
            self.assertIn("Initial commit", result["git_log"])
            self.assertEqual(project_path.name, "my-new-project")

    def test_create_no_templates(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            result = configure.create_project("bare", tmp, [])
            self.assertTrue(result["ok"])
            project_path = Path(result["path"])
            contents = [p.name for p in project_path.iterdir()]
            self.assertIn(".git", contents)

    def test_create_folder_already_exists(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "my-project").mkdir()
            result = configure.create_project("my-project", tmp, [])
            self.assertFalse(result["ok"])
            self.assertIn("already exists", result["error"])

    def test_slugify(self):
        import configure
        self.assertEqual(configure.slugify("Hello World!"), "hello-world-")
        self.assertEqual(configure.slugify("my-project"), "my-project")
        self.assertEqual(configure.slugify("ABC 123"), "abc-123")


class TestProjectGithub(unittest.TestCase):
    def test_github_no_gh_in_path(self):
        import configure
        with patch("configure.shutil") as mock_shutil:
            mock_shutil.which.return_value = None
            with tempfile.TemporaryDirectory() as tmp:
                result = configure.github_project(tmp, "test-repo", True)
        self.assertFalse(result["ok"])
        self.assertIn("error", result)


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
