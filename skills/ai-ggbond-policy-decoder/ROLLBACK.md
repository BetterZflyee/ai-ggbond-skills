# AI GGbond 政策解码器 · 版本与回滚手册

## 版本号规则（语义化）

`MAJOR.MINOR.PATCH`

| 位 | 何时进位 | 例子 |
|---|---|---|
| **MAJOR** | 框架重构，输出契约不兼容（如改了七参数或三时间线语法） | 1.0.0 |
| **MINOR** | 新增参考文件 / 新增阶段 / 新增领域 playbook | 0.2.0 |
| **PATCH** | 修错字、调阈值、改提示词、补案例 | 0.1.1 |

**当前阶段**：0.x = 探索期，允许破坏性变更，但**每次必须升 MINOR 并写 CHANGELOG**。

---

## 每次修改的标准动作（四步，不许跳）

```bash
cd ~/.hermes/skills/ai-ggbond-policy-decoder

# 1. 改之前先拉一个安全点（如果工作区干净可跳过）
git status

# 2. 改内容（改 SKILL.md / references / scripts）

# 3. 改 VERSION + 在 CHANGELOG.md 顶部加一条
#    格式：## [x.y.z] - YYYY-MM-DD
#          ### 变更 / ### 修正 / ### 已知问题

# 4. 提交并打标签（用脚本，避免打错版本号）
./scripts/version.sh ship "一句话说明这次改了什么"
```

`version.sh ship` 会做三件事：校验 VERSION 与 CHANGELOG 一致 → commit → 打 `v<版本>` 标签。

---

## 回滚方法

### 看有哪些版本
```bash
./scripts/version.sh list
```

### 整个技能退回某个版本（推荐）
```bash
./scripts/version.sh rollback v0.1.0
```
它会先自动打一个 `pre-rollback-<时间戳>` 的标签（保证回滚操作本身也可回滚），
然后把工作区文件恢复到目标版本，并留出一个未提交的 diff 供你确认。

### 只回退某个文件
```bash
git checkout v0.1.0 -- references/horizons.md
git diff --cached
```

### 撤销上一次提交（还没 push 时）
```bash
git reset --soft HEAD~1     # 保留改动，撤掉提交
git reset --hard HEAD~1     # 连改动一起丢（谨慎）
```

### 确认回滚结果
```bash
cat VERSION
git log --oneline -5
python3 scripts/policy_card.py --selftest
```

---

## 保险措施

1. **每次 ship 自动打 tag**，标签就是最可靠的版本快照。
2. **回滚前自动打 `pre-rollback-*` 标签**，防止回滚本身不可逆。
3. **`ledger/` 目录不进版本回滚范围**——预测台账是历史事实，回滚代码不能回滚它。
   已在 `.gitignore` 中单独处理：台账**入库但不随 rollback 覆盖**（rollback 用 `git checkout <tag> -- <paths>` 精确到路径，不含 ledger）。
4. **外部备份**：`cp -r` 到 `~/.hermes/skills-backup/ai-ggbond-policy-decoder-<版本>-<日期>/`，用于 git 仓库本身损坏时兜底。

---

## Git 仓库信息

- 位置：`~/.hermes/skills/ai-ggbond-policy-decoder`（独立仓库，不影响 `ai-ggbond-skills` 发布仓库）
- 远程：暂不推送。等 1.0 稳定后再同步进 `BetterZflyee/ai-ggbond-skills`。
- 合并方式：`cp -r` 到 `ai-ggbond-skills/skills/ai-ggbond-policy-decoder` 后统一 commit。
