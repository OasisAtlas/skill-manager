# 参与开发

提交变更前请保持职责边界：`skill-manager` 负责安装前决策与安装后登记，下载和认证继续交给官方 `skill-installer`。

本地检查：

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py .
```

新增行为时同步更新 `docs/behavior-spec.md`；改变安装或全局写入方式时同步更新 `docs/installation.md` 与 `docs/security.md`。不要提交本地分类目录、认证信息或 `docs/be-kobe/` 私人评测记录。
