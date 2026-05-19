# 文章写作踩坑记录 / Article Writing Pitfalls

## 1. article_manager.py macOS 不可用（2026-05-16 确认）

**问题**：脚本内部 LOG_FILE 路径硬编码了 Windows 路径 `F:\\AI Workstation\\AI\\Super_OPC\\SuperIp\\Article/`，在 macOS 上报：

```
FileNotFoundError: [Errno 2] No such file or directory: '/Users/admin/.../F:\\AI Workstation\\.../article_manager.log'
```

**解决**：手动创建文件夹结构：

```bash
ARTICLE_DIR="$HOME/Documents/Article/$(date +%Y%m%d%H%M)-文章标题"
mkdir -p "$ARTICLE_DIR/images"
```

**TODO**：修复脚本，使用 `os.path.expanduser` + 相对路径替代硬编码。

## 2. yunwu.ai 生图脚本超时问题（2026-05-16 确认）

**问题**：`generate_images_v4.py` 调用 yunwu.ai 主站时，封面图约46秒成功，但信息图生成在600秒后超时。脚本内置的3节点自动切换（yunwu.ai → api3.wai.vip → api.apiplus.org）不可靠——主站可能挂起不返回，备用节点可能返回空响应。

**解决**：绕过脚本，直接用 Python `requests` 调 API + base64 解码：

```python
import os, json, base64, requests

api_key = "从 ~/.ai-ggbond-skills/.env 读取"

resp = requests.post(
    "https://yunwu.ai/v1/images/generations",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json={"model": "gpt-image-2", "prompt": prompt, "size": "1792x1024", "quality": "standard"},
    timeout=180
)
data = resp.json()
if "data" in data and data["data"]:
    item = data["data"][0]
    if "b64_json" in item:
        img_data = base64.b64decode(item["b64_json"])
        with open("output.png", "wb") as f:
            f.write(img_data)
```

**关键发现**：
- yunwu.ai 主站返回 base64（`b64_json` 字段），不是 URL
- api.apiplus.org 也返回 base64，但偶尔返回空响应
- api3.wai.vip 超时率最高
- 批量生图时，每个请求间隔2秒，避免限流
- 5张图约300秒（5分钟），单张约60秒

## 3. 图片压缩上传微信（已自动处理）

wechat-api.ts 会自动将 >1MB 的 PNG 压缩为 JPEG（quality 82），无需手动处理。本次7张图全部 1.5-1.9MB，自动压缩后上传成功。

## 4. Markdown 图片引用是强制要求

推送到微信公众号时，`wechat-api.ts` 通过扫描 `![alt](path)` 语法检测正文图片。如果 Markdown 中没有图片引用，脚本会报 `Placeholder images: 0`，正文图片全部丢失。

**正确格式**：
```markdown
## 章节标题

![配图说明](images/01-chapter.png)

正文内容...
```

图片必须紧跟在章节标题下方、正文上方。
