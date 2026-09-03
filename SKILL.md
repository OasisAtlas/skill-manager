---
name: skill-manager
description: Install, inventory, and optionally classify local Codex skills while preserving each upstream skill's canonical name and source. Before every installation, briefly explain the target skill's main capability and workflow, then obtain an explicit category decision. Use when installing many skills, organizing the local skill library, defining categories, creating category-prefixed call aliases, or reviewing unclassified skills. Do not activate for ordinary use of an already installed skill.
metadata:
  short-description: Organize and classify installed skills
---

# Skill Manager

Manage classification around the existing `skill-installer`; do not replace its download and authentication behavior.

## Storage model

- Keep every upstream skill installed under its canonical folder and preserve the `name` in its `SKILL.md`.
- Store classification state outside skill packages at `${CODEX_HOME:-$HOME/.codex}/skill-manager/catalog.json`, so upgrades do not erase it.
- A skill may have one primary category, or remain unclassified.
- Category IDs use lowercase letters, digits, and hyphens. They also serve as optional invocation prefixes.
- A prefixed invocation such as `$ppt-slide-maker` is a thin explicit-only alias. It points to the canonical skill; it is not a renamed or duplicated upstream package.
- When a skill is assigned a category, create its category-prefixed alias by default. Skip the alias only when the user explicitly declines it or a collision makes creation unsafe.

## Installation workflow

1. Inspect the source skill's `SKILL.md` and source path before installation. Identify its canonical name, purpose, obvious overlaps, and whether it is already installed.
2. Read the existing categories with:

   ```bash
   python3 scripts/catalog.py list-categories
   ```

3. Compare the skill's actual purpose with category descriptions. Do not classify from a keyword in the name alone.
4. Before asking for classification, give a compact briefing based on the inspected source rather than the skill name alone:
   - **Main capability:** what problem the skill solves and its principal output.
   - **Main workflow:** summarize the execution path in one short sentence or compact arrow sequence.
   - **Key boundary:** mention only an important exclusion, dependency, permission, or side effect when it materially affects classification or installation.
   Keep the briefing concise; do not reproduce the full `SKILL.md`.
5. **In the same message, before running any installation command, ask the user to make the category decision. This confirmation is mandatory for every installation and cannot be inferred or skipped:**
   - If one existing category clearly fits, recommend it and ask whether to use it, choose another category, create a new category, or remain unclassified.
   - If multiple categories plausibly fit, show the compact candidate list and ask which one to use, while also offering a new category or unclassified.
   - If no category fits, ask whether to create a new category or remain unclassified.
   - Even when the user has already mentioned a likely category in the installation request, restate the exact proposed category and obtain confirmation before installation.
6. Pause until the user answers. Choosing unclassified is a complete and valid decision; category assignment and category creation remain optional.
7. Install the canonical package through `skill-installer` only after that decision. Never edit the downloaded `SKILL.md` merely to add a prefix.
8. Record the installation. Use `classify` for a category or `record-unclassified` when skipped. Include the source URL or repository path when known.
9. When classified, create the prefixed alias by default. If the user explicitly declines it, classify without an alias; if the alias collides, stop and report the conflict rather than overwriting anything.
10. Report the canonical invocation, category state, optional alias, and source. Tell the user a newly installed skill is available on the next turn.

For batch installs, classify each skill independently but present one compact proposed mapping for confirmation. Each row must include the skill name, a short capability summary, a compact workflow, and the proposed category or candidates. Do not install any item until the user confirms the whole mapping or explicitly confirms individual rows. Include unclassified and new-category choices where relevant.

## Catalog commands

The helper is deterministic and uses only the Python standard library:

```bash
python3 scripts/catalog.py inventory
python3 scripts/catalog.py list-categories
python3 scripts/catalog.py add-category --id presentation --label "演示文稿" --description "PPT、幻灯片与演示设计"
python3 scripts/catalog.py classify --skill slide-maker --category presentation --source https://github.com/example/repo --create-alias
python3 scripts/catalog.py record-unclassified --skill some-skill --source https://github.com/example/repo
python3 scripts/catalog.py unclassify --skill some-skill --remove-alias
```

Run the helper from this skill directory, or pass `--codex-home` explicitly. Commands that change state create the catalog directory when needed. They must fail rather than overwrite an existing unrelated alias or classify a missing canonical skill.

## Decision rules

- Prefer a small, stable category set based on capability, not source repository, author, temporary test batch, or quality rank.
- Use a temporary batch prefix such as `ppt-skill-1` only when the user explicitly wants batch identity to be the category.
- Do not force every skill into a category. `unclassified` is a valid durable state.
- Never treat a confident match as permission to classify or install. The user must confirm the category decision first.
- Category confirmation includes default creation of the category-prefixed alias unless the user explicitly opts out.
- Do not silently create a new category because no current category fits.
- Do not assign multiple primary categories. Record secondary discovery terms in the category description or rely on the skill's own description.
- Reject category aliases that collide with a canonical skill or another alias.
- Reclassification must first remove the old classification. If a managed alias exists, `unclassify` requires the explicit `--remove-alias` flag and removes only the verified managed alias.
- Before removing or renaming a category, show the affected skills and aliases; this helper intentionally does not automate category deletion or renaming.

## Existing-library review

`inventory` compares installed canonical skills and alias wrappers with the catalog. Treat prefix clusters as suggestions only. Ask before migrating existing names or creating aliases; existing user-managed skill folders are not automatically rewritten.
