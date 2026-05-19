# 2026-05-19《AI工具的下半场》公众号推送经验

## 场景

文章目录：`/Users/admin/SuperIp/article/202605191946-AI工具的下半场/`

正文 Markdown：`202605191946-AI工具的下半场.md`

配图目录：`images/`，共 12 张 PNG，正文中均使用 `![alt](images/xxx.png)` 引用。

## 成功流程

1. 先执行 dry-run，确认 Markdown 排版和正文图片占位符数量：

```bash
cd /Users/admin/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts
npx -y bun wechat-api.ts '/Users/admin/SuperIp/article/202605191946-AI工具的下半场/202605191946-AI工具的下半场.md' \
  --theme modern \
  --color blue \
  --title 'AI工具的下半场：不是谁更会聊天，而是谁能真正下场干活' \
  --summary 'AI工具正在从聊天窗口进入执行系统。下半场拼的不是谁更会说，而是谁能接入流程、安全执行、沉淀资产。' \
  --author 'AI朱朱侠' \
  --cover '/Users/admin/SuperIp/article/202605191946-AI工具的下半场/images/00-infographic.png' \
  --dry-run
```

关键成功信号：

```text
Placeholder images: 12
contentLength: 79796
placeholderImageCount: 12
```

2. 检查出口 IP：

```bash
curl -s --max-time 12 ifconfig.me && printf '\n'
```

如果返回 IPv6 或非 `159.75.220.145`，不要正式推送。让用户在 Mac Mini 上打开 Tailscale 并启用 exit node，再重试。

3. IP 返回 `159.75.220.145` 后，去掉 `--dry-run` 正式推送。

成功信号：

```json
{
  "success": true,
  "media_id": "...",
  "title": "AI工具的下半场：不是谁更会聊天，而是谁能真正下场干活",
  "articleType": "news"
}
```

## 重要坑位

- Hermes terminal 的 `workdir` 如果包含中文字符可能被拦截，例如路径中有 `AI工具的下半场` 会报：`Blocked: workdir contains disallowed character '工'`。解决：`workdir` 设为 `/tmp`，命令内部对实际文件路径使用引号包裹的绝对路径。
- dry-run 不需要正确 IP，但正式推送前必须验证 IP。
- 正文图上传时脚本会自动压缩到微信要求大小，日志里出现 `encoded as JPEG (82 quality)` 属正常现象。
- 公众号长文建议发布前提醒用户手机端预览：封面裁切、正文图完整性、长文密度。