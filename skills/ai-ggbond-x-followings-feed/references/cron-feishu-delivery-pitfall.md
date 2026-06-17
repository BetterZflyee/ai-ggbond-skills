# Cron 飞书投递问题 — 完整记录

**验证日期**: 2026-05-28
**环境**: Hermes Agent + Feishu/Lark 集成

## 问题

Hermes cron 任务执行成功（`last_status: ok`），但输出无法推送到飞书对话。

## 测试结果

| 投递模式 | 配置 | 结果 |
|---------|------|------|
| `origin` | `deliver: origin` | ❌ `[230002] Bot/User can NOT be out of the chat` |
| 硬编码 chat_id | `deliver: feishu:oc_3b8269b4b50e2664edeaf882a578cbe7` | ❌ 同上 |
| 本地文件 | `deliver: local` | ✅ 输出保存到 `~/.hermes/profiles/<profile>/cron/output/` |

## 根因分析

**Feishu 错误码 230002**: "Bot/User can NOT be out of the chat"

说明 cron 执行环境中的机器人身份与当前飞书对话的机器人身份不是同一个，或 cron 执行上下文中缺失飞书会话绑定。

可能原因：
1. Cron 以独立 session 执行，不继承对话的飞书上下文
2. Cron 执行时的机器人 token 或身份与对话 Bot 不同
3. `origin` 在 cron 上下文中解析到了错误的 chat_id（可能是模板/默认值）

## 当前方案

```bash
# cron 任务配置
deliver: local  # 输出保存到本地文件
schedule: 0 7 * * *
```

输出路径: `~/.hermes/profiles/touyan/cron/output/`

## 待探索解法

1. **两步法**: cron 跑完存本地 → 另一个任务/会话读取文件 → 用 `send_message` 推飞书
2. **Webhook**: cron 输出 → 飞书 webhook → 群/个人消息
3. **直接在当前会话执行**: 放弃 cron 投递，改为 cron 只存文件，手动或定时触发读取

## 会话工具差异

另注：当前飞书对话会话中，Agent 可能没有 `terminal` 或 `web_search` 工具（工具集与 cron 执行环境不同）。这意味着：
- Cron 环境：✅ 能跑 fetch 脚本、能搜索
- 飞书对话：❌ 可能缺 terminal，只能通过 browser_* 或依赖 cron 后台执行
