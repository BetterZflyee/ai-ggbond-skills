# WeChat API 凭证配置与推送调试（2026-06-07 实战）

## 凭证配置位置
优先级：环境变量 > `~/.hermes/.env` > 技能目录 `.env`

**Hermes VM 环境注意**：`$HOME` 指向 `/Users/admin/.hermes/profiles/neirong/home`，不是 `/Users/admin`。所以 `~/.hermes/.env` 实际路径是 `/Users/admin/.hermes/profiles/neirong/home/.hermes/.env`。

**推荐**：直接用 `export` 设置环境变量，避免路径问题：
```bash
export WECHAT_APP_ID=wx...
export WECHAT_APP_SECRET=...
```

## 推送命令模板
```bash
cd ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts && \
export WECHAT_APP_ID=wx... && \
export WECHAT_APP_SECRET=... && \
unset https_proxy && unset http_proxy && \
npx -y bun wechat-api.ts \
  /path/to/article.html \
  --theme default \
  --color blue \
  --title "标题" \
  --summary "摘要" \
  --author "作者" \
  --cover /path/to/cover.jpg
```

## 关键 pitfall
1. **不要用代理**：微信 API 在国内可直连，代理会导致 ECONNRESET
2. **IP 白名单**：必须将出口 IP 加入白名单，否则报 40164
3. **图片压缩**：正文图必须 <500KB，否则 ECONNRESET
4. **不要杀后台进程**：图片上传是串行的，每张 60-90 秒

## 常见错误码
| 错误码 | 含义 | 解法 |
|--------|------|------|
| 40164 | IP 不在白名单 | 加白名单或配置 Tailscale exit node |
| 45009 | API 调用频次超限 | 等待后重试 |
| ECONNRESET | 图片过大或代理问题 | 压缩图片、去掉代理 |
