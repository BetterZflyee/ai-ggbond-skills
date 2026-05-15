# AI GGBond Skills

自研 AI 技能集合，用于 Hermes Agent 和日常工作效率提升。

## 📁 仓库结构

```
ai-ggbond-skills/
└── skills/
    ├── ai-ggbond-article-writer/      # 公众号文章写作（配图/排版/风格系统）
    ├── ai-ggbond-post-to-wechat/      # 微信公众号推送（API + CDP 双模式）
    └── ai-ggbond-x-followings-feed/   # X/Twitter 关注列表日报生成器
```

---

## 🛠 技能列表

### 1. ai-ggbond-article-writer

**功能**：AI朱朱侠文章写作技能，从AI Native超级个体视角撰写微信公众号文章。

**核心特点**：
- **个人IP定位**：AI Native超级个体「AI朱朱侠」，OpenClaw布道师、数字化商业落地专家
- **内容方向**：AI产品拆解、场景解决方案、效率提升实战、产品方法论、行业观察
- **写作风格**：第一人称叙述、观点鲜明有理有据、实战导向、个人IP自然融入
- **读者画像**：普通用户/小白用户/AI爱好者（主要），产品经理同行（次要）

**使用场景**：
- 用户说"写一篇关于XXX的文章"
- 用户说"分析一下XXX产品"
- 用户说"聊聊XXX"

**依赖**：baoyu-md（Markdown处理）、云雾 API（图片生成）

**文件结构**：
```
ai-ggbond-article-writer/
├── SKILL.md                    # 主文档（写作规范、风格系统）
├── references/
│   ├── writing-guide.md        # 写作指南
│   └── style-system.md         # 风格系统
└── templates/
    └── article-template.md     # 文章模板
```

---

### 2. ai-ggbond-post-to-wechat

**功能**：推送文章到微信公众号（草稿箱），支持 Markdown/HTML 输入。

**核心特点**：
- **双模式支持**：
  - **API 模式**（推荐）：快速，需要 AppID + AppSecret + IP 白名单
  - **Browser 模式**（备用）：慢速，需要 Chrome + 已登录会话
- **自动图片处理**：扫描 Markdown 中的 `![alt](path)` → 上传到微信素材库 → 替换为 media_id
- **主题样式**：支持自定义主题和样式
- **封面图**：自动提取或指定封面图

**使用场景**：
- 将写好的公众号文章推送到草稿箱
- 批量上传文章配图
- 自动化发布流程

**依赖**：baoyu-md（Markdown处理）、baoyu-chrome-cdp（浏览器自动化）

**文件结构**：
```
ai-ggbond-post-to-wechat/
├── SKILL.md                    # 主文档（使用说明、踩坑记录）
├── scripts/
│   └── post_to_wechat.py       # 推送脚本
└── references/
    └── api-setup.md            # API 配置指南
```

**⚠️ 核心踩坑**：
- Markdown 文件必须包含 `![alt](path)` 图片引用语法，否则正文图片会丢失
- 图片会自动压缩到 <1MB 以满足微信限制

---

### 3. ai-ggbond-x-followings-feed

**功能**：自动抓取 X/Twitter 关注列表的最新推文，生成结构化 AI 日报。

**核心特点**：
- **关注流获取**：使用 `bird home --following` 获取关注博主的推文（不是推荐流）
- **分页机制**：支持多页获取，单次可获取 200+ 条推文
- **AI 分析**：自动分类为重大事件、产品发布、技术洞察、资源汇总、舆情信号等
- **代理支持**：中国大陆用户需配置 HTTPS_PROXY（x.com 被 SNI 封锁）
- **链接格式**：输出裸 URL，飞书等平台自动识别为可点击超链接

**使用场景**：
- 用户说"X日报"、"总结关注列表"、"Twitter摘要"
- 获取过去 1/3/7 天的推文摘要
- 了解 AI 行业最新动态

**依赖**：bird CLI（X/Twitter 命令行工具）、X auth cookies（AUTH_TOKEN & CT0）、HTTPS_PROXY（中国大陆必需）

**文件结构**：
```
ai-ggbond-x-followings-feed/
├── SKILL.md                            # 主文档（配置指南、踩坑记录）
├── scripts/
│   ├── fetch_followings_tweets.sh      # Shell 脚本（基础版）
│   └── fetch_x_following_paginated.py  # Python 脚本（分页版，推荐）
└── references/
    ├── analyst_prompt_template.md      # AI 分析师提示词模板
    ├── x-api-pitfalls.md               # X API 踩坑记录
    ├── x-graphql-api.md                # X GraphQL API 文档
    ├── proxy-setup.md                  # 代理配置指南
    ├── market-context.md               # 市场背景
    └── pitfalls.md                     # 通用踩坑记录
```

**⚠️ 核心踩坑**：
1. `bird home` 获取的是 "For You" 推荐流，必须加 `--following` 参数才能获取关注流
2. bird CLI 不支持代理，中国大陆必须使用 Python 脚本
3. Following 流的用户数据在 `.core` 不是 `.legacy`，需兼容两种结构
4. 链接不要用反引号包裹，否则在飞书不会渲染为超链接

**配置步骤**：
1. 从浏览器提取 X 的 `auth_token` 和 `ct0` cookie
2. 配置代理（中国大陆）：`export HTTPS_PROXY=http://127.0.0.1:7897`
3. 运行 Python 脚本获取推文
4. 使用 AI 分析师模板生成日报

---

## 🚀 使用方式

技能通过 Hermes Agent 加载使用：

```bash
# 在 Hermes 中调用
skill_view("ai-ggbond-x-followings-feed")
skill_view("ai-ggbond-post-to-wechat")
skill_view("ai-ggbond-article-writer")
```

### 快速上手

1. **写文章**：告诉 AI 朱朱侠你想写什么主题
2. **推送到微信**：写完后说"推送到公众号"
3. **获取 X 日报**：说"X日报"或"总结关注列表"

---

## 📌 许可

MIT-0

---

## 📝 更新日志

### 2026-05-15
- **ai-ggbond-x-followings-feed**：修复关注流获取问题
  - 修复：`bird home` → `bird home --following`
  - 修复：用户数据从 `.core` 读取（Following 流数据结构不同）
  - 新增：分页机制，支持多页获取（42条→270条）
  - 修复：链接格式改为裸 URL，飞书自动识别超链接
  - 新增：HTTPS_PROXY 代理配置说明
