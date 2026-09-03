#!/usr/bin/env python3
"""Verify the local skill-manager installation and optional global route."""

from __future__ import annotations

import argparse

from install import END_MARKER, START_MARKER, resolve_codex_home


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home")
    args = parser.parse_args()
    home = resolve_codex_home(args.codex_home)
    checks = {
        "skill": (home / "skills" / "skill-manager" / "SKILL.md").is_file(),
        "agent_metadata": (home / "skills" / "skill-manager" / "agents" / "openai.yaml").is_file(),
    }
    agents_path = home / "AGENTS.md"
    agents_text = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    checks["default_route"] = START_MARKER in agents_text and END_MARKER in agents_text
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
