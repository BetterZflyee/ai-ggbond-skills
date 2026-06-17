# 完整文章排版推送流程

## 流程概览

```
文章目录/ (含 images/ 子目录)
    ↓
1. 检查文章结构和图片
    ↓
2. 压缩图片到 <500KB
    ↓
3. 创建排版 Markdown（添加图片引用）
    ↓
4. 检查微信凭证
    ↓
5. 检查出口 IP（Tailscale/白名单）
    ↓
6. 执行推送命令
```

## 详细步骤

### Step 1: 检查文章结构

```bash
# 查看目录结构
ls -la /path/to/article/
ls -la /path/to/article/images/

# 查看文章内容
cat /path/to/article/*.md
```

**检查项**：
- 文章是否有 frontmatter（title, author, summary）
- images/ 目录是否存在
- 图片数量和大小（>1MB 需要压缩）

### Step 2: 压缩图片

使用内置脚本：
```bash
python3 ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts/compress_images.py \
  /path/to/article/images \
  /tmp/compressed_images \
  1200 75
```

**参数说明**：
- 参数1：图片源目录
- 参数2：输出目录（默认 /tmp/compressed_images）
- 参数3：最大宽度（默认 1200px，封面图可用 1600px）
- 参数4：JPEG 质量（默认 75，推荐 50-100KB）

### Step 3: 创建排版 Markdown

在文章中添加图片引用：
```markdown
## 章节标题

![图片说明](/tmp/compressed_images/02-timeline.jpg)

正文内容...
```

**飞哥排版偏好**：
- 正文 HTML 不写主标题/副标题（标题/摘要只填微信草稿箱栏）
- 封面图只做草稿封面，不放正文
- 图片放相关小节开头，不显示图注/alt
- 白底黑字高留白+少量点缀
- 引用框只放名言原文/出处
- 段落按语义动作和呼吸断，避免一句一段或文字墙

### Step 4: 检查微信凭证

```bash
# 检查 .env 文件
cat ~/.hermes/.env 2>/dev/null | grep -i wechat

# 检查环境变量
env | grep -i wechat
```

**如果未配置**：
```bash
echo "WECHAT_APP_ID=你的AppID" >> ~/.hermes/.env
echo "WECHAT_APP_SECRET=你的AppSecret" >> ~/.hermes/.env
```

**最可靠方式**（直接 export）：
```bash
export WECHAT_APP_ID=wx... && export WECHAT_APP_SECRET=...
```

### Step 5: 检查出口 IP

```bash
# 必须 unset 代理，否则显示的是代理 IP
unset https_proxy && unset http_proxy && curl -s ifconfig.me
```

**期望输出**：`43.156.151.87`（VPS 固定 IP，已在白名单）

**如果 IP 不对**：
1. 检查 Tailscale 是否开启
2. 在 Tailscale App → Settings → Use exit node 中手动选择 VPS 节点
3. 或者将当前 IP 加入微信公众号白名单

### Step 6: 执行推送

```bash
cd ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts

npx -y bun wechat-api.ts \
  /path/to/article-formatted.md \
  --theme default \
  --color blue \
  --title "文章标题" \
  --summary "摘要（最多128字符）" \
  --author "作者名" \
  --cover /tmp/compressed_images/cover.jpg
```

## 常见问题

### Q: 推送超时怎么办？
**A**: 多图推送耗时公式：每张图 60-90 秒。9 张图 + 封面 ≈ 12-15 分钟。**不要杀进程**，设置 `background=true, notify_on_complete=true` 等待。

### Q: ECONNRESET 错误
**A**: 图片 >1MB 导致。用 compress_images.py 压缩到 <500KB。

### Q: 40164 白名单错误
**A**: 出口 IP 不在白名单。检查 Tailscale 或将当前 IP 加入白名单。

### Q: 图片不显示
**A**: Markdown 必须包含 `![alt](path)` 语法，否则脚本检测不到图片。

### Q: 中文路径问题
**A**: 某些情况下中文路径会导致问题，可以用 `cd` 切换到目录再执行。
