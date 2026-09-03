# 安装与升级

## 推荐：完整初始化安装

```bash
git clone https://github.com/OasisAtlas/skill-manager.git
cd skill-manager
python3 scripts/install.py
```

交互安装器会先推荐“完整初始化安装”，但必须由用户确认。该模式执行两件事：

1. 将 Skill 安装到 `${CODEX_HOME:-~/.codex}/skills/skill-manager/`。
2. 在 `${CODEX_HOME:-~/.codex}/AGENTS.md` 写入带起止标记的默认安装路由。

已有 `AGENTS.md` 不会被整体覆盖。第一次修改前，安装器会保留 `AGENTS.md.skill-manager.bak`；以后仅更新自己标记范围内的内容。

## 仅安装 Skill

在提示中选择第二项，或运行：

```bash
python3 scripts/install.py --mode skill-only
```

此模式不修改全局配置。`skill-manager` 仍允许隐式调用，但 Codex 是否在每次安装请求中命中它取决于语义路由，不能视为强制默认入口。

## 为什么手工复制后仍建议初始化

仅复制 Skill 文件不会自动建立全局默认路由，也不应由来源包静默改写用户的全局指令。因此，若采用手工复制，仍建议在仓库根目录运行：

```bash
python3 scripts/install.py --mode full
```

## 验证

```bash
python3 scripts/verify_install.py
```

三项均为 `PASS` 表示 Skill、Agent 元数据和默认路由都已就位。

## 升级

在仓库中拉取新版本后重新运行安装器。它只覆盖 `skill-manager` 自己的程序文件，不删除分类目录，也不会改写其他全局规则：

```bash
git pull --ff-only
python3 scripts/install.py --mode full
```

升级完成后新开一个 Codex 任务。
