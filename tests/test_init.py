import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parent.parent


class InitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "skills-repo"
        for directory in ("scripts", "config", "skills"):
            shutil.copytree(REPO / directory, self.repo / directory)
        self.project = self.root / "example-project"

    def run_init(self, *args):
        return subprocess.run(
            [str(self.repo / "scripts/init"), "--project-dir", str(self.project), *args],
            capture_output=True, text=True,
        )

    def test_defaults_and_existing_log_are_preserved(self):
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stderr)
        log = self.project / "docs/example-project-TASKLOG.md"
        self.assertIn("# example-project task log", log.read_text())
        self.assertTrue((self.project / "docs/plans").is_dir())
        rendered = self.repo / ".generated/skills/one-by-one/SKILL.md"
        self.assertIn("docs/PROJECT_NAME-TASKLOG.md", rendered.read_text())
        self.assertNotIn("{{", rendered.read_text())
        log.write_text("User's existing progress\n")
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text(), "User's existing progress\n")

    def test_custom_paths(self):
        config = self.root / "custom.json"
        config.write_text(json.dumps({
            "tasklog_dir": "notes/tasks", "planning_doc_dir": "notes/plans",
        }))
        result = self.run_init("--config", str(config))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / "notes/tasks/example-project-TASKLOG.md").is_file())
        self.assertTrue((self.project / "notes/plans").is_dir())
        rendered = (self.repo / ".generated/skills/one-by-one/SKILL.md").read_text()
        self.assertIn("notes/tasks/PROJECT_NAME-TASKLOG.md", rendered)
        self.assertIn("`notes/plans`", rendered)

    def test_example_defaults_without_local_config(self):
        (self.repo / "config/defaults.json").unlink(missing_ok=True)
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / "docs/example-project-TASKLOG.md").is_file())
        self.assertTrue((self.project / "docs/plans").is_dir())

    def test_local_config_and_explicit_override(self):
        (self.repo / "config/defaults.json").write_text(json.dumps({
            "tasklog_dir": "local/tasks", "planning_doc_dir": "local/plans",
        }))
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / "local/tasks/example-project-TASKLOG.md").is_file())
        config = self.root / "override.json"
        config.write_text(json.dumps({"tasklog_dir": "override/tasks"}))
        result = self.run_init("--config", str(config))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / "override/tasks/example-project-TASKLOG.md").is_file())
        rendered = (self.repo / ".generated/skills/one-by-one/SKILL.md").read_text()
        self.assertIn("`local/plans`", rendered)

    def test_absolute_paths_share_resources_across_projects(self):
        tasks = self.root / "shared/tasks"
        plans = self.root / "shared/plans"
        config = self.root / "shared.json"
        config.write_text(json.dumps({
            "tasklog_dir": str(tasks), "planning_doc_dir": str(plans),
        }))
        for project_name in ("first-project", "second-project"):
            self.project = self.root / project_name
            result = self.run_init("--config", str(config))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((tasks / f"{project_name}-TASKLOG.md").is_file())
            self.assertFalse((self.project / "docs").exists())
        self.assertTrue(plans.is_dir())
        rendered = (self.repo / ".generated/skills/one-by-one/SKILL.md").read_text()
        self.assertIn(f"{tasks}/PROJECT_NAME-TASKLOG.md", rendered)
        self.assertIn(f"`{plans}`", rendered)
        log = tasks / "second-project-TASKLOG.md"
        log.write_text("Existing shared progress\n")
        result = self.run_init("--config", str(config))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text(), "Existing shared progress\n")

    def test_mixed_absolute_and_relative_paths(self):
        config = self.root / "mixed.json"
        config.write_text(json.dumps({"planning_doc_dir": str(self.root / "plans")}))
        result = self.run_init("--config", str(config))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / "docs/example-project-TASKLOG.md").is_file())
        self.assertTrue((self.root / "plans").is_dir())

    def test_parent_relative_paths(self):
        config = self.root / "parent.json"
        config.write_text(json.dumps({
            "tasklog_dir": "../shared/tasks", "planning_doc_dir": "../shared/plans",
        }))
        result = self.run_init("--config", str(config))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "shared/tasks/example-project-TASKLOG.md").is_file())
        self.assertTrue((self.root / "shared/plans").is_dir())

    def test_invalid_config_does_not_write_output(self):
        for overrides in (
            {"project_name": "../outside"}, {"tasklog_dir": 3}, {"typo": "docs"},
        ):
            with self.subTest(overrides=overrides):
                config = self.root / "invalid.json"
                config.write_text(json.dumps(overrides))
                result = self.run_init("--config", str(config))
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.repo / ".generated").exists())
                self.assertFalse(self.project.exists())

    def test_resource_paths_follow_symlinks(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.project.mkdir()
        (self.project / "docs").symlink_to(outside, target_is_directory=True)
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((outside / "example-project-TASKLOG.md").is_file())
        self.assertTrue((outside / "plans").is_dir())

    def test_installers_render_without_project_resources(self):
        home = self.root / "home"
        home.mkdir()
        for app in ("codex", "claude"):
            with self.subTest(app=app):
                result = subprocess.run(
                    [str(self.repo / f"scripts/install-{app}")], cwd=home,
                    env={**os.environ, "HOME": str(home)}, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                installed = home / f".{app}/skills/one-by-one"
                self.assertTrue(installed.is_symlink())
                self.assertNotIn("{{", (installed / "SKILL.md").read_text())
                self.assertFalse((home / "docs").exists())


if __name__ == "__main__":
    unittest.main()
