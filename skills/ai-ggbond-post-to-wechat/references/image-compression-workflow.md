# 图片压缩工作流（WeChat 推送前）

## 何时需要压缩

文章图片目录中的 PNG 文件通常 2-3MB，微信 API 上传 >1MB 图片会触发 `ECONNRESET`。
**必须在推送前将所有图片压缩到 500KB 以下（推荐 50-100KB）**。

## 自动压缩脚本

当文章目录包含 `images/` 子目录时，运行以下 Python 脚本：

```python
#!/usr/bin/env python3
"""压缩文章图片到 <200KB JPEG，用于微信公众号推送"""
import os, glob
from PIL import Image

image_dir = "/path/to/article/images"  # 文章图片目录
output_dir = "/tmp/compressed_images"   # 压缩后输出目录
MAX_WIDTH = 1200   # 正文图最大宽度（封面用 1600）
QUALITY = 75       # JPEG 质量

os.makedirs(output_dir, exist_ok=True)

for png_file in glob.glob(os.path.join(image_dir, "*.png")):
    img = Image.open(png_file)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    w, h = img.size
    if w > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, int(h * MAX_WIDTH / w)), Image.LANCZOS)
    filename = os.path.basename(png_file).replace('.png', '.jpg')
    output_path = os.path.join(output_dir, filename)
    img.save(output_path, 'JPEG', quality=QUALITY, optimize=True)
    print(f"✅ {filename}: {os.path.getsize(output_path)/1024:.1f} KB")
```

## 完整工作流（文章目录 → 微信推送）

```
文章目录/
├── article.md          # 原始 Markdown
├── images/
│   ├── cover.png       # 封面图
│   ├── 01-xxx.png      # 正文配图
│   └── ...
└── _briefs/            # 需求文档（不推送）
```

**步骤 1：压缩图片**
```bash
python3 /tmp/compress_images.py  # 输出到 /tmp/compressed_images/
```

**步骤 2：创建带图片引用的 Markdown**
在文章适当位置插入图片引用：
```markdown
## 章节标题

![图片说明](/tmp/compressed_images/01-xxx.jpg)

正文内容...
```

⚠️ Markdown 必须包含 `![alt](path)` 语法，否则正文图片全部丢失。

**步骤 3：推送**
```bash
export WECHAT_APP_ID=wx... && export WECHAT_APP_SECRET=完整值
cd ~/.hermes/profiles/touyan/skills/productivity/ai-ggbond-post-to-wechat/scripts
npx -y bun wechat-api.ts /path/to/article-formatted.md \
  --theme default --color blue \
  --title "文章标题" --summary "摘要" --author "作者" \
  --cover /tmp/compressed_images/cover.jpg
```

## 踩坑记录

- PNG 透明背景必须先转 RGB，否则 JPEG 保存报错
- 封面图建议 MAX_WIDTH=1600，正文图 MAX_WIDTH=1200
- quality=75 在手机端阅读完全够用，肉眼不可见差异
- 压缩后文件在 `/tmp/` 目录，重启后丢失，无需清理
