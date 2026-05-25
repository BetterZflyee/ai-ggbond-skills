# 2026-05-21 HTML 精排版推送成功案例

## 场景

文章：`《我越来越确定：AI 工具的下一站，不是更聪明，而是接管工作流》`

文章目录：
`/Users/admin/SuperIp/article/202605211305-AI编程正在从Copilot进入Agent接管时代/`

用户要求：严格按公众号排版偏好做 HTML 精排，并推送到微信公众号草稿箱。

## 成功流程

1. 先用 article-writer 侧生成自定义 HTML 精排版，不依赖 `wechat-api.ts --theme` 做视觉排版。
2. HTML 使用相对图片路径：
   - `images/infographic.png`
   - `images/02-tool-vs-platform.png`
   - `images/03-copilot-vs-agent.png`
   - `images/04-agent-runtime-architecture.png`
   - `images/05-control-and-quota.png`
   - `images/06-workflow-assets.png`
3. 封面图通过 `--cover images/cover.png` 单独上传。
4. 推送前执行洁净度预检：不得包含 `建议阅读`、`点击右上角`、`全文核心信息图`、`配图：`、`图片说明`、`<figcaption`、`金句断点`。
5. 检查 HTML 图片路径存在，使用 Python 正则统计 `<img\b` 而不是误写成 `<img\\b`。
6. 检查出口 IP：`curl -s --max-time 10 ifconfig.me`，本次返回 `43.156.151.87`。
7. 先 dry-run，再正式推送。

## 关键命令

```bash
cd /Users/admin/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts

npx -y bun wechat-api.ts '/path/to/article-公众号精排版.html' \
  --title '我越来越确定：AI 工具的下一站，不是更聪明，而是接管工作流' \
  --summary '从 Gemini CLI 迁移到 Antigravity CLI，看懂 AI 编程工具真正的转折点。' \
  --author 'AI朱朱侠' \
  --cover '/path/to/images/cover.png' \
  --dry-run

# dry-run 成功后去掉 --dry-run 正式推送
```

## 成功信号

HTML dry-run：

```json
{
  "articleType": "news",
  "htmlPath": "...公众号精排版.html",
  "contentLength": 25851
}
```

正式推送：

```json
{
  "success": true,
  "media_id": "...",
  "title": "我越来越确定：AI 工具的下一站，不是更聪明，而是接管工作流",
  "articleType": "news"
}
```

## 注意事项

- HTML 文件路径可以带中文，但 terminal `workdir` 仍建议设为 `/tmp`，命令内部用引号包裹绝对路径。
- HTML 模式下脚本能识别 `<img src="images/xxx.png">` 并上传正文图片；不需要 Markdown 的 `![alt](...)`。
- 正文图片会被脚本压缩并转 JPEG，日志里出现 `encoded as JPEG (82 quality)` 属正常。
- 推送成功后提醒用户去公众号后台手机端预览，重点看段落节奏与微信压缩后图片小字清晰度。
