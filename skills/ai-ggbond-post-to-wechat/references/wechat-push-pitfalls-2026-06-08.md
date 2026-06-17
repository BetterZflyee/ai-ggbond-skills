# 微信推送特殊字符与代理问题（2026-06-08 实战）

## 特殊引号问题：「」

**症状**：文章中出现 `「` 和 `」`（日文/繁体中文角引号），在微信公众号编辑器中显示不正常。

**原因**：Markdown 源文件使用了 `「」` 而非标准简体中文引号 `""`。

**修复**：
```bash
sed -i '' 's/「/"/g; s/」/"/g' 文章.md
```

**检查**：
```bash
grep -c '「' 文章.md  # 应为 0
```

**推送前必须检查**：扫描全文是否有 `「」`、`『』`、`【】` 等非标准引号，统一替换为简体中文标准标点。

## 代理配置（Mac Mini 动态 IP 环境）

**微信 API 必须走 tinyproxy 代理**（VPS Tailscale IP）：

```bash
export http_proxy=http://100.117.255.36:8888
export https_proxy=http://100.117.255.36:8888
```

**关键**：
- 微信 API 是中国大陆服务，不要用 Clash 代理（会 ECONNRESET）
- 用 VPS 的 Tailscale 内网 IP，不用公网 IP（hairpin 问题）
- `unset` Clash 代理后再设 tinyproxy

**推送脚本模板**（/tmp/push_wechat.sh）：
```bash
#!/bin/bash
export WECHAT_APP_ID=wx...
export WECHAT_APP_SECRET=...
# Read secret from .env if not hardcoded
# export WECHAT_APP_SECRET=$(grep WECHAT_APP_SECRET ~/.hermes/.env | cut -d'=' -f2)

cd ~/.hermes/profiles/neirong/skills/productivity/ai-ggbond-post-to-wechat/scripts
export http_proxy=http://100.117.255.36:8888
export https_proxy=http://100.117.255.36:8888
npx -y bun wechat-api.ts \
  "/path/to/article.md" \
  --theme default \
  --color blue \
  --title "标题" \
  --summary "摘要" \
  --author "AI朱朱侠" \
  --cover "/path/to/cover.jpg"
```

## ECONNRESET 处理

图片 >1MB 时微信 API 会 ECONNRESET。解法：
- 推送前预压缩图片到 <500KB（quality=75, max_width=1200px）
- 某张图失败不影响其他图，继续推送
- 失败的图在公众号后台手动上传

## 脚本 HOME 路径问题

**症状**：脚本找不到 `~/.ai-ggbond-skills/.env`，实际路径是 `~/.hermes/profiles/neirong/home/.ai-ggbond-skills/.env`

**原因**：Hermes 沙盒环境的 HOME 被重定向。

**解法**：脚本中用硬编码路径读取 .env：
```python
with open('/Users/admin/.hermes/profiles/neirong/skills/creative/ai-ggbond-article-writer/.env') as f:
```
或用 `os.path.expanduser('~')` 检查实际 HOME，再决定 .env 路径。
