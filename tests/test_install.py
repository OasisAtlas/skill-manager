from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("skill_manager_install", SCRIPT)
INSTALL = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(INSTALL)


class InstallTests(unittest.TestCase):
    def test_interactive_default_recommends_full_install(self) -> None:
        with patch("builtins.input", return_value=""):
            self.assertEqual(INSTALL.choose_mode(), "full")

    def test_interactive_skill_only_choice(self) -> None:
        with patch("builtins.input", return_value="2"):
            self.assertEqual(INSTALL.choose_mode(), "skill-only")

    def test_full_install_is_idempotent_and_preserves_other_rules(self) -> None:
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / ".codex"
            home.mkdir()
            agents = home / "AGENTS.md"
            agents.write_text("# Existing\n\nKeep this rule.\n", encoding="utf-8")
            destination = home / "skills" / "skill-manager"
            INSTALL.install_package(source, destination)
            rule = INSTALL.render_rule(source, home)
            self.assertEqual(INSTALL.initialize_global_route(agents, rule), "updated")
            first = agents.read_text(encoding="utf-8")
            self.assertEqual(INSTALL.initialize_global_route(agents, rule), "unchanged")
            self.assertEqual(agents.read_text(encoding="utf-8"), first)
            self.assertIn("Keep this rule.", first)
            self.assertIn(str(home / "skills" / "skill-manager" / "SKILL.md"), first)
            self.assertTrue((destination / "SKILL.md").is_file())
            self.assertTrue((home / "AGENTS.md.skill-manager.bak").is_file())

    def test_partial_markers_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            agents = Path(directory) / "AGENTS.md"
            agents.write_text(INSTALL.START_MARKER, encoding="utf-8")
            with self.assertRaises(ValueError):
                INSTALL.initialize_global_route(agents, "rule")


if __name__ == "__main__":
    unittest.main()
