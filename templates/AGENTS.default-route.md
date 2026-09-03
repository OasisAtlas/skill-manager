<!-- skill-manager:default-install-route:start -->
## Skill Installation Default Workflow

Whenever the user asks to install, add, download, or import a Codex Skill, automatically use `${CODEX_HOME}/skills/skill-manager/SKILL.md` as the primary workflow without requiring an explicit `$skill-manager` invocation. The workflow must inspect and briefly introduce the target Skill, obtain an explicit category decision, and only then use `skill-installer` as the subordinate download mechanism. Do not route an actual installation directly to `skill-installer`, even when the user mentions that installer. A listing-only request may use `skill-installer`; selecting an item for installation activates `skill-manager` before download.
<!-- skill-manager:default-install-route:end -->
