# Session 2026-06-27: X API 失败 → Web Search 降级成功案例

## 背景

Cron job 触发 X 关注流日报生成。X API 和 xurl 均不可用：
- `fetch_x_following_paginated.py` → `SSLEOFError(8, 'EOF occurred in violation of protocol')`（代理 TLS 握手失败）
- `xurl timeline` → 401 Unauthorized（OAuth token 过期）
- `urllib` 直连 → 403 Forbidden（无认证）

## 降级方案执行

### Step 1: 三路并行 Web Search

```python
# 路 1: X/Twitter 原始信号
web_search("AI news today June 27 2026 site:x.com OR site:twitter.com")

# 路 2: 模型发布
web_search("AI agent model release news June 27 2026 Claude GPT Gemini")

# 路 3: 开源动态
web_search("open source AI tool release GitHub trending June 2026")
```

### Step 2: Tier 1 源站深度提取

```python
web_extract(["https://www.buildfastwithai.com/blogs/ai-news-today-june-27-2026"])
web_extract(["https://aitoolsrecap.com/Blog/ai-news-june-27-2026"])
```

### Step 3: 信号评分 + 日报生成

从 buildfastwithai 提取 15 条新闻，从 aitoolsrecap 提取 5 条核心事件，交叉验证后生成日报。

## 产出信号

| 信号 | 来源 | 强度 |
|------|------|------|
| 白宫封堵 GPT-5.6 | aitoolsrecap + whitehouse.gov | 🔴 极强 |
| Anthropic 指控 Qwen 蒸馏攻击 | aitoolsrecap + buildfastwithai | 🔴 极强 |
| Alphabet 六天蒸发 $2690 亿 | buildfastwithai | 🟠 强 |
| OpenAI 考虑大幅降价 | buildfastwithai (WSJ 引用) | 🟠 强 |
| GPT-4.5 今日退役 | aitoolsrecap | 🟡 中 |
| Gemini 3.5 Pro 延期至 7 月 | buildfastwithai | 🟡 中 |
| Claude Opus 4.8 发布 | anthropic.com | 🟡 中 |
| 特朗普 AI 行政令 | whitehouse.gov | 🟠 强 |

## 关键发现

1. **buildfastwithai.com** 是最佳单源——每日 15 条新闻，含 Polymarket 赔率、定价对比、IPO 时间线、人才流动分析，信息密度极高
2. **aitoolsrecap.com** 是最佳补充——功能对比表（Fable 5 vs GPT-5.6）、政策事件时间线，适合做"重大信号"板块的结构化对比
3. 两个源交叉验证后，信号质量不亚于直接 X 关注流抓取
4. Web Search 降级模式的搜索查询优化见 `cron-fallback-workflow.md` Step 1

## 搜索查询效果

- `"AI news today June 27 2026 site:x.com OR site:twitter.com"` → 返回 aitoolsrecap 和 buildfastwithai 的聚合页（间接获取 X 信号）
- `"AI agent model release news June 27 2026 Claude GPT Gemini"` → 返回 felloai.com 模型对比、YouTube 视频、Reddit 讨论
- `"open source AI tool release GitHub trending June 2026"` → 返回 ossinsight.io 实时排名、GitHub trending 页面、ByteByteGo 分析

## 结论

当 X API 不可用时，Web Search 降级模式是**可靠的备用方案**。关键是知道哪些源站信息密度最高——buildfastwithai + aitoolsrecap 两个源就能覆盖 80% 的核心信号。
