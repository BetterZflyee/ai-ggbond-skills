# 微信公众号 HTML 排版工作流

> 版本：v1.0 | 更新日期：2026-05-11

---

## 标准工作流程

### 步骤 1：用 format_article.py 生成基础 HTML

```bash
cd /Users/admin/.hermes/skills/creative/ai-ggbond-article-writer/scripts
python3 format_article.py \
  -i "文章.md" \
  -o "文章.html" \
  -t "文章标题"
```

**注意**：脚本默认使用绿色主题（#07c160），需要手动改色。

### 步骤 2：修改配色方案

```bash
# 例：改为科技蓝
sed -i '' 's/#07c160/#1E88E5/g' "文章.html"
sed -i '' 's/#333;/#3f3f3f;/g' "文章.html"
```

常用配色方案：

| 内容类型 | PRIMARY | ACCENT | 替换命令 |
|---------|---------|--------|---------|
| 科技/商务 | #1E88E5 | #E3F2FD | `s/#07c160/#1E88E5/g` |
| 生活方式 | #A8DADC | #F1FAEE | `s/#07c160/#A8DADC/g` |
| 励志/能量 | #FF6B35 | #FFF3E0 | `s/#07c160/#FF6B35/g` |
| 教育/知识 | #00897B | #E0F2F1 | `s/#07c160/#00897B/g` |

### 步骤 3：插入配图

format_article.py 不会自动插入图片。需要手动在 HTML 中找到每个章节的 `</blockquote>` 位置，在其后插入图片标签：

```html
<div style="text-align: center; margin: 30px 0;">
<img src="images/FILENAME" alt="ALT" style="max-width: 100%; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
<p style="font-size: 12px; color: #999; text-align: center; margin-top: 10px;">CAPTION</p>
</div>
```

**插入位置规则**：
- 封面图：`</h1>` 之后
- 信息图：第一个 `</blockquote>` 之后
- 章节配图：每个章节最后一个 `</blockquote>` 之后

**Python 批量插入脚本**（推荐）：

```python
import re

with open('文章.html', 'r') as f:
    html = f.read()

def img_tag(fname, caption):
    return f'''<div style="text-align: center; margin: 30px 0;">
<img src="images/{fname}" alt="{caption}" style="max-width: 100%; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
<p style="font-size: 12px; color: #999; text-align: center; margin-top: 10px;">{caption}</p>
</div>
'''

# 插入封面图
html = html.replace('</h1>', '</h1>\n' + img_tag('cover.png', '封面图'), 1)

# 按章节标题关键词匹配插入配图
section_images = [
    ('章节关键词1', '02-xxx.png', '图片说明1'),
    ('章节关键词2', '03-xxx.png', '图片说明2'),
    # ...
]

h2_pattern = re.compile(r'<h2[^>]*>(.*?)</h2>', re.DOTALL)
for m in h2_pattern.finditer(html):
    title = m.group(1)
    for keyword, fname, caption in section_images:
        if keyword in title:
            bq_pos = html.find('</blockquote>', m.end())
            if bq_pos > 0:
                insert_pos = bq_pos + len('</blockquote>') + 1
                html = html[:insert_pos] + '\n' + img_tag(fname, caption) + html[insert_pos:]
            break

with open('文章.html', 'w') as f:
    f.write(html)
```

### 步骤 4：添加页脚

```python
footer = '''
<div style="margin: 30px 0 0 0; padding: 20px; border-top: 1px solid #e0e0e0; text-align: center;">
<p style="margin: 0; font-size: 14px; color: #666;">📌 AI朱朱侠 · 用产品思维理解 AI，用 Harness 思维驾驭 AI</p>
</div>
'''
# 插入到 </div>\n</body> 之前
html = html.replace('    </div>\n</body>', footer + '\n    </div>\n</body>')
```

---

## 本地预览（图片显示问题）

**问题**：HTML 中用相对路径引用图片（`images/xxx.png`），直接双击打开 HTML 文件时浏览器无法加载图片。

**解决方案**：在文章目录启动 HTTP 服务器：

```bash
cd /Users/admin/SuperIp/Article/YYYYMMDDHHMM-文章标题
python3 -m http.server 8765
```

然后浏览器打开 `http://localhost:8765/文章.html`，图片正常显示。

**注意**：HTTP 服务器会在前台运行，需要单独 terminal 窗口。用 `terminal(background=True)` 启动。

---

## Base64 内嵌方案（备选）

如果需要一个独立的 HTML 文件（不依赖外部图片），可以把图片转为 base64 内嵌：

```python
import base64, os

with open('文章.html', 'r') as f:
    html = f.read()

for fname in os.listdir('images'):
    if fname.endswith('.png'):
        with open(f'images/{fname}', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        html = html.replace(f'src="images/{fname}"', f'src="data:image/png;base64,{b64}"')

with open('文章-preview.html', 'w') as f:
    f.write(html)
```

**⚠️ 注意**：11 张图片 base64 后约 30MB，文件很大。仅用于本地预览，不用于发布。

---

## 发布到微信公众号

1. 打开 135 编辑器（135editor.com）
2. 新建文章 → 点"源代码"模式
3. 粘贴 HTML 内容
4. 图片需要单独上传到微信素材库，替换 HTML 中的图片路径为微信 CDN 链接
5. 预览 → 发布

---

## 已知坑

| 坑 | 解决方案 |
|----|---------|
| format_article.py 默认绿色主题 | 用 sed 替换配色 |
| 不自动插入图片 | 用 Python 脚本批量插入 |
| 不自动添加页脚 | 手动添加 |
| 相对路径图片不显示 | HTTP 服务器预览 |
| base64 版本太大（30MB） | 仅用于本地预览 |
| h2 关键词匹配可能不精确 | 检查插入结果，必要时手动调整 |

---

## 更新日志

### 2026-05-11 v1.0
- 初始版本：基于 Harness 文章排版实战经验
