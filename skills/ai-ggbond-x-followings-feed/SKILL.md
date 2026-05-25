---
name: ai-ggbond-x-followings-feed
version: 1.5.0
author: "AI GGBond"
license: MIT
description: |
  Auto-fetch latest tweets from your X/Twitter followings and generate structured AI digest. Supports custom time ranges: 1 day, 3 days, 7 days, or custom.

  自动抓取X/Twitter关注列表的最新推文，并使用AI分析师提示词生成结构化日报。支持自定义时间段：1天、3天、7天或自定义天数。

  **Trigger Words:**
  - "summarize my followings", "X digest", "Twitter summary", "tweets from last 3 days", "weekly summary"

  **触发词：**
  - "总结关注列表", "X日报", "Twitter摘要", "过去3天的推文", "一周摘要"

  **Prerequisites:** X auth via AUTH_TOKEN & CT0 env vars + Proxy (HTTPS_PROXY) for China users
---

# X关注列表日报生成器 / X Followings Digest Generator

自动抓取你关注的人的最新推文，并生成结构化的AI日报。

Auto-fetch latest tweets from your followings and generate structured AI digest.

**Hermes 路径:** `~/.hermes/skills/ai-ggbond-x-followings-feed/`
**GitHub:** `github.com/BetterZflyee/ai-ggbond-skills/skills/ai-ggbond-x-followings-feed/`

**v1.5.0 更新：** 新增「🎯 个人视角」Personal Lens 汇总分析。日报末尾从 Hermes Memory 动态读取当前用户的身份、主线和偏好，生成定制化的信号解读与行动建议。**用户无关设计**：技能本身不硬编码任何用户状态，谁用就结合谁的 Memory — 飞哥用就是求职/制造业/IP，别人用就是别人的主线。每期日报不再只是信息搬运，而是当前用户的私人战略情报官。

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

### 2. 配置代理（中国大陆必需）

在中国大陆，`x.com` 被 SNI 封锁，**必须通过代理**访问。

```bash
# 临时设置（替换为你的代理端口）
export HTTPS_PROXY=http://127.0.0.1:7897  # Clash Verge 默认端口

# 持久化到 Hermes（推荐）
echo 'HTTPS_PROXY=http://127.0.0.1:7897' >> ~/.hermes/.env
```

**验证代理可用**：
```bash
curl -I --max-time 5 -x http://127.0.0.1:7897 https://x.com
# 应返回 HTTP 200 或 302
```

### 3. 获取关注列表推文 / Fetch Tweets

**⚠️ 重要：使用 Python 脚本获取关注流（推荐）**

bird CLI 不支持代理，且获取的是 "For You" 推荐流。**推荐使用 Python 脚本直接获取关注流**：

```bash
# 设置代理（中国大陆必需）
export HTTPS_PROXY=http://127.0.0.1:7897

# 获取关注流（推荐：分页获取更多数据）
python3 ~/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_following_paginated.py 5
# 参数：页数（默认3页，约120条推文；5页约200条）

# 快速获取（单页约40条）
python3 ~/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_timeline.py 40
```

**用户偏好**：飞哥希望获取尽可能多的关注流数据，不要只获取20条。建议默认使用分页脚本获取 3-5 页（120-200条推文）。

**也可以用 bird CLI（不推荐，有局限）**：
```bash
# bird CLI 获取 "For You" 推荐流（不是关注流！）
bird home --json -n 20

# bird CLI 获取关注流（但不支持代理，中国大陆无法使用）
bird home --following --json -n 20
```

### 3. 生成日报 / Generate Digest

将获取到的推文内容，使用 [analyst_prompt_template.md](references/analyst_prompt_template.md) 中的提示词模板进行分析。

Feed the fetched tweets to the AI using the prompt template in `references/analyst_prompt_template.md`.

**推荐流程 / Recommended workflow:**

```bash
# 1. 抓取推文到文件
python3 ~/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_following_paginated.py 5 > /tmp/x_following_latest.json
```

```python
# 2. 内联打分过滤（推荐：用 execute_code，逻辑可见可调）
#    移除 RT、低信号，按 engagement + 信号关键词排序，取 top 50
#    详见 references/curation-heuristics.md
```

```
# 3. 基于过滤结果 + analyst_prompt_template.md 生成日报
#    日报末尾自动追加「🎯 个人视角」— 从 Memory 读取用户状态生成
```

也可用 `scripts/curate_and_score.py` 做离线打分（`python3 .../curate_and_score.py /tmp/x_following_latest.json --top 50`），但推荐内联方式以便按场景调整信号权重。

## 输出格式 / Output Format

日报包含以下分类（仅显示有内容的类别）：

Digest includes (only shows categories with content):

- **🔥 重大事件 / Major Events** - 具体细节和影响分析 / Specific details & impact analysis
- **🚀 产品发布 / Product Releases** - 新模型、API更新、工具版本 / New models, API updates, tools
- **💡 技术洞察 / Tech Insights** - 技术方案、优化技巧、代码片段 / Technical solutions, optimizations
- **🔗 资源汇总 / Resources** - 论文、开源项目、教程、工具 / Papers, OSS, tutorials, tools
- **🎁 福利羊毛 / Deals & Freebies** - 免费额度、优惠、赠品 / Free credits, discounts, giveaways
- **📊 舆情信号 / Signals** - 争议话题、预测、警告 / Controversies, predictions, warnings
- **🎯 个人视角 / Personal Lens** - 从 Memory 动态读取当前用户状态，生成定制化信号解读与行动建议（用户无关设计，谁用就结合谁的记忆）— 详见 [references/curation-heuristics.md](references/curation-heuristics.md) § Memory-driven Personal Lens workflow

## 语言设置 / Language Setting

在调用AI分析时，通过提示词指定输出语言：

When calling the AI, specify output language in the prompt:

- **中文输出**: 使用提示词中的 [中文] 部分
- **English Output**: Use the [EN] section in the prompt template
- **中英双语**: 使用完整提示词，要求 bilingual output

## 依赖 / Dependencies

- `bird` CLI (X/Twitter client) — **不支持代理，中国大陆需用 Python fallback**
- `AUTH_TOKEN` & `CT0` from browser cookies
- Python 3 + `requests` 库（作为 bird CLI 的代理环境 fallback）

## Pitfalls / 踩坑记录

> **详细踩坑记录**：[references/x-api-pitfalls.md](references/x-api-pitfalls.md)

**核心踩坑点**：

1. **`bird home` ≠ 关注流**：`bird home` 获取的是 "For You" 推荐流（算法推荐），不是你关注的人的推文。必须加 `--following` 参数：`bird home --following --json -n <count>` 才能获取 "Following" 关注流。

2. **bird CLI 不支持代理**：bird CLI 是 Node.js 脚本，使用原生 `fetch` API，**不响应** `HTTP_PROXY`/`HTTPS_PROXY` 环境变量。中国大陆必须使用 Python 脚本 fallback。

3. **Following 流数据结构不同**：用户信息在 `.core` 不是 `.legacy`，解析时需兼容两种结构。

4. **数据量偏好**：用户希望获取更多数据（120-200条），不要只获取 20-40 条。使用分页脚本 `fetch_x_following_paginated.py`。

5. **飞书链接格式**：输出日报时，链接**不要用反引号包裹**。裸URL `https://x.com/...` 在飞书会自动识别为可点击超链接；反引号 `` `https://...` `` 会渲染成代码块，不可点击。已更新 `analyst_prompt_template.md` 中所有链接为裸URL格式。

## Fallback: Python 直连 X GraphQL API（代理环境）

当 bird CLI 不可用时（特别是需要代理的环境），使用 Python 脚本直接调用 X 的 GraphQL API：

```bash
# 设置代理并运行
export HTTPS_PROXY=http://127.0.0.1:7897

# 分页获取关注流（推荐，3页约120条，5页约200条）
python3 ~/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_following_paginated.py 5

# 单页快速获取（约40条）
python3 ~/.hermes/skills/ai-ggbond-x-followings-feed/scripts/fetch_x_timeline.py 40
```

脚本位置：
- `scripts/fetch_x_following_paginated.py` — 分页获取关注流（推荐）
- `scripts/fetch_x_timeline.py` — 单页获取 For You 推荐流
- `scripts/fetch_followings_tweets.sh` — bird CLI 封装（不支持代理）

API 详情：
- [references/x-api-pitfalls.md](references/x-api-pitfalls.md) — 踩坑记录与 API 细节
- [references/x-graphql-api.md](references/x-graphql-api.md) — GraphQL API 文档

## 写作与推广 / Writing & Positioning

写文章或向他人介绍本 skill 时，可参考 `references/market-context.md`，包含：
- X/Twitter API 市场现状与竞品对比
- 信息聚合工具生态概览
- 本 skill 的差异化定位与核心痛点
- 适用人群画像

## 注意事项 / Notes

- 推文数量越多，处理时间越长
- More tweets = longer processing time
- 建议设置定时任务每日自动运行
- Recommended: set up cron job for daily auto-run

## 输出增强 / Output Enhancements

- 脚本自动为每条推文和引用推文拼接 `url` 字段（格式: `https://x.com/{username}/status/{id}`）
- Prompt 模板强制每条内容附带原推链接，不得省略
- 网络预检：脚本会先 curl x.com 测试连通性，不通则快速报错（避免 bird 挂起 30 秒）
- **飞书链接格式**：详见 [references/feishu-rendering.md](references/feishu-rendering.md) — 裸URL自动识别为超链接，反引号包裹会渲染为代码块（不可点击）
- **汇总取舍**：默认优先整理最近 120–200 条中的高信号内容；纯 RT 仅在自身信息量高时保留。
- **筛选策略**：优先保留含版本号、benchmark、价格、产品名、仓库/论文链接的内容；对泛泛观点做降权处理。
- **避免终端输出截断**：分页脚本抓 5 页会产生 10万+ 字符 JSON，直接在终端展示容易被截断。生产流程应先重定向到 `/tmp/x_following_latest.json`，再用 Python/execute_code 解析、打分和精选，最后只输出高信号摘要。
- **脚本笔记**：常见解析坑与精选规则见 [references/curation-heuristics.md](references/curation-heuristics.md)
- **会话案例**：5页关注流抓取、避免 stdout 截断、Python精选与微信私聊摘要结构见 [references/session-2026-05-19-output-workflow.md](references/session-2026-05-19-output-workflow.md)
