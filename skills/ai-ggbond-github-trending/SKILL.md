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
   - 如项目适配飞哥场景，提出"1小时复刻/试用/二创"的最小动作。
   - **主动询问是否要安装**：当用户问"有什么好玩的"或看完整个 Trending 报告后，对 P0/P1 级项目主动问"要帮你装上吗？"。用户看到好项目后往往想立刻试用，不要等用户自己提。安装流程参考 `clawhub-skills-install-to-hermes` 技能（ClawHub 技能 vs GitHub 完整项目要区分清楚）。

## Output Format

### 格式铁律

1. **飞书不支持 Markdown 表格**，所有表格数据统一用代码块展示。非飞书平台可用标准表格。
2. **Star 数和增长数必须突出**，是读者第一眼看到的数字。
3. **深挖项目按相关性优先级排序**（P0 > P1 > P2），不按增长排名。
4. **每个选题必须有标题+一句话切入角度**，标题要有判断、有钩子，不做新闻搬运。

See `references/feishu-formatting.md` for complete Feishu formatting rules.

### 输出结构（6 段式）

> 完整模板见 `templates/trending_report.md`

```md
## 一句话结论
[时间范围内最值得关注的趋势，不超过 80 字，要有判断]

### 🏆 增长 Top 5
（代码块格式，每个项目：排名 / 项目名 ⭐ 总Star (+周增长/周) / 语言 | 一句话核心价值）

### 📊 完整榜单（按周增长排序）
（代码块格式，表头：项目 / 总 Star / 周增长 / 语言 / 简介，建议 15-25 个）

### 🎯 值得深挖的项目
（选择标准：与目标受众主线相关 + 周增长 Top 10 + 有明确场景价值）
每个项目 5 个维度：
- 项目定位：一句话说清楚它是什么
- 解决的问题：它到底在解决什么真实痛点
- 爆火原因：为什么是现在爆，不是半年前
- 对[目标受众]的价值：P0/P1/P2，具体说明和受众主线的关系
- 下一步：一个可执行的最小动作（试用/写文/联系作者/对比分析）
（深挖 3-6 个项目，根据实际情况调整数量）

### 📈 趋势判断
4 个维度：
- 技术趋势：从数据中提炼的技术方向信号，2-3 条
- 产品趋势：从数据中提炼的产品形态信号，1-2 条
- 商业化可能：可落地的商业机会，2-3 条
- 风险/泡沫：需要警惕的泡沫或噪声，1-2 条

### ✍️ 可转化内容选题
（3-5 个选题，每个：标题 + 一句话说明切入角度）
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

## Skill Discovery: Ranking by Fit, Not Stars

当用户问 GitHub 上“有什么好 Skill”，尤其带有具体工作场景（如给领导汇报、项目周报、方案材料），不要把 Trending 或 Star 当作推荐结论。Star 是传播信号，不是场景适配或文本可靠性的证明。

### 必做筛选

1. **先识别交付对象与风险**：汇报对象是领导/客户/公众，还是日常社媒；是否必须保留数字、时间、责任人、风险、待决策事项。
2. **分清两类能力**：
   - `结构技能`：把进度、风险、待决事项、下一步组织成决策友好的材料；
   - `去 AI 味技能`：删模板腔、宣传腔和空话。两者不可互相替代。
3. **优先验证仓库原始 README / SKILL.md**：确认具体场景、事实保护、语体边界、测试/评测和目标 Agent 兼容性；搜索摘要只用于发现候选。
4. **按适配度排序，Star 只作括号信息**：给出 P0/P1/P2 和适用边界，不要混排一个“高 Star 榜单”。
5. **汇报材料的红线**：避免推荐会默认口语化、情绪注入、设问互动、扩写内容或以“绕过检测”为卖点的工具。优先“保信息、保责任、保节点、保风险”的技能。

### 领导汇报场景的推荐框架

- **P0 去腔主编辑**：有 `status` / 商务 / 职场语体，并能锁定数字、日期、责任人、阻塞与下一步。
- **P0/P1 结构工具**：能将信息组织为“当前进度 → 待决事项 → 阻塞/影响 → 下一步”，并按领导偏好调整颗粒度。
- **P1 轻量补丁**：只用于交付前扫除“不是 A 而是 B”“持续推进”“赋能/抓手/闭环”等模板壳，不能替代事实校对。
- **P2 参考而非安装**：泛英文 humanizer、纯禁词表、单 Prompt 项目和声称规避检测的项目。

最终回答至少说明：推荐它解决什么、它不会解决什么、适合哪种材料，以及一条可复用的调用提示。对领导汇报，调用提示应包含：`先给结论；保留数字、节点、责任人和风险；区分已完成/进行中/阻塞/待决策；不新增事实、不弱化问题、不写口号。`

## Multi-Day Historical Aggregation

当用户要求“最近两周 / 过去 N 天 / 一段自定义日期范围的 Top 50”时，不能把当前 Weekly 与 Monthly 页面简单拼接。应读取每日历史快照、跨日去重，并按上榜天数等明确指标聚合。

完整的数据源选择、排序、并列处理、API 补全和口径说明见 `references/multi-day-trending-aggregation.md`。

核心要求：

- 明确日期范围与完整自然日口径；
- 明确榜单是“持续上榜天数榜”还是“Star 增长榜”；
- 第三方归档若只覆盖部分语言，必须披露覆盖范围；
- 并列项目不能仅凭仓库名字母序制造虚假的精确排名；
- GitHub API 返回缺失时写“暂缺”，不要写成 0；
- 当前总 Star 不得表述为窗口新增 Star。

## Fallback Strategy

GitHub Trending 没有官方 API，页面结构可能变。若脚本失败：

1. 用 `web_extract(["https://github.com/trending?..."])` 获取页面内容（约 20 个项目）。
2. 如页面被压缩或解析失败，使用 browser 打开页面检查 DOM。
3. **替代数据源**（按优先级）：
   - **trendshift.io**：第三方聚合，有历史趋势和更长榜单。`web_extract(["https://trendshift.io/github-trending-repositories?since=weekly"])`
   - **ossinsight.io/trending/ai**：AI 专项排名，含 star 增长数据。适合 AI/Agent 方向筛选。
   - **GitHub Search API**：`gh search repos --created=">YYYY-MM-DD" --sort=stars --order=desc --limit=50 --json fullName,stargazersCount,description,primaryLanguage` 可获取指定时间段内的高增长仓库（非 Trending 等价，但覆盖面更广）。
4. 输出时标注数据来源和限制，不要假装精确。明确告知用户"GitHub Trending 页面最多展示约 25 个项目"。

## Pitfalls

1. **脚本超时是常态**：fetch_github_trending.py 在 Hermes VM 上经常 60s 超时（网络慢或 GitHub 限流）。遇到超时不要反复重试，直接 fallback 到 `web_extract(["https://github.com/trending?since=weekly"])`，通常 10-20 秒就能拿到数据。
2. **web_extract 返回的是摘要**：页面超过 5000 字符会被 LLM 截断，可能丢失尾部项目。如需完整 25+ 项目，用 browser 打开页面抓取。
3. **GitHub Trending 页面上限约 25 个项目**：即使脚本设置 `--limit 100`，也只能获取页面实际展示的约 19-25 个项目。这是 GitHub 官方页面的硬限制，不是脚本 bug。用户要求"前50名"时，需明确告知此限制并提供替代方案。
4. **替代数据源补充**：当需要更长榜单时，可用以下来源补充：
   - **trendshift.io**：第三方 GitHub Trending 聚合，有历史趋势数据
   - **ossinsight.io/trending/ai**：AI 专项排名，含增长数据
   - **GitHub Search API**：`gh search repos --created=">日期" --sort=stars` 可获取更长时间范围的高增长仓库
5. **curl 直接抓取 GitHub Trending 页面失败率高**：GitHub 有反爬机制，curl 返回空内容。优先用脚本或 web_extract。

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
