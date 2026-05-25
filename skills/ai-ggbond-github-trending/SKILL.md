---
name: ai-ggbond-github-trending
description: 检索、筛选并解读 GitHub Trending 热门开源项目，输出适合飞哥的 AI Native、开发者工具、Agent、MCP、LLM 应用趋势洞察。Use when 用户提到 GitHub Trending、热门开源项目、趋势仓库、AI 项目发现、开发者工具发现、开源项目选题、公众号选题、副业机会或需要从 GitHub 热榜找人脉/商机。
version: 1.0.0
author: AI朱朱侠
license: MIT
metadata:
  hermes:
    tags: [github, trending, ai-native, developer-tools, research, content-ideas]
    related_skills: [ai-ggbond-article-writer, ai-ggbond-x-followings-feed, web-access]
---

# AI朱朱侠 GitHub Trending 趋势发现

## Overview

这个 Skill 用来围绕 `https://github.com/trending` 做轻量但有判断力的趋势发现：不是搬运热榜，而是帮助飞哥从开源项目里找到 AI Native 机会、开发者工具趋势、Agent/MCP/LLM 应用方向、人脉资源和可转化的公众号选题。

核心原则：**查、筛、判**。先稳定拿到 GitHub Trending 项目，再按语言、时间、关键词过滤，最后站在飞哥的求职/IP/副业视角判断“为什么值得关注”。

## When to Use

- 用户要查 GitHub Trending 今日/本周/本月热门项目。
- 用户指定语言，例如 Python、TypeScript、Go、Rust、JavaScript。
- 用户想找 AI、Agent、MCP、LLM、自动化、开发者工具方向的新项目。
- 用户要把开源热榜转化为公众号选题、产品机会、副业线索或可链接的人脉。
- 用户需要一份“项目清单 + 趋势判断 + 下一步动作”的简报。

不要用于：

- 严肃投资尽调：Trending 只能作为早期信号，不能替代财务、用户、商业化验证。
- 长期监控：定时推送应另建 cronjob，不写死在 Skill 里。
- 只看 star 排名：星标增长不等于真实价值，必须补充问题价值、用户场景和风险判断。

## Quick Start

优先使用本 Skill 自带脚本：

```bash
python /Users/admin/.hermes/skills/creative/ai-ggbond-github-trending/scripts/fetch_github_trending.py --since daily --limit 10 --markdown
```

按语言筛选：

```bash
python /Users/admin/.hermes/skills/creative/ai-ggbond-github-trending/scripts/fetch_github_trending.py --language python --since weekly --limit 10 --markdown
```

按关键词筛选 AI/Agent/MCP：

```bash
python /Users/admin/.hermes/skills/creative/ai-ggbond-github-trending/scripts/fetch_github_trending.py --since daily --limit 20 --keyword agent,mcp,llm,ai --markdown
```

输出 JSON 供二次分析：

```bash
python /Users/admin/.hermes/skills/creative/ai-ggbond-github-trending/scripts/fetch_github_trending.py --language typescript --since monthly --limit 20 --json
```

## Workflow

0. **先确认边界，不抢跑实现**
   - 当用户要求修改/升级本 Skill 的设计，尤其涉及“用户画像适配、跨 Agent 兼容、自动读取记忆、隐私边界、通用版 vs 私有版”等产品边界时，必须先连续追问并确认需求，不要直接改文件。
   - 推荐先确认：支持哪些 Agent、是否真的读取 profile 文件、profile 优先级、是否保留飞哥专属模式、输出中是否展示适配依据、无画像时默认框架。
   - 如果用户明确说“没明确需求前不要开始行动”，这一句优先级高于默认执行冲动。

1. **识别需求**
   - 时间范围：`daily` / `weekly` / `monthly`，默认 `daily`。
   - 语言：可选，转成 GitHub Trending slug，如 `python`、`typescript`。
   - 关键词：可选，逗号分隔，如 `agent,mcp,llm,rag,workflow,automation`。
   - 输出目标：清单、趋势简报、选题、商机、人脉跟进建议。

2. **抓取项目**
   - 用脚本请求 `https://github.com/trending/{language}?since={since}`。
   - 如果脚本失败，fallback 到 `web_extract` / browser / GitHub Search API。
   - 保留字段：repo、url、description、language、stars、forks、growth、built_by。

3. **筛选与去噪**
   - 关键词过滤只能作为第一层，不要漏掉描述不明显但方向相关的项目。
   - 对 AI Native 方向重点看：Agent、MCP、LLM、RAG、workflow、automation、eval、inference、devtool、browser、data、observability。
   - 对飞哥主线重点看：是否能服务求职背书、公众号内容、制造业/企业服务方案、副业工具、人脉链接。

4. **输出飞哥视角判断**
   - 不要只说“这个项目很火”。必须回答：
     - 它解决了什么真实问题？
     - 为什么现在爆？
     - 对 AI Native 超级个体有什么启发？
     - 对求职/IP/副业有什么可行动价值？
     - 是否值得联系作者/加入社区/做二创文章？

5. **给下一步动作**
   - 深挖 1-3 个项目 README、issues、roadmap。
   - 找项目作者的 X/GitHub/LinkedIn，用于人脉链接。
   - 生成 1-3 个公众号选题。
   - 如项目适配飞哥场景，提出“1小时复刻/试用/二创”的最小动作。

## Output Format

默认输出结构：

```md
## 一句话结论
[今天/本周/本月最值得关注的趋势，不超过 80 字]

## Top 项目清单
| Rank | Repo | Language | Stars | Growth | Why it matters |
|---:|---|---|---:|---:|---|
| 1 | owner/repo | Python | 12.3k | 1,234 stars today | ... |

## 值得飞哥深挖的项目
### 1. [repo]
- 项目定位：
- 解决的问题：
- 爆火原因：
- 对求职/IP/副业的价值：
- 下一步动作：

## 趋势判断
- 技术趋势：
- 产品趋势：
- 商业化可能：
- 风险/泡沫：

## 可转化内容选题
1. 《...》
2. 《...》
3. 《...》
```

## 飞哥专属判断框架

用四个问题快速判断一个 Trending 项目值不值得投入时间：

1. **场景真不真**：它解决的是刚需、效率痛点，还是 Demo 型炫技？
2. **扩散快不快**：是否顺应了模型能力、开源生态、开发者工作流变化？
3. **迁移值不值**：能否迁移到飞哥的求职表达、企业 AI 方案、公众号内容或副业工具？
4. **链接人不人**：是否值得 follow 作者、进 Discord/社区、主动交流建立人脉？

判断口径：

- **P0 深挖**：强相关 AI Native / Agent / MCP / 开发者工具，且有明确应用场景。
- **P1 关注**：方向有启发，但与飞哥当前主线间接相关。
- **P2 略过**：纯技术炫技、噪声榜、商业化/内容转化价值低。

## Script Reference

脚本位置：

```text
/Users/admin/.hermes/skills/creative/ai-ggbond-github-trending/scripts/fetch_github_trending.py
```

参数：

- `--language`: 可选，语言 slug，例如 `python`、`typescript`、`go`、`rust`、`javascript`。
- `--since`: `daily` / `weekly` / `monthly`，默认 `daily`。
- `--limit`: 返回数量，默认 20。
- `--keyword`: 逗号分隔关键词，本地过滤 repo 名称、描述、语言。
- `--json`: 输出 JSON。
- `--markdown`: 输出 Markdown 表格。

## Cross-Agent User Profile Adaptation

当本 Skill 被不同用户或不同 Agent 使用时，**不要把某一个人的身份写死进分析**。Skill 负责“怎么分析 GitHub Trending”，用户画像负责“为谁分析”。

本 Skill 的默认产品边界已确认：

1. **策略 + 脚本双层适配**：`SKILL.md` 要写清识别逻辑；脚本侧也应支持环境探测，且不要假设只存在 Hermes/Claude Code/Codex/OpenCode/OpenClaw，需保留未来 Agent 扩展位。
2. **只检测，不读取隐私内容**：脚本默认只检测 profile / memory / instruction 文件是否存在，不自动读取内容；由当前 Agent 已注入上下文或用户明确授权决定是否读取。
3. **三层上下文合并**：用户级 Profile 决定“为谁分析”，项目级 Context 决定“在什么项目语境里分析”，Skill 决定“怎么做分析”。多个 profile 同时存在时，不简单互相覆盖。
4. **保留 AI朱朱侠 IP 名称**：继续迭代 `ai-ggbond-github-trending`，但内部分析逻辑要可迁移，不写死“飞哥专属”。
5. **适配说明简短透明**：最终报告只简短显示“已按当前用户画像/当前 Agent 环境调整分析重点”，不要暴露具体 profile 路径或隐私内容。
6. **无画像时用通用五类框架**：Developer value、Product value、Business value、Content value、Network value。

常见 profile/context 探测位置（仅检测存在）：

| Agent / Context | 用户级画像候选 | 项目级上下文候选 |
|---|---|---|
| Hermes Agent | `~/.hermes/memories/USER.md`, `~/.hermes/memories/MEMORY.md` | `AGENTS.md`, `CLAUDE.md`, project skills |
| Claude Code | `~/.claude/CLAUDE.md`, `~/.claude/rules/*.md` | `./CLAUDE.md`, `./.claude/rules/*.md` |
| Codex | 全局 instructions/上层 `AGENTS.md`（若存在） | `./AGENTS.md`, 子目录 `AGENTS.md` |
| OpenCode/OpenClaw/Other | `~/.config/<agent>/AGENTS.md` 或工具配置 | `./AGENTS.md`, `./CLAUDE.md`, custom instructions |

详细设计与后续实现记录见 `references/cross-agent-user-profile-adaptation.md`。

## Fallback Strategy

GitHub Trending 没有官方 API，页面结构可能变。若脚本失败：

1. 用 `web_extract(["https://github.com/trending?... "])` 获取页面内容。
2. 如页面被压缩或解析失败，使用 browser 打开页面检查 DOM。
3. 必要时用 GitHub Search API 搜索近期高 star 仓库，但要明确这不是 Trending 等价数据。
4. 输出时标注数据来源和限制，不要假装精确。

## Common Pitfalls

1. **把 Trending 当真理。** Trending 是热度信号，不是价值证明。必须补“为什么值得关注/为什么可能是噪声”。
2. **只搬运项目列表。** 飞哥要的是判断、选题、人脉和商机，不是榜单复读机。
3. **关键词过滤过窄。** 很多好项目不会在描述里写 agent/llm/mcp，先全量抓取，再语义判断。
4. **忽略时间窗口。** Daily 看爆发，Weekly 看持续性，Monthly 看趋势稳定性。
5. **过度工程化。** 第一版只做查、筛、判；数据库、归档、定时推送后续按使用频率再加。
6. **页面解析脆弱。** GitHub 改 HTML 时脚本可能失效，保留 fallback，并优先输出清晰错误。

## Verification Checklist

- [ ] 脚本 `--help` 可用。
- [ ] `--since daily --limit 5 --markdown` 能返回表格或清晰错误。
- [ ] `--language python --since weekly --limit 10 --json` 输出可被 `json.loads` 解析。
- [ ] `--keyword agent,mcp,llm` 能过滤结果；无匹配时不崩溃。
- [ ] 输出字段至少包含 repo、url、description、language、stars、forks、growth。
- [ ] 最终回答必须包含飞哥视角判断，而不是只贴榜单。
