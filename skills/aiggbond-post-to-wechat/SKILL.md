---
name: aiggbond-post-to-wechat
description: "推送文章到微信公众号（草稿箱）。支持 Markdown/HTML 输入，自动图片上传（正文内联 + 封面），主题样式，API 模式（推荐）和 Chrome CDP 模式（备用）。基于 baoyu-post-to-wechat 迭代，修复了图片处理、路径配置等关键问题。"
---

# 推送到微信公众号 (aiggbond-post-to-wechat)

## 概述

将文章推送到微信公众号草稿箱。两种方式：

| 方式 | 速度 | 要求 | 适用场景 |
|------|------|------|----------|
| **API 模式**（推荐） | 快 | AppID + AppSecret + IP 白名单 | 日常推送 |
| **Browser 模式**（备用） | 慢 | Chrome + 已登录会话 | IP 未白名单或无 API 凭证 |

## 🔴 核心机制：图片处理流程

**这是最容易踩坑的地方，务必理解。**

API 模式的工作原理：

```
Markdown 文件 (含 ![alt](path) 图片引用)
    ↓
1. 扫描所有 ![alt](path) → 替换为 WECHATIMGPH_N 占位符
2. Markdown → HTML（含占位符）
3. 每张图片上传到微信素材库（自动压缩到 <1MB）
4. 占位符替换为微信 media_id URL
5. 整体推送到草稿箱
```

### ⚠️ 关键：Markdown 文件必须包含图片引用！

如果 Markdown 文件里**没有** `![alt](path)` 语法，脚本会报 `Placeholder images: 0`，**正文图片全部丢失**，只剩封面图。

**❌ 错误**（图片不会被检测到）：
```markdown
## 第一章
一些文字...
```

**✅ 正确**（图片会被上传）：
```markdown
## 第一章
一些文字...

![配图说明](images/01-chapter.png)
```

### 推送前必须检查清单

1. ✅ Markdown 文件中每张图片都有 `![alt](images/xxx.png)` 引用
2. ✅ 图片路径是相对于 Markdown 文件的相对路径
3. ✅ 图片文件实际存在且非空
4. ✅ 封面图通过 `--cover` 参数单独指定
5. ✅ Tailscale exit node 已激活（动态 IP 环境）
6. ✅ `curl -s ifconfig.me` 返回的是白名单 IP

## 快速使用

```bash
cd ~/.ai-ggbond-skills/aiggbond-post-to-wechat/scripts

npx -y bun wechat-api.ts \
  /path/to/article.md \
  --theme default \
  --color blue \
  --title "文章标题" \
  --summary "摘要" \
  --author "作者名" \
  --cover /path/to/cover.png
```

**注意**：文件路径是第一个位置参数（不是 flag）。

## 凭证配置

存储在 `~/.ai-ggbond-skills/.env`：

```
WECHAT_APP_ID=wx...
WECHAT_APP_SECRET=...
```

检测顺序：
1. 环境变量 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`
2. `<cwd>/.ai-ggbond-skills/.env`
3. `~/.ai-ggbond-skills/.env`

## ⚠️ IP 白名单问题（动态 IP → Tailscale exit node）

```
Mac Mini (动态 IP) → Tailscale → VPS (固定 IP 159.75.220.145) → 微信 API
```

### Tailscale 配置步骤

1. Mac Mini 和 VPS 都安装 Tailscale
2. VPS 端：`sudo tailscale up --advertise-exit-node`
3. 在 https://login.tailscale.com/admin/machines 审批 exit node
4. Mac Mini 端：`tailscale up --exit-node=<vps-tailscale-ip> --accept-routes`
5. 将 VPS 的固定公网 IP 加入微信公众号 IP 白名单
6. 验证：`curl -s ifconfig.me` 应显示 VPS 的 IP

### 推送时操作

```bash
# 激活 exit node
tailscale up --exit-node=100.xxx.xxx.xxx --accept-routes

# 验证出口 IP
curl -s ifconfig.me  # 应显示 159.75.220.145

# 推送
cd ~/.ai-ggbond-skills/aiggbond-post-to-wechat/scripts
npx -y bun wechat-api.ts /path/to/article.md --cover images/cover.png

# 用完关闭
tailscale up --exit-node=
```

## 主题选项

主题：`default`, `grace`, `simple`, `modern`

颜色预设：`blue`, `green`, `vermilion`, `yellow`, `purple`, `sky`, `rose`, `olive`, `black`, `gray`, `pink`, `red`, `orange`（或 hex 色值）

## 完整参数

```
npx -y bun wechat-api.ts <file> [options]

参数：
  file                Markdown (.md) 或 HTML (.html) 文件

选项：
  --type <type>       news（文章，默认）或 newspic（图文）
  --title <title>     覆盖标题
  --author <name>     作者名（最多 16 字符）
  --summary <text>    摘要（最多 128 字符）
  --theme <name>      主题（default, grace, simple, modern）
  --color <name|hex>  主色调
  --cover <path>      封面图路径（本地或 URL）
  --account <alias>   多账号时选择账号
  --no-cite           禁用底部引用链接
  --dry-run           只解析渲染，不推送
  --help              帮助
```

## 脚本列表

| 脚本 | 用途 |
|------|------|
| `wechat-api.ts` | API 模式推送（快速，推荐） |
| `wechat-article.ts` | Browser 模式推送（慢，备用） |
| `wechat-browser.ts` | 图文帖（贴图发表） |
| `md-to-wechat.ts` | Markdown → 微信 HTML |
| `check-permissions.ts` | 环境检查 |
| `wechat-image-processor.ts` | 图片压缩/格式转换 |
| `preflight.ts` | 推送前预检（图片引用、文件存在、Tailscale 状态） |

## 与 ai-ggbond-article-writer 配合

典型工作流：

1. 用 `ai-ggbond-article-writer` 生成文章 Markdown + 配图
2. **🔴 确认 Markdown 中包含 `![alt](images/xxx.png)` 图片引用**
3. 用 `aiggbond-post-to-wechat` 推送到公众号草稿箱
4. 在公众号后台预览、调整、发布

## 已知踩坑

详见技能安装目录下的 `references/wechat-api-pitfalls.md`，包含 7 个已知问题及解决方案。

关键踩坑：
- **正文图片丢失**：Markdown 中没有 `![alt](path)` 引用
- **IP 白名单 40164**：动态 IP 需要 Tailscale exit node
- **文件路径格式**：文件是第一个位置参数，不是 `--markdown` flag
