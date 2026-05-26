# AI GGBond Skills · 专注让 AI 成为你的<br>自动化搞钱和IP运营系统

<p align="center">
  <a href="https://github.com/BetterZflyee/ai-ggbond-skills/stargazers"><img src="https://img.shields.io/github/stars/BetterZflyee/ai-ggbond-skills?style=for-the-badge&color=facc15" alt="Stars"></a>
  <a href="https://github.com/BetterZflyee/ai-ggbond-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"></a>
  <a href="https://zflyee.com/"><img src="https://img.shields.io/badge/built%20by-AI%20朱朱侠-8b5cf6?style=for-the-badge" alt="AI 朱朱侠"></a>
  <a href="#changelog"><img src="https://img.shields.io/badge/version-1.0-0891b2?style=for-the-badge" alt="Version"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/English-📖-2563eb?style=for-the-badge" alt="English"></a>
</p>

> **为 AI Native 超级个体&OPC打造的 Agent Skills 技能集合。**
>
> 每个技能都是一个完整的自动化工作流——不是聊天玩具，是能发文章、能运营社媒、能抓趋势、能沉淀知识的 AI 劳动力。即插即用，持续迭代，所有经验教训沉淀在 `references/` 目录中。

---

## 为什么选择 AI GGBond Skills

本技能库运行在 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 之上——Hermes 是目前唯一具备**内建学习闭环**的 AI Agent：自动从经验中创建技能、使用中自我改进、跨会话持久记忆。AI GGBond Skills 则更进一步——不满足于"聊天"，直接面向**搞钱和 IP 运营**场景提供端到端自动化。

你可以自由选择底层模型——OpenAI、DeepSeek、OpenRouter 200+ 模型、Nous Portal、或是你自己的部署——模型随你换，技能不用改。

---

## 技能矩阵

| 技能 | 分类 | 核心能力 |
|:---|:---|:---|
| `ai-ggbond-article-writer` | 📝 创作 | 公众号长文全流水线：选题→大纲→初稿→排版→配图→发布 |
| `ai-ggbond-post-to-wechat` | 🚀 发布 | 一键推送微信公众号草稿箱，API + Browser CDP 双模式 |
| `ai-ggbond-sticker-writer` | 🎨 创作 | 内容转小红书风微信贴图，自动总结→排版→配图 |
| `ai-ggbond-github-trending` | 🔍 研究 | GitHub Trending 抓取+AI 解读，AI/Agent/MCP 趋势洞察 |
| `ai-ggbond-x-followings-feed` | 📡 信号 | X/Twitter 关注流抓取 + AI 结构化日报 + 策展评分 |
| `ai-ggbond-publish-to-x` | 📢 社媒 | X/Twitter 全功能发布：短帖、引用、长文、Thread |
| `ai-ggbond-run-xiaohongshu` | 📕 社媒 | 小红书全链路运营：定位→选题→生产→发布→评论→复盘 |
| `ai-ggbond-brain-setup` | 🧠 知识 | GBrain 记忆层集成：让 AI 拥有长期记忆和知识检索 |

> 所有技能均支持 **"千人千面"用户适配**（v1.0 里程碑）——自动读取 Hermes Memory 中的用户画像，输出贴合你个人风格的内容，而不是千篇一律的 AI 味。

---

## 系统架构

```
┌──────────────────────────────────────────────────┐
│                  Hermes Agent                      │
│          (AI 朱朱侠 · PMO 指挥决策中枢)              │
│                                                    │
│  记忆层 ←→ GBrain (ai-ggbond-brain-setup)          │
└──────┬────────────┬─────────────┬─────────────────┘
       │            │             │
  ┌────▼─────┐ ┌───▼────┐ ┌─────▼──────┐
  │ 内容生产   │ │信号采集 │ │ 多渠道发布   │
  │ Creative  │ │ Signal  │ │ Distribution │
  └────┬─────┘ └───┬────┘ └─────┬──────┘
       │            │             │
  ┌────┼─────┐      │      ┌─────┼──────┐
  ▼    ▼     ▼      ▼      ▼     ▼      ▼
文章  贴图  GitHub   X      微信   X     小红书
写作  转换  Trending 关注流  公众号  发布   运营
       │            │             │
       └────────────┴─────────────┘
                    │
              用户画像适配层
           (Hermes Memory 千人千面)
```

**设计哲学：可组合的工作流**

每个技能不是孤岛——它们是可串联的流水线节点：

```
X 关注流日报 ──→ 选题灵感 ──→ 文章写作 ──→ 微信发布
       │                          │
       └────→ X 发推评论 ←────────┘

GitHub Trending ──→ 选题灵感 ──→ 文章写作 ──→ 微信发布
```

---

## 快速安装

### 前置条件

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) 已安装并运行
- macOS / Linux / WSL2（技能均通过命令行操作，对操作系统无特殊要求）

### 一键安装全部技能

```bash
# 克隆仓库
git clone https://github.com/BetterZflyee/ai-ggbond-skills.git /tmp/ai-ggbond-skills

# 安装所有技能到 Hermes
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-* ~/.hermes/skills/

# 验证安装
hermes skills list | grep ai-ggbond
```

### 按需安装单个技能

```bash
# 示例：只安装文章写作技能
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-article-writer ~/.hermes/skills/creative/
```

### 更新技能

```bash
cd /tmp/ai-ggbond-skills && git pull
cp -r skills/ai-ggbond-* ~/.hermes/skills/
```

---

## 使用指南

### 自然语言触发（推荐）

在 Hermes 对话中直接说话即可触发对应技能：

| 你对 AI 朱朱侠说 | 自动触发 |
|:---|:---|
| "写一篇关于 AI Agent 的文章" | `ai-ggbond-article-writer` |
| "发到微信公众号" | `ai-ggbond-post-to-wechat` |
| "把这个转成贴图" | `ai-ggbond-sticker-writer` |
| "看看 GitHub Trending 今天有什么" | `ai-ggbond-github-trending` |
| "X 日报" / "总结关注列表" | `ai-ggbond-x-followings-feed` |
| "发推" / "publish to X" | `ai-ggbond-publish-to-x` |
| "帮我运营小红书" | `ai-ggbond-run-xiaohongshu` |
| "配置 brain" / "灌内容到 gbrain" | `ai-ggbond-brain-setup` |

### CLI 命令参考

```bash
# 查看已安装的全部技能
hermes skills list

# 只看 AI GGBond 系列
hermes skills list | grep ai-ggbond

# 查看某个技能的详细文档
hermes skills view ai-ggbond-article-writer

# 更新 Hermes Agent 本体
hermes update

# 诊断问题
hermes doctor
```

---

## 技能详览

### ai-ggbond-article-writer

公众号长文写作全流水线。从 AI Native 超级个体视角输出内容。

**能力**：选题判断 → 大纲框架 → 正文初稿 → 语义节奏排版 → AI 配图 → 推送到微信草稿箱

**特色**：
- Anthropic 暖米白 + Tech Blue v3 双排版主题
- 信息图自动生成（课程表隐喻、陶土橙 / 鼠尾草绿配色）
- 图片 OCR 质检、金句断点、引用框规范
- 支持"千人千面"用户适配——根据你的定位自动调整文风和深度

### ai-ggbond-post-to-wechat

将文章推送到微信公众号草稿箱。

**双模式**：
- **API 模式**（推荐）：AppID + AppSecret，快速可靠
- **Browser CDP 模式**（备用）：直连 Chrome 扫码登录，绕过敏感词拦截

**自动处理**：正文图片上传、封面图提取、HTML 样式注入、Tailscale 出口 IP 适配

### ai-ggbond-sticker-writer

将文章或要点转换为微信贴图（小红书风格）。

**流程**：输入内容 → 自动总结提炼 → 标题生成 → Markdown 排版 → AI 配图生成

**样式**：知识卡片、清单体、对比图、步骤图、观点卡

### ai-ggbond-github-trending

GitHub Trending 趋势发现与解读。

**能力**：daily / weekly / monthly 时间窗 · AI / Agent / MCP / LLM 领域过滤 · P0 / P1 / P2 优先级自动分级 · Markdown 报告 + 选题建议输出

### ai-ggbond-x-followings-feed

X/Twitter 关注流 AI 日报。

**能力**：获取关注列表推文（非推荐算法流）· 单次 200+ 条 · 1 / 3 / 7 天时间窗 · AI 自动分类（重大事件 / 产品发布 / 技术洞察 / 资源汇总 / 舆情信号）· 内置 `curate_and_score.py` 策展评分引擎

### ai-ggbond-publish-to-x

X/Twitter 全功能发布客户端。

**能力**：短帖（文字 + 图片 + 视频）· 引用转发 · 长文（X Articles / Markdown）· 帖子串（Thread）· 对接 article-writer 和 followings-feed 形成内容闭环

### ai-ggbond-run-xiaohongshu

小红书全链路运营。

**能力**：自动读取 Hermes Memory 适配用户定位 → 选题研究 → 内容生产 → 发布执行 → 评论回复 → 爆款复刻 → 复盘沉淀 · CDP 浏览器适配

### ai-ggbond-brain-setup

GBrain 记忆层集成——让 AI 拥有长期记忆。

**能力**：PGLite 本地向量存储 · 桥接 signal-detector / brain-ops / conventions 等上游技能 · 知识库内容灌入工作流

---

## 集成生态

### 依赖关系

```
ai-ggbond-brain-setup (记忆底座)
        ↓
Hermes Memory (用户画像)
        ↓
┌───────┼──────────┬──────────────┐
↓       ↓          ↓              ↓
article  sticker   xiaohongshu   github
writer   writer    ops           trending
   ↓       ↓          ↓
post-to   publish    (内置发布)
-wechat   -to-x
```

### 技能间串联示例

| 工作流 | 技能链 |
|:---|:---|
| 日常信号→文章→发布 | `x-followings-feed` → `article-writer` → `post-to-wechat` |
| 热点快评→X 推文 | `x-followings-feed` → `publish-to-x` |
| 开源项目→选题创作 | `github-trending` → `article-writer` → `post-to-wechat` |
| 知识沉淀→长期记忆 | `article-writer` 产出 → `brain-setup` 灌入 GBrain |

---

## 迁移指南

### 从 ai-ggbond-push-to-x 迁移到 ai-ggbond-publish-to-x

`ai-ggbond-push-to-x` 已于 2026 年 5 月 26 日废弃，请使用 `ai-ggbond-publish-to-x`：

```bash
# 1. 删除旧技能
rm -rf ~/.hermes/skills/ai-ggbond-push-to-x

# 2. 安装新技能
cp -r /tmp/ai-ggbond-skills/skills/ai-ggbond-publish-to-x ~/.hermes/skills/social-media/

# 3. 验证
hermes skills list | grep publish-to-x
```

**变化**：新技能 API 向后兼容旧的触发词（"发推""tweet""publish to X"），无需修改使用习惯。新增支持 X Articles 长文 Markdown 发布和 Thread 帖子串。

---

## 更新日志

| 日期 | 里程碑 |
|:---|:---|
| 2026-05-26 | 📦 `ai-ggbond-brain-setup` 上线 · `push-to-x` 废弃，`publish-to-x` 替代 |
| 2026-05-20 | 🔍 `ai-ggbond-github-trending` 上线 · 全部技能达成"千人千面"用户适配 v1.0 |
| 2026-04-20 | 🏗️ 仓库创建，技能体系正式工程化 |
| 2026-02-28 | ✍️ `ai-ggbond-article-writer` 首个技能上线，完成第一篇端到端自动发布 |

---

## 贡献

本仓库为 AI Native 超级个体的实战技能库。每个技能的 `references/` 目录沉淀了真实会话中的踩坑记录和迭代经验——这是本仓库最有价值的部分。

**迭代流程**：实战使用 → 发现问题 → 更新 SKILL.md + references/ → 同步 GitHub

欢迎提 Issue 讨论使用场景，或 Fork 后定制你自己的技能变体。

---

## 关注

<p align="center">
  <table>
    <tr align="center">
      <td><b>微信公众号</b></td>
      <td><b>X / Twitter</b></td>
      <td><b>个人博客</b></td>
    </tr>
    <tr align="center">
      <td><img src="assets/wechat-qr.jpg" width="140" alt="AI 朱朱侠 公众号"></td>
      <td><a href="https://x.com/Zflyee">𝕏 · @Zflyee</a></td>
      <td><a href="https://zflyee.com/">🌐 · zflyee.com</a></td>
    </tr>
  </table>
</p>

---

## 许可

[MIT](LICENSE) · 无任何限制。自由使用、修改、分发。Build in public.
