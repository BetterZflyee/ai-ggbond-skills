---
name: ai-ggbond-post-to-wechat
description: "推送文章到微信公众号（草稿箱）。支持 Markdown/HTML 输入，自动图片上传（正文内联 + 封面），主题样式，API 模式（推荐）和 Chrome CDP 模式（备用）。"
version: "2.0.0"
author: "AI GGBond"
license: MIT
metadata:
  hermes:
    tags: [wechat, publishing, article, draft, api, feishu]
---

# 推送到微信公众号 (aiggbond-post-to-wechat)

## 概述

将文章推送到微信公众号草稿箱。支持两种方式：

**边界提醒**：本技能的 `--theme default/grace/simple/modern` 只提供基础 Markdown 转微信 HTML 样式和图片上传，不等于专业公众号精排版器。若用户反馈“排版累、需要金句断点、不要每句换行、要高留白/HTML精排”，应先用文章写作技能生成自定义 HTML 预览版，确认后再用本技能推送 HTML 文件；不要靠反复切换 theme 解决精排问题。


| 方式 | 速度 | 要求 | 适用场景 |
|------|------|------|----------|
| **API 模式**（推荐） | 快 | AppID + AppSecret + IP 白名单 | 日常推送 |
| **Browser 模式**（备用） | 慢 | Chrome + 已登录会话 | IP 未白名单或无 API 凭证 |

## 核心机制：图片处理流程

**⚠️ newspic（贴图）类型注意**：API 模式推送贴图时可能触发 45166 错误（内容校验失败），涉及敏感话题时概率更高。此时降级到 Browser 模式（`wechat-browser.ts`）。详见 `references/wechat-api-pitfalls.md` 问题 8。

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

**⚠️ 关键：Markdown 文件必须包含图片引用！**

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

1. ✅ Markdown 文件中每张图片都有 `![alt](images/xxx.png)` 引用；HTML 文件中 `<img src="images/xxx.png">` 相对路径存在
2. ✅ 图片路径是相对于文章文件的相对路径
3. ✅ 图片文件实际存在且非空
4. ✅ 封面图通过 `--cover` 参数单独指定
5. ✅ Tailscale exit node 已激活（动态 IP 环境）
6. ✅ `curl -s ifconfig.me` 返回的是白名单 IP
7. ✅ 飞哥公众号发布前必须做正文洁净度预检：不得出现 `建议阅读`、`点击右上角`、`全文核心信息图`、`配图：`、`图片说明`、`figcaption` 等可见模板/图注痕迹；详见 `references/wechat-clean-publish-preflight.md`

### ⚠️ 文章查找位置提醒

文章写作技能在 `article_manager.py` 失败时会将文件保存到 `/tmp/article-{主题}/` 而非标准目录。如果在标准 `Article/` 目录下找不到文章，**检查 `/tmp/`**：

```bash
ls /tmp/article-*/
```

## 快速使用

```bash
cd ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts

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

存储在 `~/.hermes/.env`：

```
WECHAT_APP_ID=wx...
WECHAT_APP_SECRET=...
```

检测顺序：
1. 环境变量 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`
2. `~/.hermes/.env`（推荐，统一配置）

## ⚠️ IP 白名单问题

微信 API 要求调用方 IP 在公众号的 IP 白名单中。如果机器是**动态公网 IP**，用 **Tailscale exit node** 走固定 IP VPS：

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

### 检查 Tailscale 状态

```bash
tailscale status          # 查看节点列表
tailscale exit-node list  # 查看可用 exit node
curl -s ifconfig.me       # 验证当前出口 IP
```

### ⚠️ Tailscale 必须手动开启（Mac Mini 环境）

Tailscale CLI 在本机**未安装**（`command not found`），用户通过 **Tailscale 桌面 App** 手动开启。

**推送前强制检查流程**：
1. 告诉用户"请打开 Tailscale"
2. 等待用户确认
3. 执行 `curl -s ifconfig.me` 验证出口 IP 为 `159.75.220.145`
4. IP 确认无误后再执行推送命令

**常见失败场景**：
- Tailscale 未开启 → 出口 IP 为本机动态 IP（如 `172.216.245.31`、`163.125.130.62`）→ 40164 白名单错误
- Tailscale 开启但 exit node 未生效 → 返回 IPv6 地址（如 `2408:8256:...`）→ 同样白名单错误
- VPN 软件冲突 → 可能导致出口 IP 在 VPN IP 和 Tailscale IP 之间跳动

**正确的出口 IP**：`159.75.220.145`（VPS 固定 IP，已加入微信公众号白名单）

## 主题选项

主题：`default`, `grace`, `simple`, `modern`

颜色预设：`blue`, `green`, `vermilion`, `yellow`, `purple`, `sky`, `rose`, `olive`, `black`, `gray`, `pink`, `red`, `orange`（或 hex 色值）

## 完整参数

```
npx -y bun wechat-api.ts <file> [options]

参数：
  file                Markdown (.md) 或 HTML (.html) 文件

选项：
  --type <type>       文章类型：news（文章，默认）或 newspic（图文）
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

## Frontmatter 字段（Markdown）

```yaml
---
title: 文章标题
author: 作者名
license: MIT
---
```

## 环境检查

```bash
cd ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts
npx -y bun check-permissions.ts
```

检查项：Chrome、Bun、API 凭证、剪贴板等。

## 脚本列表

| 脚本 | 用途 |
|------|------|
| `wechat-api.ts` | API 模式推送（快速，推荐） |
| `wechat-article.ts` | Browser 模式推送（慢，备用） |
| `wechat-browser.ts` | 图文帖（贴图发表） |
| `md-to-wechat.ts` | Markdown → 微信 HTML |
| `check-permissions.ts` | 环境检查 |
| `wechat-image-processor.ts` | 图片压缩/格式转换 |

## 参考文档

| 文件 | 内容 |
|------|------|
| `references/api-setup.md` | 凭证配置指南 |
| `references/article-posting.md` | 文章推送流程 |
| `references/image-text-posting.md` | 图文帖参数 |
| `references/multi-account.md` | 多账号支持 |
| `references/wechat-api-setup.md` | Tailscale + IP 白名单配置 |
| `references/wechat-api-pitfalls.md` | API 踩坑记录 |
| `references/session-2026-05-19-ai-tools-article-push.md` | 《AI工具的下半场》12图长文成功推送案例：dry-run、Tailscale IP 验证、中文路径 workdir 坑 |
| `references/wechat-clean-publish-preflight.md` | 飞哥公众号发布前正文洁净度预检：拦截阅读元信息、图片图注、alt 可见化、卡片堆叠等问题 |

## 贴图发表（图文帖）注意事项

### API 模式 vs Browser 模式

| 模式 | 贴图支持 | 已知问题 |
|------|---------|---------|
| **API 模式**（wechat-api.ts --type newspic） | 理论支持 | ❌ 2026-05-15 实测报错 `45166: invalid content hint`，可能与内容敏感词有关 |
| **Browser 模式**（wechat-browser.ts） | ✅ 实测可用 | 需要扫码登录，上传速度较慢 |

**推荐**：贴图类型优先使用 Browser 模式。

### Browser 模式贴图流程
1. Chrome 会自动打开并检测登录状态
2. 如未登录，提示用户扫码（公众号管理员微信）
3. 自动点击"贴图"菜单
4. 批量上传图片（所有 PNG/JPG，按文件名排序）
5. 自动填充标题（最多20字，超出自动压缩）和内容（最多1000字）
6. 点击"保存为草稿"

### 关键踩坑
- **Markdown 必须包含图片引用** `![alt](images/xxx.png)`，否则正文图片丢失
- **图片按文件名排序上传**，命名建议：`01-封面.png`、`02-内容.png`...
- **Tailscale 必须开启**，出口 IP 必须为 `159.75.220.145`
- **Chrome profile** 路径：`/Users/admin/Library/Application Support/baoyu-skills/chrome-profile`

## 与 ai-ggbond-article-writer 配合使用

典型工作流：

1. 用 `ai-ggbond-article-writer` 生成文章 Markdown + 配图
2. 如果飞哥要求“HTML 精排版/读起来舒服/金句断点”，先在文章写作技能中完成语义节奏排版和本地 HTML 预览；`ai-ggbond-post-to-wechat` 只负责发布转换，不要把它当精细排版设计器
3. 确认 Markdown 中包含 `![alt](images/xxx.png)` 图片引用；如果输入是 HTML，确认 `<img src="images/xxx.png">` 本地相对路径存在
4. 用 `ai-ggbond-post-to-wechat` 推送到公众号草稿箱
5. 在公众号后台预览、调整、发布
