# skill-manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`skill-manager` 是 Codex 的 Skill 安装入口与分类管理器。它会在下载任何目标 Skill 前，先简要说明该 Skill 的主要功能、流程和关键边界，再要求用户明确选择已有类目、新建类目或不分类。

## 为什么需要完整初始化

单独安装 `SKILL.md` 只能让 Codex 在语义匹配时调用 `skill-manager`，不能保证所有“安装 Skill”请求都先经过它。完整初始化会额外向全局 `~/.codex/AGENTS.md` 写入一条受标记管理的默认路由规则，因此这是推荐安装方式。

## 安装

先克隆仓库，然后运行交互式安装器：

```bash
git clone https://github.com/OasisAtlas/skill-manager.git
cd skill-manager
python3 scripts/install.py
```

安装器会提示：

```text
1. 完整初始化安装（推荐）：安装 Skill，并设置为所有 Skill 安装请求的默认入口
2. 仅安装 Skill：不修改全局 AGENTS.md
3. 取消
```

回车默认选择完整初始化。也可用于自动化：

```bash
python3 scripts/install.py --mode full
python3 scripts/install.py --mode skill-only
```

安装完成后请新开一个 Codex 任务，使 Skill 和全局规则稳定生效。更多细节见 [安装说明](docs/installation.md)。

## 默认安装流程

检查来源 → 简述对象 Skill 的能力与流程 → 读取已有类目 → 要求用户确认分类 → 调用官方 `skill-installer` 下载 → 记录分类 → 按需创建类目前缀别名。

分类始终可选，但分类决策不可跳过：

- 一个类目明显匹配：仍需确认是否进入该类目。
- 多个类目匹配：询问进入哪个。
- 没有匹配：询问新建类目或保持未分类。
- 用户可以随时选择不分类，也可以拒绝创建前缀别名。

## 分类模型

- 上游 Skill 的目录、名称和内容保持不变。
- 分类数据独立保存在 `~/.codex/skill-manager/catalog.json`。
- 一个 Skill 最多有一个主类目，也可以长期保持未分类。
- `$ppt-slide-maker` 一类前缀名称是显式调用别名，不是上游 Skill 的副本。

## 常用命令

```bash
python3 scripts/catalog.py inventory
python3 scripts/catalog.py list-categories
python3 scripts/catalog.py add-category --id presentation --label "演示文稿" --description "PPT、幻灯片与演示设计"
python3 scripts/catalog.py classify --skill slide-maker --category presentation --create-alias
python3 scripts/catalog.py record-unclassified --skill some-skill
python3 scripts/catalog.py unclassify --skill slide-maker --remove-alias
python3 scripts/verify_install.py
```

## 项目文档

- [安装与升级](docs/installation.md)
- [工作原理](docs/architecture.md)
- [行为规范](docs/behavior-spec.md)
- [数据与安全边界](docs/security.md)
- [参与开发](CONTRIBUTING.md)
- [版本记录](CHANGELOG.md)

## 兼容边界

`skill-manager` 负责安装前说明、分类决策和安装后登记；真正的下载、认证与来源处理仍交给 Codex 自带的 `skill-installer`。项目仅使用 Python 标准库。

## License

本项目采用 [MIT License](LICENSE) 开源，可自由使用、修改和分发，但需保留版权与许可声明。
