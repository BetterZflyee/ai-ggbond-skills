# ai-ggbond-post-to-wechat 踩坑记录

> 版本：v2.0 | 更新日期：2026-05-11

---

## 问题 1：正文图片全部丢失（封面图正常）

### 症状

推送成功，但公众号草稿里**只有封面图，正文没有图片**。脚本日志显示：`Placeholder images: 0`

### 根因

**Markdown 文件里没有 `![alt](path)` 图片引用语法。**

API 模式的图片检测机制是扫描 `![alt](path)` 语法 → 生成占位符 → 上传图片。如果 Markdown 里没有这种语法，脚本完全不知道有图片要上传。

### 常见触发场景

1. 用 `ai-ggbond-article-writer` 生成文章后，图片是手动添加的，没有写入 Markdown
2. 用 HTML 文件推送，但 HTML 里的 `<img>` 标签是本地路径（未上传到可访问的 URL）
3. 图片放在 `images/` 目录但 Markdown 里没有引用

### 解决方案

**推送前必须确认 Markdown 文件中包含图片引用：**

```markdown
## 第一章 标题

正文内容...

![配图说明](images/02-chapter-name.png)
```

### 检查命令

```bash
# 检查 Markdown 中有多少图片引用
grep -c '!\[' /path/to/article.md

# 列出所有图片引用
grep -n '!\[' /path/to/article.md

# 对比 images/ 目录中的文件和 Markdown 中的引用
ls images/*.png | while read f; do
  basename=$(basename "$f")
  if ! grep -q "$basename" article.md; then
    echo "❌ 未引用: $f"
  fi
done
```

---

## 问题 2：IP 白名单限制（错误码 40164）

### 症状

```json
{"errcode": 40164, "errmsg": "invalid ip xxx.xxx.xxx.xxx, not in whitelist"}
```

### 解决方案

**动态 IP 环境 → Tailscale exit node 走固定 IP VPS：**

```bash
# 激活 exit node
tailscale up --exit-node=<vps-tailscale-ip> --accept-routes

# 验证出口 IP
curl -s ifconfig.me  # 应显示 VPS 的固定 IP

# 推送完成后关闭
tailscale up --exit-node=
```

---

## 问题 3：文件路径参数格式

文件路径是**第一个位置参数**，不是 `--markdown` flag。

```bash
# ✅ 正确
npx -y bun wechat-api.ts article.md --theme default --title "标题"

# ❌ 错误
npx -y bun wechat-api.ts --markdown article.md
```

---

## 问题 4：图片格式/大小问题

脚本内置自动处理：
- **格式转换**：WebP/BMP/TIFF → PNG/JPEG（自动）
- **大小压缩**：超过 1MB 自动压缩（先降质量，再缩尺寸）
- **透明度处理**：PNG 透明背景自动叠加白色背景

---

## 问题 5：推送成功但公众号后台看不到

API 模式推送到的是**草稿箱**，不是直接发布。需要在公众号后台 → 内容管理 → 草稿箱中找到并发布。

---

## 问题 6：封面图不显示

封面图必须通过 `--cover` 参数单独指定：

```bash
npx -y bun wechat-api.ts article.md --cover images/cover.png
```

---

## 问题 7：Tailscale exit node 不生效

```bash
# 检查 exit node 状态
tailscale exit-node list

# 重新设置
tailscale up --exit-node=100.xxx.xxx.xxx --accept-routes

# 验证
curl -s https://api.ipify.org
```
