# Feishu Message Formatting Guide

## Core Rule

Feishu Markdown rendering is LIMITED. Always format output for Feishu compatibility when the user is on Feishu.

## Supported Syntax

- **Bold**: `**text**`
- *Italic*: `*text*`
- ~~Strikethrough~~: `~~text~~`
- Links: `[text](url)`
- Lists: `- item` or `1. item`
- Code blocks: ` ```language\ncode\n``` `
- Dividers: `---` (needs blank line before/after)
- Emoji: ✅ Supported — 🔥⭐→✅❌ all render correctly
- `<font color='red'>` color tags

## NOT Supported

- **Tables**: `|---|---|` renders as plain text. **Use code blocks instead.**

## Table Replacement Pattern

Instead of:
```
| Project | Value | Growth | Verdict |
|---|---|---|---|
| headroom | Token compression | +14K/wk | P0 |
```

Use:
````
```
项目            核心价值                  增长          判断
headroom        Token 压缩 60-95%        +14,272/周    P0，Agent 省钱刚需
hermes-agent    你的主控 Agent            +11,427/周    P0，核心工具
```
````

## Emoji Usage

Emoji works fine in Feishu. Use for visual hierarchy:
- 🔥 for hot/trending
- 🏆 for top tier
- 📊 for data sections
- 🎯 for action items
- ✅ for verified/available
- ⚠️ for warnings
- ❌ for failures/unavailable

## Section Dividers

Use `---` with blank lines around it:

```
## Section Title

Content here.

---

## Next Section

More content.
```
