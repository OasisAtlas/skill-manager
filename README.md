# Skill Manager for Codex

English | [中文](#中文简介)

`skill-manager` is a Codex skill for installing, inventorying, and optionally classifying local skills without renaming or modifying their canonical packages.

## What it does

- Keeps each installed skill's original folder and `SKILL.md` name.
- Stores category metadata separately in `~/.codex/skill-manager/catalog.json`.
- Creates optional, explicit-only category aliases such as `$presentation-slide-maker`.
- Requires a category decision before every installation: use an existing category, create one, or remain unclassified.
- Refuses to overwrite unrelated aliases or silently reclassify existing skills.

## Workflow

Inspect the source skill → summarize its capability and workflow → ask for a category decision → install through `skill-installer` → record the classification → optionally create a prefixed alias.

## Installation

Copy or clone this repository to your Codex skills directory:

```bash
git clone https://github.com/OasisAtlas/skill-manager.git ~/.codex/skills/skill-manager
```

Restart Codex or begin a new conversation, then invoke:

```text
$skill-manager
```

## Catalog commands

Run these commands from the repository root:

```bash
python3 scripts/catalog.py inventory
python3 scripts/catalog.py list-categories
python3 scripts/catalog.py add-category --id presentation --label "Presentations" --description "Slides and presentation design"
python3 scripts/catalog.py classify --skill slide-maker --category presentation --source https://github.com/example/repo --create-alias
python3 scripts/catalog.py record-unclassified --skill some-skill --source https://github.com/example/repo
python3 scripts/catalog.py unclassify --skill slide-maker --remove-alias
```

The helper uses only the Python standard library. It supports `--codex-home` for testing or managing another Codex installation.

## Important boundary

This skill manages classification around the existing `skill-installer`; it does not replace its download or authentication behavior. Category aliases are thin wrappers, not copies of upstream skills.

## 中文简介

`skill-manager` 是一个面向 Codex 的本地 Skill 管理技能，用于安装、盘点和可选分类，同时保留每个上游 Skill 的原始目录、名称与内容。

## 主要能力

- 保留已安装 Skill 的原始目录和 `SKILL.md` 名称。
- 将分类信息独立存放在 `~/.codex/skill-manager/catalog.json`，避免升级覆盖。
- 可创建 `$presentation-slide-maker` 这类仅供显式调用的类目前缀别名。
- 每次安装前必须由用户决定：使用已有类目、新建类目，或保持未分类。
- 遇到无关别名冲突或已有分类时会安全拒绝，不静默覆盖。

## 工作流程

检查来源 Skill → 简述主要能力与流程 → 请求用户确认分类 → 通过 `skill-installer` 安装 → 记录分类 → 按需创建前缀别名。

## 安装方式

将仓库克隆到 Codex Skills 目录：

```bash
git clone https://github.com/OasisAtlas/skill-manager.git ~/.codex/skills/skill-manager
```

重启 Codex 或开始新对话后，使用以下方式调用：

```text
$skill-manager
```

## 重要边界

本 Skill 是现有 `skill-installer` 外围的分类与决策层，不替代其下载和认证机制。类目前缀别名只是指向正本的薄包装，不会复制或改名上游 Skill。
