# Cron/Headless 环境 Fallback 工作流

> 当在 cron job、headless 环境、或没有 bash/terminal 工具的环境中运行时，fetch 脚本无法执行。此文档记录 Web Search 聚合的替代方案。

## 适用场景
- Cron job 定时任务（无交互终端）
- Hermes Agent 环境中 `bash`/`terminal` 工具被禁用或不可用
- X API 认证失效或有网络问题时的降级方案

## Fallback 流程

### 第一步：多路 Web Search
同时发起 4-5 路 web_search，覆盖不同维度：

```
1. "AI news today [当前日期] latest LLM release"
2. "AI agent open source tool [当前年月] latest release"
3. "Claude GPT Gemini benchmark new model [当前年月]"
4. "AI product launch pricing free credit [当前年月]"
5. "AI agent framework developer tools news [当前年月] MCP"
```

### 第二步：深挖具体事件
用 web_extract 获取高信号源站的详细内容：
- `https://www.buildfastwithai.com/blogs/ai-news-today-[日期]` — 每日 AI 新闻汇总
- `https://llm-stats.com/ai-news` — LLM 发布追踪
- `https://press.airstreet.com/p/state-of-ai-[月份]-[年份]` — Air Street Press 月度分析
- `https://blog.mean.ceo/new-ai-model-releases-news-[月份]-[年份]` — 创始人视角模型发布汇总
- `https://fazm.ai/t/new-ai-model-release-or-paper-or-open-source-[日期]` — 日历日级 AI 动态

### 第三步：生成日报
按照 `analyst_prompt_template.md` 格式输出，但需注意：
- 由于不是 X 关注流，没有具体的 `username`/`tweet_id`，用源站 URL 替代链接
- 分类和筛选逻辑不变
- Personal Lens 照常执行（Memory 可用时从 Memory 读用户状态，不可用时从系统提示提取）

## 局限性
- 信息源是聚合站点而非原始推文，时效性略低
- 无法按用户关注列表个性化筛选（但 Personal Lens 层面对齐用户主线可弥补）
- 数量取决于 web_search 返回量，一般可获取 60-100 条高质量信号
- 无互动数据（like/retweet/reply），评分无法用 engagement 维度

## 优势
- 不依赖 X API 和代理，可靠性更高
- 多个聚合源交叉验证，减少单一信息源偏差
- 适合定时任务的容错设计
