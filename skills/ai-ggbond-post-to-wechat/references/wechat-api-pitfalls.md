# ai-ggbond-post-to-wechat 踩坑记录

> 版本：v2.0 | 更新日期：2026-05-15

---

## 问题 1：正文图片全部丢失（封面图正常）

### 症状

推送成功，但公众号草稿里**只有封面图，正文没有图片**。脚本日志显示：

```
Placeholder images: 0
```

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

### 正确流程

```
生成文章 → 确认 images/ 目录有图 → 在 Markdown 中插入 ![alt](images/xxx.png) → 推送
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
# 1. 激活 exit node
tailscale up --exit-node=<vps-tailscale-ip> --accept-routes

# 2. 验证出口 IP
curl -s ifconfig.me
# 应显示 VPS 的固定 IP（如 159.75.220.145）

# 3. 推送
cd ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts
npx -y bun wechat-api.ts /path/to/article.md ...

# 4. 用完关闭 exit node
tailscale up --exit-node=
```

### 注意

- 每次推送前都要 `curl -s ifconfig.me` 确认出口 IP
- 如果 VPS 重启了，Tailscale exit node 可能需要重新配置
- 微信公众号 IP 白名单最多 5 个 IP

---

## 问题 3：文件路径参数格式

### 症状

`bun run wechat-api.ts --markdown article.md` 报错：`Error: File path required`

### 原因

文件路径是**第一个位置参数**，不是 `--markdown` flag。

```bash
# ✅ 正确
npx -y bun wechat-api.ts article.md --theme default --title "标题"

# ❌ 错误
npx -y bun wechat-api.ts --markdown article.md
```

---

## 问题 4：图片格式/大小问题

### 症状

上传失败或图片显示异常。

### 解决方案

脚本内置了自动处理：
- **格式转换**：WebP/BMP/TIFF → PNG/JPEG（自动）
- **大小压缩**：超过 1MB 自动压缩（先降质量，再缩尺寸）
- **透明度处理**：PNG 透明背景自动叠加白色背景

如果自动处理失败，手动预处理：

```bash
# macOS 用 sips 转换格式
sips -s format png image.webp --out image.png

# 或者用 ImageMagick
convert image.webp image.png
```

---

## 问题 5：Tailscale exit node 不生效

### 症状

`tailscale up --exit-node=<ip>` 后 `curl ifconfig.me` 仍然显示本地 IP。

### 解决方案

```bash
# 检查 exit node 状态
tailscale exit-node list

# 重新设置（注意格式）
tailscale up --exit-node=100.xxx.xxx.xxx --accept-routes

# 如果仍然不生效，检查 DNS
nslookup ifconfig.me

# 或者用其他方式验证
curl -s https://api.ipify.org
```

---

## 问题 6：推送成功但公众号后台看不到

### 原因

API 模式推送到的是**草稿箱**，不是直接发布。

### 解决方案

1. 登录公众号后台 → 内容管理 → 草稿箱
2. 找到刚推送的文章
3. 预览 → 确认图片和排版 → 发布

---

## 问题 7：封面图不显示

### 症状

推送成功，封面图位置是空白。

### 原因

封面图必须通过 `--cover` 参数单独指定，且必须是本地文件路径或可访问的 URL。

```bash
# ✅ 正确：本地封面图
npx -y bun wechat-api.ts article.md --cover images/cover.png

# ❌ 错误：没有指定封面图
npx -y bun wechat-api.ts article.md
```

---

## 问题 8：newspic 类型推送报错 45166（invalid content hint）

### 症状

```json
{"errcode": 45166, "errmsg": "invalid content hint: [SEdl8a083105-0]"}
```

使用 `--type newspic` 推送贴图时，API 模式报错。图片上传成功（cover media_id 正常返回），但最终发布失败。

### 根因

微信 API 对 `newspic`（贴图/图文）类型的内容校验比普通文章更严格，某些内容或格式会触发 `invalid content hint`。具体触发条件不完全明确，但与以下因素相关：
- 内容涉及敏感话题（国际政治等）
- 文本长度或格式不符合 newspic 类型要求
- 图片数量与内容比例不匹配

### 解决方案

**降级到 Browser 模式**（`wechat-browser.ts`），它直接操作公众号后台编辑器，不受 API 内容校验限制：

```bash
cd ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts

npx -y bun wechat-browser.ts \
  --markdown /path/to/article.md \
  --images /path/to/images/ \
  --submit
```

### Browser 模式注意事项

1. **需要扫码登录**：脚本会打开 Chrome，提示用微信扫码登录公众号
2. **标题自动压缩**：超过 20 字符会被截断
3. **内容自动压缩**：超过 1000 字符会被截断
4. **图片上限 9 张**：微信贴图限制
5. **Chrome 需要关闭再开**：如果之前有 Chrome 实例，先 `pkill -f "Google Chrome"` 再运行
6. **Chrome debug port 连接失败**：如果报 `Chrome debug port not ready`，先关闭所有 Chrome 进程再重试

### 判断用哪种模式

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| 普通文章（news） | API 模式 | 快速、不需要浏览器 |
| 贴图（newspic）+ 无敏感内容 | API 模式 | 可能成功 |
| 贴图（newspic）+ 45166 报错 | Browser 模式 | 绕过 API 校验 |
| 贴图（newspic）+ 敏感话题 | Browser 模式 | 最可靠 |
