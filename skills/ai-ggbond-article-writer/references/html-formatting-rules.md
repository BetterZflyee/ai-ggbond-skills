# HTML 精排版铁律（2026-06-07 补充）

## 问题背景

飞哥公众号文章推送时，发现以下问题：
1. Markdown `**加粗**` 语法未转换为 HTML，原样显示在公众号
2. 章节标题排版差，没有使用模板的编号样式
3. 金句没有独立样式，和普通加粗一样
4. 标点符号错误（`「」`搞反）

## 铁律

### 1. Markdown 必须全部转 HTML

公众号平台**不会**自动转换 Markdown 语法。`**加粗**` 会原样显示。

**验证脚本**：
```python
import re
with open('file.html', 'r') as f:
    content = f.read()
md_bold = re.findall(r'\*\*[^*]+\*\*', content)
assert len(md_bold) == 0, f"发现 {len(md_bold)} 处未转换的 Markdown"
```

### 2. 金句必须有独立卡片样式

金句 ≠ 普通加粗。金句用独立卡片：
```html
<div style="margin: 25px 0; padding: 20px; background: #f8f8f8; border-left: 4px solid #1a1a1a; text-align: center;">
  <p style="font-size: 16px; font-weight: bold; color: #1a1a1a; margin: 0; line-height: 1.6;">
    金句内容
  </p>
</div>
```

关键概念只用 `<strong>` 即可，不要都做成金句卡片。

### 3. 章节标题使用模板编号样式

参考 `assets/base-template.html`：
```html
<div style="margin: 40px 0 10px 0;">
  <span style="display: inline-block; font-size: 18px; font-weight: bold; color: #1E88E5; padding: 5px 15px; border-left: 4px solid #1E88E5;">
    01.
  </span>
</div>
<h2 style="font-size: 17px; font-weight: bold; color: #1a1a1a; margin: 15px 0;">
  章节标题
</h2>
```

### 4. 标点符号必须正确

- 中文引号：`「」`（不是`""`）
- `「` 是左引号，`」` 是右引号，不能搞反
- 引用块用 `>` 语法，转为 `<blockquote>` 样式

### 5. 使用 base-template.html

生成 HTML 时**必须参考** `assets/base-template.html`，不要自己写模板。模板包含：
- 章节编号样式
- 引用块样式
- 金句卡片样式
- 图片居中样式
- 底部行动号召样式
