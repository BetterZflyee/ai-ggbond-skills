# 微信公众号发布工作流

## 发布链路

```
Markdown 文章 → ai-ggbond-article-writer (写作+配图)
                ↓
             ai-ggbond-post-to-wechat (推送)
                ↓
             Tailscale → VPS 固定 IP → 微信 API
                ↓
             微信公众号草稿箱
```

## 前置条件

1. Markdown 文件中必须包含 `![alt](path)` 图片引用（不是 HTML `<img>` 标签）
2. 封面图单独指定（`--cover` 参数）
3. 微信 API 凭证已配置在 `~/.ai-ggbond-skills/.env`
4. Tailscale 出口节点已连接（验证：`curl -s ifconfig.me` 应显示 VPS IP）

## 完整命令

```bash
cd ~/.hermes/skills/ai-ggbond-post-to-wechat/scripts

bun run wechat-api.ts \
  /path/to/article.md \
  --theme default \
  --color blue \
  --title "文章标题" \
  --summary "120字以内摘要" \
  --author "AI朱朱侠" \
  --cover /path/to/images/cover.png
```

## ⚠️ 关键注意事项

1. **图片必须在 Markdown 中用 `![alt](path)` 引用**，否则 API 模式检测不到（Placeholder images: 0）
2. **文件路径是第一个位置参数**，不是 flag
3. 图片会自动压缩到 1MB 以内（JPEG 82 quality）
4. 推送成功后去公众号草稿箱预览确认

## 配图规范（已写入 SKILL.md）

- 元数据行（约 xxxx 字 · 建议阅读 x 分钟）：居中、10px、#999、后缀 `· 点击右上角🎧可听阅`
- 标签行（#Harness ...）：居中、10px、#999
- 封面图：2.35:1 或 16:9
- 信息图：16:9 横版
- 章节配图：16:9 横版，每章节 1 张

## 排版脚本

```bash
cd ~/.hermes/skills/creative/ai-ggbond-article-writer/scripts

python3 format_article.py \
  -i article.md \
  -o article.html \
  -t "文章标题"
```

注意：format_article.py 生成的 HTML 是通用模板，配色和图片需要手动调整。
