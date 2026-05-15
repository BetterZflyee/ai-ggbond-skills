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

## 🛠 技能列表

| 技能 | 说明 | 依赖 |
|------|------|------|
| **ai-ggbond-article-writer** | 公众号文章写作，支持配图、排版、多风格 | baoyu-md, 云雾 API |
| **ai-ggbond-post-to-wechat** | 推送到微信公众号草稿箱（API/CDP） | baoyu-md, baoyu-chrome-cdp |
| **ai-ggbond-x-followings-feed** | X/Twitter 关注列表日报生成 | bird CLI, X auth cookies |

## 🚀 使用方式

技能通过 Hermes Agent 加载使用：

```bash
# 在 Hermes 中调用
skill_view("ai-ggbond-x-followings-feed")
skill_view("ai-ggbond-post-to-wechat")
```

## 📌 许可

MIT-0
