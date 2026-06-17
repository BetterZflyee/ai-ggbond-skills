# gpt-image-2 中文渲染终极方案（2026-06-08 实战验证）

## 核心发现

**英文 prompt + 指定中文输出** > 中文 prompt。

## 之前失败的方案

| 方案 | 结果 | 原因 |
|------|------|------|
| 中文 prompt 大段描述 | 乱码/自由发挥 | 模型对中文 prompt 结构理解差 |
| 简化中文（只留标题） | 太简单，用户不满意 | 信息密度不够 |
| 全英文标注 | 用户拒绝 | "除了专业词语，其他不能用英文" |
| 代码绘图（matplotlib） | 用户禁止 | "效果非常差，明令禁止" |
| Pillow 后贴文字 | 用户拒绝 | "文字和图分离，很丑" |
| HTML/CSS + Playwright | 用户拒绝 | "非常差劲，根本不好用" |

## 最终成功方案

**英文 prompt 结构化描述 + 明确要求中文输出**：

```
Create a 16:9 tech infographic, dark background #0A1628, neon blue #00D4FF accents.
Title: "中文标题" in large glowing text at top.
6 information cards in a grid layout:
Card 1: "中文标签" — "中文描述文字"
Card 2: "中文标签" — "中文描述文字"...
Bottom bar: "安装命令" in elegant terminal box.
All text MUST be in Simplified Chinese (简体中文), clear and legible. No watermark.
```

**关键技巧**：
1. prompt 主体用英文写，结构清晰
2. 中文内容用引号包裹，嵌入英文 prompt 中
3. 末尾强调 "All text MUST be in Simplified Chinese"
4. 不要用中文写长段描述性 prompt

## 女性角色信息图

详见 sticker-writer 的 `references/gpt-image2-chinese-and-female-characters.md`。
