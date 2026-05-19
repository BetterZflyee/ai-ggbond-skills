# 2026-05-19 X关注流抓取输出工作流记录

## 背景
用户要求“获取当前X上的最新信息”。本次使用 `fetch_x_following_paginated.py 5` 抓取关注流，共约 300 条。

## 关键学习
分页抓取 5 页会输出 10万+ 字符 JSON。如果直接让终端返回完整 stdout，Hermes/终端工具会截断输出，后续分析会丢上下文。

## 推荐流程
```bash
set -a; [ -f ~/.hermes/.env ] && . ~/.hermes/.env; set +a
export HTTPS_PROXY=${HTTPS_PROXY:-http://127.0.0.1:7897}
python3 ~/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_following_paginated.py 5 > /tmp/x_following_latest.json
```

然后用 Python 读取 `/tmp/x_following_latest.json`，按以下维度精选：
- 主题关键词：Claude、Anthropic、Codex、OpenAI、GPT、Gemini、Hermes、Agent、Open Design、MCP、sandbox、token、llama.cpp、Qwen、MIT、CAD 等。
- 互动分：`likeCount + 2*retweetCount + replyCount`。
- 对用户有用性：优先选择能服务求职定位、AI转型专家人设、个人IP选题、工具工作流优化的内容。

## 输出建议
微信私聊场景下不要堆完整日报，优先输出：
1. 抓取范围和数量。
2. 5-6 条高信号主线。
3. 每条给判断，不只罗列推文。
4. 最后给“对飞哥有什么用”的行动建议/选题。
5. 链接使用裸 URL，不用反引号。

## 本次有效输出结构
- Claude/Anthropic：token limit、self-hosted sandboxes、MCP tunnels。
- OpenAI/Codex：Codex 可持续干活，开发者心智回流。
- Agent：约束工程、ReAct while loop、Hermes contributor/Kanban 信号。
- Open Design：400 templates/skills/design systems，agent-native creation。
- Local AI/OSS：llama.cpp + Qwen MTP 支持。
- 对飞哥的内容选题：Agent 约束工程；任务能力分层选模型。
