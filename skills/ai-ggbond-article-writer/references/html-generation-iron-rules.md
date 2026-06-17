# HTML 生成铁律（2026-06-07 实战补充）

## 必须使用模板，禁止手写 HTML

生成公众号 HTML 时，**必须**使用 `assets/base-template.html` 模板结构，禁止自己从零写 HTML。

模板包含：
- 章节编号样式（`01.` `02.` 带蓝色左边框）
- 引用块样式（淡蓝背景 + 蓝色左边框）
- 金句卡片样式（灰底 + 黑色左边框）
- 图片居中圆角样式

**错误示范**：自己写简单的 `<p>` + `<h2>` 模板 → 排版效果差，缺乏层次感

**正确做法**：读取 `assets/base-template.html`，按模板结构生成 HTML

## Markdown 语法必须全部转换

推送到公众号前，HTML 文件中**不得残留任何 Markdown 语法**：

- `**加粗**` → `<strong>加粗</strong>` 或直接去掉标记
- `[链接](url)` → `<a href="url">链接</a>`
- `![alt](src)` → `<img src="src" alt="alt">`

**验证命令**：
```bash
python3 -c "
import re
with open('article.html', 'r') as f:
    content = f.read()
md_bold = re.findall(r'\*\*[^*]+\*\*', content)
print(f'残留 Markdown: {len(md_bold)} 处')
"
```

## 引号修正

Markdown 中的 `「」` 需要转换为标准中文引号 `""`，不能出现 `「` 和 `」` 混用的情况。

## 金句卡片设计

金句需要**视觉上与普通文本区分**，使用独立卡片样式：

```html
<div style="margin: 25px 0; padding: 20px; background: #f8f8f8; border-left: 4px solid #1a1a1a; text-align: center;">
  <p style="font-size: 16px; font-weight: bold; color: #1a1a1a; margin: 0; line-height: 1.6;">
    金句内容
  </p>
</div>
```

**不要**：通篇都是 `<strong>` 加粗，没有视觉层次
**要**：金句用卡片样式，普通强调用 `<strong>`，引用用 blockquote
