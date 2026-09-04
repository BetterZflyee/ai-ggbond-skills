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
    "https://api.openlux.ai/v1/images/generations",
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

## 5. 平行案例陷阱（2026-05-27 飞哥纠正）

**问题**：多案例文章写成"ClickUp 一节 → SO 一节 → 合规一节"各自独立，读起来像新闻摘要堆砌。"读起来比较松散，没有主线"。

**根因**：每个案例独立成节，彼此没有递进关系，读者不知道它们在共同论证什么。

**正确做法**：所有案例必须服务一条递进论证链：
```
现象 → 机制 → 权力转移 → 冷思考 → 行动 → 升华
```

每个案例只出现一次，只服务一个递进论点。案例之间用过渡句串联，让读者感受到"同一件事的下一层"。

## 6. 冷思考与行动顺序陷阱（2026-05-27 飞哥纠正）

**问题**：把"行动建议"放在"冷思考/边界"之前 → 读者看完行动建议后看到边界警告，产生焦虑。

**飞哥原话**："冷静边界 → 你的三个行动 → 判断力是唯一护城河"

**正确顺序**：先踩刹车（去幻想、认知边界）→ 再给行动建议（基于清醒认知）→ 最后升华。过渡句："我先把边界讲清楚，不是为了吓你。恰恰相反——正因为知道边界在哪，行动起来才不盲目。"

## 7. 配图文字过多陷阱（2026-05-27 飞哥纠正）

**飞哥原话**："图形可以再多一点，文字少一点"

**原则**：信息图/章节配图应 **85% 图形 + 15% 文字**。用图标、箭头、前后对比图、视觉隐喻讲故事。文字退到短标签和微标注。图片应做到"不看正文也能理解核心概念"。禁止信息图做成密集文字墙。
