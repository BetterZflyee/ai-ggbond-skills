# AI GGBond Skills · 飞哥 AI 技能库

> **为 AI Native 超级个体打造的 Hermes Agent 技能集合。**
> 覆盖内容创作、社交媒体运营、知识管理、趋势洞察的全链路 AI 工作流。
> 即插即用，每个技能沉淀了真实场景的实战经验与迭代优化。

> **A curated collection of Hermes Agent skills for the AI Native solopreneur.**
> End-to-end AI workflows covering content creation, social media ops, knowledge management, and trend intelligence.
> Plug-and-play — each skill is battle-tested and iteratively refined from real-world usage.

---

## 技能矩阵 / Skill Matrix

| 技能 / Skill | 分类 / Category | 一句话 / TL;DR |
|:---|:---|:---|
| `ai-ggbond-article-writer` | 创作 / Creative | 公众号长文写作，AI Native 视角，排版→配图→发布全流程 |
| `ai-ggbond-post-to-wechat` | 效率 / Productivity | 一键推送文章到微信公众号草稿箱，API + Browser 双模式 |
| `ai-ggbond-sticker-writer` | 创作 / Creative | 内容转小红书风微信贴图，总结→标题→排版→配图 |
| `ai-ggbond-github-trending` | 研究 / Research | GitHub Trending 检索解读，AI/Agent/MCP 趋势洞察 |
| `ai-ggbond-x-followings-feed` | 社媒 / Social | X/Twitter 关注流抓取 + AI 结构化日报 |
| `ai-ggbond-publish-to-x` | 社媒 / Social | 发布到 X/Twitter，支持短帖、引用、长文、Thread |
| `ai-ggbond-run-xiaohongshu` | 社媒 / Social | 小红书全链路运营，定位→选题→生产→发布→复盘 |
| `ai-ggbond-brain-setup` | 知识 / Knowledge | GBrain 记忆层安装配置，让 AI 拥有长期记忆 |

---

## 系统架构 / Architecture

```
┌─────────────────────────────────────────────────┐
│                   Hermes Agent                    │
│         (AI 朱朱侠 · PMO 指挥决策中枢)              │
└────────┬──────────┬──────────┬──────────────────┘
         │          │          │
    ┌────▼────┐ ┌───▼───┐ ┌───▼────┐
    │ 创作流水线 │ │社媒矩阵 │ │知识引擎 │
    │ Creative │ │ Social │ │Knowledge│
    └────┬─────┘ └───┬───┘ └───┬─────┘
         │            │          │
  ┌──────┼──────┐  ┌──┼───┐     │
  ▼      ▼      ▼  ▼  ▼   ▼     ▼
文章   贴图   GitHub X  小红书  GBrain
写作   转换   Trending 发布  运营   记忆层
  │      │              │
  └──────┴──────────────┘
         │
    ┌────▼────┐
    │ 微信草稿箱 │
    │ WeChat   │
    └─────────┘
```

**设计哲学 / Design Philosophy**

每个技能不是孤立工具，而是可组合的工作流节点：
- `ai-ggbond-x-followings-feed` 抓取信号 → `ai-ggbond-article-writer` 生成文章 → `ai-ggbond-post-to-wechat` 发布
- `ai-ggbond-x-followings-feed` 抓取信号 → `ai-ggbond-publish-to-x` 发推评论
- `ai-ggbond-github-trending` 发现项目 → `ai-ggbond-article-writer` 选题创作

---

## 快速开始 / Quick Start

### 前置条件 / Prerequisites

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) 已安装并运行
- 各技能的前置依赖（见各技能 SKILL.md）

### 安装 / Installation

```bash
# 克隆到 Hermes 技能目录
git clone https://github.com/BetterZflyee/ai-ggbond-skills.git /tmp/ai-ggbond-skills

# 安装全部技能
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* ~/.hermes/skills/

# 或按需安装单个技能
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-article-writer ~/.hermes/skills/creative/
```

### 触发使用 / Trigger

在 Hermes 对话中自然语言触发：

| 你说 / You Say | 触发技能 / Triggers |
|:---|:---|
| "写一篇关于 AI Agent 的文章" | `ai-ggbond-article-writer` |
| "发到微信公众号" | `ai-ggbond-post-to-wechat` |
| "把这个转成贴图" | `ai-ggbond-sticker-writer` |
| "看看 GitHub Trending" | `ai-ggbond-github-trending` |
| "X 日报" / "总结关注列表" | `ai-ggbond-x-followings-feed` |
| "发推" / "tweet" | `ai-ggbond-publish-to-x` |
| "帮我运营小红书" | `ai-ggbond-run-xiaohongshu` |
| "配置 brain / gbrain" | `ai-ggbond-brain-setup` |

---

## 技能详情 / Skill Details

### ai-ggbond-article-writer

公众号长文写作，从 AI Native 超级个体视角输出。支持：
- 选题判断 → 大纲 → 初稿 → 排版 → 配图 → 发布 全流水线
- Anthropic 暖米白 + Tech Blue v3 双排版主题
- 信息图生成（课程表隐喻、陶土橙/鼠尾草绿配色）
- 图片 OCR 质检、金句断点、引用框规范

### ai-ggbond-post-to-wechat

推送文章到微信公众号草稿箱：
- **API 模式**（推荐）：AppID + AppSecret，快速可靠
- **Browser CDP 模式**（备用）：直连 Chrome，绕过 API 敏感词拦截
- 自动图片上传（正文内联 + 封面图）、主题样式注入
- Tailscale 出口 IP 适配（国内网络环境）

### ai-ggbond-sticker-writer

内容转微信贴图（小红书风格）：
- 输入文章/要点 → 自动总结提炼 → 标题生成 → Markdown 排版 → 配图生成
- 支持知识卡片、清单体、对比图等多种贴图样式

### ai-ggbond-github-trending

GitHub Trending 趋势洞察：
- 支持 daily/weekly/monthly 时间窗
- AI/Agent/MCP/LLM 领域关键词过滤
- P0/P1/P2 优先级自动分级
- 输出 Markdown 报告 + 选题建议

### ai-ggbond-x-followings-feed

X/Twitter 关注流 AI 日报：
- 获取关注列表推文（非推荐算法流）
- 单次 200+ 条，支持 1/3/7 天时间窗
- AI 自动分类：重大事件、产品发布、技术洞察、资源汇总、舆情信号
- 内置评分策展 (curate_and_score.py)

### ai-ggbond-publish-to-x

X/Twitter 全功能发布：
- 短帖（文字 + 图片 + 视频）
- 引用转发、长文（X Articles / Markdown）
- 帖子串（Thread）
- 对接 article-writer 和 followings-feed 形成闭环

### ai-ggbond-run-xiaohongshu

小红书全链路运营：
- 自动读取 Hermes Memory 适配用户定位
- 选题研究 → 内容生产 → 发布执行 → 评论回复 → 爆款复刻 → 复盘沉淀
- CDP 浏览器适配（绕过反爬）

### ai-ggbond-brain-setup

GBrain 记忆层集成：
- 在 Hermes 环境下安装配置 GBrain
- PGLite 本地向量存储
- 桥接 signal-detector / brain-ops / conventions 等上游技能
- 知识库内容灌入工作流

---

## 贡献与迭代 / Contributing

本仓库为个人自用技能库，持续迭代中。每个技能的 `references/` 目录沉淀了真实会话中的经验教训和踩坑记录。

技能更新流程：
```
实战使用 → 发现问题 → 更新 SKILL.md + references/ → 同步 GitHub
```

---

## 许可 / License

[MIT-0](LICENSE) · 无任何限制，自由使用、修改、分发。
