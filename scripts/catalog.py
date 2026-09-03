#!/usr/bin/env python3
"""Maintain optional categories and explicit aliases for local Codex skills."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64


def codex_home(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def paths(home: Path) -> tuple[Path, Path]:
    return home / "skills", home / "skill-manager" / "catalog.json"


def empty_catalog() -> dict:
    return {"schema_version": 1, "categories": {}, "skills": {}}


def load_catalog(path: Path) -> dict:
    if not path.exists():
        return empty_catalog()
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("schema_version") != 1:
        raise ValueError(f"Unsupported catalog schema in {path}")
    if not isinstance(data.get("categories"), dict) or not isinstance(data.get("skills"), dict):
        raise ValueError(f"Invalid catalog structure in {path}")
    return data


def save_catalog(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    temporary.replace(path)


def validate_slug(value: str, label: str) -> None:
    if not SLUG_RE.fullmatch(value) or len(value) > MAX_NAME_LENGTH:
        raise ValueError(f"{label} must be hyphen-case and at most {MAX_NAME_LENGTH} characters: {value}")


def installed_skills(root: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    if not root.exists():
        return result
    for skill_md in sorted(root.glob("*/SKILL.md")):
        folder = skill_md.parent.name
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        name_match = re.search(r"(?m)^name:\s*[\"']?([^\"'\n]+)", text)
        name = name_match.group(1).strip() if name_match else folder
        is_alias = "Managed-By: skill-manager" in text
        result[folder] = {"name": name, "path": str(skill_md.parent), "alias": is_alias}
    return result


def require_canonical(root: Path, skill: str) -> Path:
    validate_slug(skill, "skill")
    folder = root / skill
    if not (folder / "SKILL.md").is_file():
        raise ValueError(f"Canonical skill is not installed at {folder}")
    return folder


def alias_name(category: str, skill: str) -> str:
    value = f"{category}-{skill}"
    validate_slug(value, "alias")
    return value


def create_alias(root: Path, category: str, skill: str) -> str:
    alias = alias_name(category, skill)
    destination = root / alias
    if destination.exists():
        skill_md = destination / "SKILL.md"
        existing = skill_md.read_text(encoding="utf-8", errors="replace") if skill_md.exists() else ""
        marker = f"Canonical-Skill: {skill}"
        if "Managed-By: skill-manager" in existing and marker in existing:
            return alias
        raise ValueError(f"Alias destination already exists and is not the expected managed alias: {destination}")
    destination.mkdir(parents=False)
    (destination / "agents").mkdir()
    canonical_path = root / skill / "SKILL.md"
    (destination / "SKILL.md").write_text(
        f'''---
name: {alias}
description: Explicit category-prefixed alias for the installed `{skill}` skill. Use only when the user invokes `${alias}`; otherwise select the canonical skill normally.
metadata:
  short-description: Alias for {skill}
---

# {alias}

<!-- Managed-By: skill-manager -->
<!-- Canonical-Skill: {skill} -->

Read and follow the canonical skill at `{canonical_path}` for this entire task. This alias changes only invocation; it does not change the canonical package, source, permissions, or workflow.
''',
        encoding="utf-8",
    )
    (destination / "agents" / "openai.yaml").write_text(
        f'''interface:
  display_name: "{alias}"
  short_description: "Explicit alias for the {skill} skill"
  default_prompt: "Use ${alias} for this task."
policy:
  allow_implicit_invocation: false
''',
        encoding="utf-8",
    )
    return alias


def command_inventory(args: argparse.Namespace, home: Path, root: Path, catalog_path: Path) -> None:
    catalog = load_catalog(catalog_path)
    installed = installed_skills(root)
    rows = []
    aliases = {name for name, item in installed.items() if item["alias"]}
    for folder, item in installed.items():
        if item["alias"]:
            continue
        record = catalog["skills"].get(folder, {})
        rows.append({
            "skill": folder,
            "declared_name": item["name"],
            "category": record.get("category"),
            "status": record.get("status", "not-recorded"),
            "alias": record.get("alias") if record.get("alias") in aliases else None,
            "source": record.get("source"),
        })
    print(json.dumps({"codex_home": str(home), "skills": rows}, ensure_ascii=False, indent=2))


def command_list_categories(args: argparse.Namespace, home: Path, root: Path, catalog_path: Path) -> None:
    catalog = load_catalog(catalog_path)
    print(json.dumps(catalog["categories"], ensure_ascii=False, indent=2, sort_keys=True))


def command_add_category(args: argparse.Namespace, home: Path, root: Path, catalog_path: Path) -> None:
    validate_slug(args.id, "category id")
    catalog = load_catalog(catalog_path)
    existing = catalog["categories"].get(args.id)
    proposed = {"label": args.label, "description": args.description}
    if existing and existing != proposed:
        raise ValueError(f"Category already exists with different data: {args.id}")
    catalog["categories"][args.id] = proposed
    save_catalog(catalog_path, catalog)
    print(json.dumps({"category": args.id, **proposed}, ensure_ascii=False))


def command_classify(args: argparse.Namespace, home: Path, root: Path, catalog_path: Path) -> None:
    require_canonical(root, args.skill)
    catalog = load_catalog(catalog_path)
    if args.category not in catalog["categories"]:
        raise ValueError(f"Unknown category: {args.category}. Create it explicitly or leave the skill unclassified.")
    record = catalog["skills"].get(args.skill, {})
    current = record.get("category")
    if current and current != args.category:
        raise ValueError(
            f"Skill is already classified as {current}. Run unclassify first so any old alias is handled explicitly."
        )
    record.update({"status": "classified", "category": args.category})
    if args.source:
        record["source"] = args.source
    if args.create_alias:
        record["alias"] = create_alias(root, args.category, args.skill)
    catalog["skills"][args.skill] = record
    save_catalog(catalog_path, catalog)
    print(json.dumps({"skill": args.skill, **record}, ensure_ascii=False))


def command_unclassified(args: argparse.Namespace, home: Path, root: Path, catalog_path: Path) -> None:
    require_canonical(root, args.skill)
    catalog = load_catalog(catalog_path)
    record = catalog["skills"].get(args.skill, {})
    record.update({"status": "unclassified", "category": None})
    if args.source:
        record["source"] = args.source
    catalog["skills"][args.skill] = record
    save_catalog(catalog_path, catalog)
    print(json.dumps({"skill": args.skill, **record}, ensure_ascii=False))


def command_unclassify(args: argparse.Namespace, home: Path, root: Path, catalog_path: Path) -> None:
    require_canonical(root, args.skill)
    catalog = load_catalog(catalog_path)
    record = catalog["skills"].get(args.skill, {})
    existing_alias = record.get("alias")
    if existing_alias:
        alias_path = root / existing_alias
        alias_skill_md = alias_path / "SKILL.md"
        alias_text = alias_skill_md.read_text(encoding="utf-8", errors="replace") if alias_skill_md.exists() else ""
        expected_marker = f"Canonical-Skill: {args.skill}"
        if not args.remove_alias:
            raise ValueError(
                f"Managed alias {existing_alias} exists. Re-run with --remove-alias to remove it explicitly."
            )
        if "Managed-By: skill-manager" not in alias_text or expected_marker not in alias_text:
            raise ValueError(f"Refusing to remove an alias that is not verified as managed: {alias_path}")
        shutil.rmtree(alias_path)
    record.update({"status": "unclassified", "category": None})
    record.pop("alias", None)
    catalog["skills"][args.skill] = record
    save_catalog(catalog_path, catalog)
    print(json.dumps({"skill": args.skill, **record}, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--codex-home", help="Override CODEX_HOME for testing or another installation")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("inventory")
    commands.add_parser("list-categories")
    add = commands.add_parser("add-category")
    add.add_argument("--id", required=True)
    add.add_argument("--label", required=True)
    add.add_argument("--description", required=True)
    classify = commands.add_parser("classify")
    classify.add_argument("--skill", required=True)
    classify.add_argument("--category", required=True)
    classify.add_argument("--source")
    classify.add_argument("--create-alias", action="store_true")
    unclassified = commands.add_parser("record-unclassified")
    unclassified.add_argument("--skill", required=True)
    unclassified.add_argument("--source")
    remove = commands.add_parser("unclassify")
    remove.add_argument("--skill", required=True)
    remove.add_argument("--remove-alias", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    home = codex_home(args.codex_home)
    root, catalog_path = paths(home)
    handlers = {
        "inventory": command_inventory,
        "list-categories": command_list_categories,
        "add-category": command_add_category,
        "classify": command_classify,
        "record-unclassified": command_unclassified,
        "unclassify": command_unclassify,
    }
    try:
        handlers[args.command](args, home, root, catalog_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
