---
name: ai-ggbond-x-followings-feed
version: 1.2.0
author: "AI GGBond"
license: MIT
description: |
  Auto-fetch latest tweets from your X/Twitter followings and generate structured AI digest. Supports custom time ranges: 1 day, 3 days, 7 days, or custom.

  自动抓取X/Twitter关注列表的最新推文，并使用AI分析师提示词生成结构化日报。支持自定义时间段：1天、3天、7天或自定义天数。

  **Trigger Words:**
  - "summarize my followings", "X digest", "Twitter summary", "tweets from last 3 days", "weekly summary"

  **触发词：**
  - "总结关注列表", "X日报", "Twitter摘要", "过去3天的推文", "一周摘要"

  **Prerequisites:** X auth via AUTH_TOKEN & CT0 env vars
---

# X关注列表日报生成器 / X Followings Digest Generator

自动抓取你关注的人的最新推文，并生成结构化的AI日报。

Auto-fetch latest tweets from your followings and generate structured AI digest.

**Hermes 路径:** `~/.hermes/skills/ai-ggbond-x-followings-feed/`
**GitHub:** `github.com/BetterZflyee/ai-ggbond-skills/skills/ai-ggbond-x-followings-feed/`

## 快速开始 / Quick Start

### 1. 配置X授权 / Configure X Auth

从浏览器提取 cookie：
1. 登录 x.com
2. 打开 DevTools → Application → Cookies → x.com
3. 复制 `auth_token` 和 `ct0` 的值

```bash
export AUTH_TOKEN="your_auth_token"
export CT0="your_ct0"
```

持久化到 Hermes 环境（推荐）：
```bash
echo 'AUTH_TOKEN=your_auth_token' >> ~/.hermes/.env
echo 'CT0=your_ct0' >> ~/.hermes/.env
# 重启 gateway 使生效
```

**安全提醒**：这两个 cookie 等同于你的 X 账号 session，不要转发给别人，配置完建议每隔几个月刷新一次。

### 2. 获取关注列表推文 / Fetch Tweets

**⚠️ 踩坑记录 / Pitfall：**

原脚本使用 `bird following --json`，该命令返回的是**关注用户列表**（profile），不是推文内容。
正确的命令是 `bird home --json -n <count>`，获取 Home Timeline 推文。

```bash
# 获取最近推文（推荐方式）
# 20条推文，默认
bird home --json -n 20

# 50条推文
bird home --json -n 50

# 也可以用脚本（脚本内部已修复为 bird home）
./scripts/fetch_followings_tweets.sh        # 默认20条
./scripts/fetch_followings_tweets.sh 50 1   # 50条, 最近1天
./scripts/fetch_followings_tweets.sh 100 7  # 100条, 最近7天
```

**注意：** `bird home` 返回的 JSON 中，每条推文包含 `text`, `author.username`, `author.name`, `createdAt`, `likeCount`, `retweetCount`, `replyCount` 等字段，以及可选的 `quotedTweet`（引用推文）。

### 3. 生成日报 / Generate Digest

将获取到的推文内容，使用 [analyst_prompt_template.md](references/analyst_prompt_template.md) 中的提示词模板进行分析。

Feed the fetched tweets to the AI using the prompt template in `references/analyst_prompt_template.md`.

## 输出格式 / Output Format

日报包含以下分类（仅显示有内容的类别）：

Digest includes (only shows categories with content):

- **🔥 重大事件 / Major Events** - 具体细节和影响分析 / Specific details & impact analysis
- **🚀 产品发布 / Product Releases** - 新模型、API更新、工具版本 / New models, API updates, tools
- **💡 技术洞察 / Tech Insights** - 技术方案、优化技巧、代码片段 / Technical solutions, optimizations
- **🔗 资源汇总 / Resources** - 论文、开源项目、教程、工具 / Papers, OSS, tutorials, tools
- **🎁 福利羊毛 / Deals & Freebies** - 免费额度、优惠、赠品 / Free credits, discounts, giveaways
- **📊 舆情信号 / Signals** - 争议话题、预测、警告 / Controversies, predictions, warnings

## 语言设置 / Language Setting

在调用AI分析时，通过提示词指定输出语言：

When calling the AI, specify output language in the prompt:

- **中文输出**: 使用提示词中的 [中文] 部分
- **English Output**: Use the [EN] section in the prompt template
- **中英双语**: 使用完整提示词，要求 bilingual output

## 依赖 / Dependencies

- `bird` CLI (X/Twitter client)
- `AUTH_TOKEN` & `CT0` from browser cookies

## Pitfalls / 踩坑记录

1. **`bird following` ≠ 推文**：`bird following --json` 返回的是关注用户列表（profile），不是推文内容。获取推文必须用 `bird home --json -n <count>`。
2. **网络不通时 bird 会挂起30秒+**：如果 x.com 不可达（无VPN/代理），bird CLI 会超时。脚本已加入 `curl` 连通性预检，5秒内快速失败。
3. **cookie 会过期**：AUTH_TOKEN 和 CT0 来自浏览器 session cookie，浏览器登出或 session 刷新后需要重新提取。
4. **env 变量需 source**：`~/.hermes/.env` 中的变量需要 gateway 重启后才对 Hermes 生效；直接命令行使用需 `export` 或 `source`。
5. **日期过滤是 best-effort**：脚本计算了 `SINCE_TIMESTAMP` 但 bird CLI 本身不支持时间过滤，实际过滤靠 AI 分析时判断推文日期。

## 注意事项 / Notes

- 推文数量越多，处理时间越长
- More tweets = longer processing time
- 建议设置定时任务每日自动运行
- Recommended: set up cron job for daily auto-run

## 输出增强 / Output Enhancements

- 脚本自动为每条推文和引用推文拼接 `url` 字段（格式: `https://x.com/{username}/status/{id}`）
- Prompt 模板强制每条内容附带原推链接，不得省略
- 网络预检：脚本会先 curl x.com 测试连通性，不通则快速报错（避免 bird 挂起 30 秒）
