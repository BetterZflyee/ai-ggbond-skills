# 飞书链接渲染规则补充（2026-06-14）

## 核心发现

飞书的自动URL识别**有条件限制**：

| 格式 | 渲染结果 | 原因 |
|------|----------|------|
| `https://x.com/...`（裸URL，前后有空格） | ✅ 可点击超链接 | 飞书自动识别 |
| `[🔗 原推](https://x.com/...)` | ✅ 可点击超链接 | Markdown链接语法 |
| `🔗 https://x.com/...`（emoji紧挨URL） | ❌ 可能显示为纯文本 | emoji干扰自动识别 |
| `` `https://x.com/...` ``（反引号包裹） | ❌ 代码块，不可点击 | 被当作行内代码 |

## 最佳实践

**所有链接统一使用Markdown链接语法**：
```
[🔗 原推](https://x.com/{username}/status/{tweet_id})
```

不要依赖裸URL的自动识别——尤其当URL前面有emoji、特殊字符、或在列表项中时，行为不可预测。

## 修改记录

- `analyst_prompt_template.md`：所有`🔗 https://...`改为`[🔗 原推](https://...)`
- `cron-job-prompt-template.md`：输出约束和验证清单更新
- `feishu-rendering.md`：最佳实践更新
- SKILL.md pitfall #5 和 #17：补充emoji+URL不可靠的说明
- cron job提示词：同步更新
