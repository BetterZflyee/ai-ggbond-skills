# 本地维护

GitHub 源码位于仓库的 `skills/ai-ggbond-sticker-writer`，精排位于同级 `ai-ggbond-wechat-layout`。此台工作机的维护副本位于 `/Volumes/station/Felix Station/products/`。安装器通过 `--home` 指定用户目录，部署 Hermes、Codex、共享 agents 三份技能入口。

```bash
python3 "<sticker-source>/scripts/install_local.py" \
  --home "/Users/admin" \
  --layout-source "<layout-source>" \
  --backup-dir "/path/to/private-backups"
```

本命令默认仅检查与显示计划。升级已经获得授权、计划核对完成后加 `--apply`，无需再次要求用户批准。系统沙箱仍需按当前工具要求处理。可选 `--baseline /path/to/inventory.json` 用于初始盘点后的变更检查。

安装器只同步两种技能的三个副本，在四个写作、三个长图和三个发布入口中维护标记块，并应用发布器的原生贴图适配文件。它保留标记块之外的正文、已有精排入口和发布器其他文件。所有目标先备份，备份仅当前用户可读；写入后核对文件哈希，写入失败恢复原版本。已安装相同版本时再次执行计划没有变更。

发布补丁要求已知基线哈希，未知发布器版本不会强行覆盖。修改过发布器时应先重新合并与验证 `adapters/wechat-api-sticker.patch`，并更新 `publisher-adapter.json`；不能仅修改预期哈希跳过合并。适配器源文件是 `adapters/newspic-bundle.ts`。

Hermes 的旧合集还曾提供同名 v2.7 入口。新版吸收其杂志默认、平台分工和模型约定后，将该入口保留为 `SKILL.legacy-v2.7.md`，其余文件和 Git 修改原样保留；它不再参加 `SKILL.md` 索引，避免同名歧义。安装器只处理已盘点哈希的旧入口；若上游恢复了不同内容，先合并，不能强行停用。已升级的仓库入口若与当前源码一致则保留，Hermes 会将相同入口去重，因此可以直接从更新后的仓库安装。

本地检查：

```bash
python3 -m unittest discover -s "<sticker-source>/tests" -p 'test_*.py'
bun test "<sticker-source>/tests/newspic-bundle.test.ts"
```

Python 的旧生图导入测试需要已安装的 requests/Pillow；测试通过模拟配置与网络，不能据此声称模型已生成图片。浏览器预览与发布器 dry-run 不访问微信账号或创建草稿。平台读回与真机显示另行记录。
