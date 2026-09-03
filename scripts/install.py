#!/usr/bin/env python3
"""Install skill-manager and optionally initialize its global routing rule."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


START_MARKER = "<!-- skill-manager:default-install-route:start -->"
END_MARKER = "<!-- skill-manager:default-install-route:end -->"
PACKAGE_ITEMS = ("SKILL.md", "agents", "scripts", "templates")


def resolve_codex_home(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def choose_mode() -> str:
    print("请选择安装方式：")
    print("1. 完整初始化安装（推荐）：安装 Skill，并设置为所有 Skill 安装请求的默认入口")
    print("2. 仅安装 Skill：不修改全局 AGENTS.md")
    print("3. 取消")
    try:
        answer = input("选择 [1]: ").strip()
    except EOFError as error:
        raise ValueError("无法读取交互选择；请显式传入 --mode full 或 --mode skill-only") from error
    answer = answer or "1"
    choices = {"1": "full", "2": "skill-only", "3": "cancel"}
    if answer not in choices:
        raise ValueError(f"无效选择：{answer}")
    return choices[answer]


def install_package(source: Path, destination: Path) -> None:
    if source.resolve() == destination.resolve():
        return
    destination.mkdir(parents=True, exist_ok=True)
    for name in PACKAGE_ITEMS:
        source_item = source / name
        destination_item = destination / name
        if source_item.is_dir():
            shutil.copytree(
                source_item,
                destination_item,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
            )
        elif source_item.is_file():
            shutil.copy2(source_item, destination_item)


def render_rule(source: Path, codex_home: Path) -> str:
    template = (source / "templates" / "AGENTS.default-route.md").read_text(encoding="utf-8")
    return template.replace("${CODEX_HOME}", str(codex_home))


def initialize_global_route(agents_path: Path, rule: str) -> str:
    existing = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    if (START_MARKER in existing) != (END_MARKER in existing):
        raise ValueError(f"{agents_path} 中的 skill-manager 标记不完整，拒绝自动修改")
    if START_MARKER in existing:
        prefix, remainder = existing.split(START_MARKER, 1)
        _, suffix = remainder.split(END_MARKER, 1)
        updated = prefix.rstrip() + "\n\n" + rule.strip() + suffix
    else:
        updated = existing.rstrip() + ("\n\n" if existing.strip() else "") + rule.strip() + "\n"
    if updated == existing:
        return "unchanged"
    agents_path.parent.mkdir(parents=True, exist_ok=True)
    backup = agents_path.with_name("AGENTS.md.skill-manager.bak")
    if agents_path.exists() and not backup.exists():
        shutil.copy2(agents_path, backup)
    temporary = agents_path.with_suffix(".md.skill-manager.tmp")
    temporary.write_text(updated, encoding="utf-8")
    temporary.replace(agents_path)
    return "updated"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--mode", choices=("full", "skill-only"), help="Skip the interactive choice")
    result.add_argument("--codex-home", help="Override CODEX_HOME")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        mode = args.mode or choose_mode()
        if mode == "cancel":
            print("已取消，未修改任何文件。")
            return 0
        source = Path(__file__).resolve().parent.parent
        codex_home = resolve_codex_home(args.codex_home)
        destination = codex_home / "skills" / "skill-manager"
        install_package(source, destination)
        route_status = "not-requested"
        if mode == "full":
            route_status = initialize_global_route(codex_home / "AGENTS.md", render_rule(source, codex_home))
        print(f"Skill 已安装：{destination}")
        if mode == "full":
            print(f"默认安装路由：{route_status}（{codex_home / 'AGENTS.md'}）")
        else:
            print("未修改全局 AGENTS.md；安装请求只能依赖 Skill 的语义触发。")
        print("请新开一个 Codex 任务后使用。")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
