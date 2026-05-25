---
name: ai-ggbond-publish-to-x
description: 发布内容到 X (Twitter)。支持短帖(文字+图片+视频)、引用转发、长文(X Articles/Markdown)、帖子串(Thread)。对接 ai-ggbond-article-writer 和 ai-ggbond-x-followings-feed。当用户说"发到X""发推""tweet""publish to X"时触发。
version: 2.0.0
metadata:
  openclaw:
    homepage: https://github.com/BetterZflyee/ai-ggbond-skills#ai-ggbond-publish-to-x
    requires:
      anyBins:
        - bun
        - npx
---

# AI朱朱侠 — Publish to X

将内容策略化发布到 X（原 Twitter），支持短帖、图片、视频、引用转发、长文和帖子串。

设计原则：发布不是"推一条"——发布是分发策略的终点。每条内容都应服务于飞哥的 AI Native 超级个体定位。

---

## 脚本目录

**重要**：所有脚本位于本 skill 的 `scripts/` 子目录。

**执行指令**：
1. 确定本 SKILL.md 所在目录为 `{baseDir}`
2. 脚本路径 = `{baseDir}/scripts/<script-name>.ts`
3. 本文档中所有 `{baseDir}` 替换为实际路径
4. `${BUN_X}` 解析：`bun` 已安装 → `bun`；否则 → `npx -y bun`

**脚本速查**：

| 脚本 | 用途 |
|------|------|
| `scripts/x-browser.ts` | 短帖（文字+图片），CDP 后备 |
| `scripts/x-video.ts` | 视频帖，CDP 后备 |
| `scripts/x-quote.ts` | 引用转发，CDP 后备 |
| `scripts/x-article.ts` | 长文发布（Markdown），CDP 后备 |
| `scripts/md-to-html.ts` | Markdown → HTML 转换 |
| `scripts/copy-to-clipboard.ts` | 内容复制到剪贴板 |
| `scripts/paste-from-clipboard.ts` | 真实粘贴按键 |
| `scripts/check-paste-permissions.ts` | 环境与权限验证 |

---

## 执行模式选择（必须二选一）

1. **Hermes Browser 模式**（首选）：使用 Hermes 的 `browser_*` 工具操控真实 Chrome，复用用户已登录的 X 会话。
2. **CDP 脚本模式**（后备）：Browser 模式不可用时，通过 CDP 直连 Chrome，脚本自动填充内容。

两种模式都**打开浏览器让用户审核**，绝不自动点击发布按钮（除非用户明确说"直接发"）。

---

## 发布前策略检查

在发布任何内容之前，快速过一遍：

1. **这条内容服务于什么定位？** → AI Native 超级个体 = 实用干货 + 犀利观点 + 工具/方法论
2. **什么时间发？** → 飞哥时区 (UTC+8) 的 8:00-9:00、12:00-13:00、20:00-22:00 是 X 中文圈活跃窗口
3. **和什么联动？** → 公众号文章 → X 发摘要+链接；X 发现 → 公众号深度展开
4. **是首次发布还是二次分发？** → 公众号首发后，X 24h 内做摘要分发

---

## Hermes Browser 模式（首选）

使用 Hermes 内置 `browser_navigate` / `browser_click` / `browser_type` / `browser_snapshot` 工具操控 Chrome。

**通用规则**：
- 始终先 `browser_navigate` 到目标页面
- 用 `browser_snapshot` 获取页面元素 ref ID
- 用元素 ref 点击，坐标点击仅作后备
- **绝不**在用户确认前点击 `Post` / `Publish` / `发帖`
- 若页面是中文 X 界面，选择器用中文文本匹配

**短帖发布**：
1. `browser_navigate` → `https://x.com/compose/post`
2. `browser_snapshot` → 找到发帖框
3. `browser_type` → 输入文字
4. 如有图片，用脚本复制到剪贴板：
   ```bash
   ${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts image /absolute/path/to/img.png
   ```
5. `browser_press key="Meta+v"`（macOS）或 `Control+v`（其他）
6. 等待上传完成 → 请用户确认 → 点发布

**引用转发**：
1. `browser_navigate` → 目标推文 URL
2. `browser_snapshot` → 找到引用/转发按钮
3. 输入评论 → 确认 → 发布

**X 长文 (Articles)**：
1. 先把 Markdown 转 HTML：
   ```bash
   ${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/x-article-body.html > /tmp/x-article.json
   ```
2. 读 JSON 拿 `title`、`coverImage`、`contentImages`
3. `browser_navigate` → `https://x.com/compose/articles`
4. 上传封面、填标题
5. 复制富文本 HTML 到剪贴板：
   ```bash
   ${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts html --file /tmp/x-article-body.html
   ```
6. `browser_press key="Meta+v"` 粘贴到文章正文
7. 逐个替换 `XIMGPH_N` 占位符 → Insert → Media → 上传图片
8. 预览 → 确认 → 发布

---

## CDP 脚本模式（后备）

Browser 模式不可用时使用。脚本自动启动 Chrome + CDP，填充内容后浏览器保持打开供审核。

### 短帖

```bash
${BUN_X} {baseDir}/scripts/x-browser.ts "推文内容" --image ./img.png
```

| 参数 | 说明 |
|------|------|
| `<text>` | 推文内容（位置参数） |
| `--image <path>` | 图片文件（可重复，最多4张） |
| `--profile <dir>` | 自定义 Chrome profile 目录 |

### 视频帖

```bash
${BUN_X} {baseDir}/scripts/x-video.ts "看看这个！" --video ./clip.mp4
```

### 引用转发

```bash
${BUN_X} {baseDir}/scripts/x-quote.ts https://x.com/user/status/123 "精彩！"
```

### X 长文 (Articles)

```bash
${BUN_X} {baseDir}/scripts/x-article.ts article.md
${BUN_X} {baseDir}/scripts/x-article.ts article.md --cover ./cover.jpg
```

Markdown 支持 YAML frontmatter：
```yaml
---
title: 文章标题
cover_image: /path/to/cover.jpg
---
```

---

## 帖子串 (Thread) 支持

当内容超过 280 字符时，自动拆分为帖子串（1/N 格式）。

**拆分规则**：
- 按句号/段落自然断点拆分
- 每条 ≤ 280 字符
- 自动添加 `1/N` `2/N` 标记
- 第一条包含核心观点/钩子
- 最后一条包含 CTA 或链接

**实现方式**：
1. AI 先手动拆分内容为 N 条
2. 第一条用短帖发布
3. 后续每条作为回复追加到前一条

---

## 发布内容类型决策树

```
用户给的内容是什么？
├─ 短文本（≤280字符）
│  └─ 直接发短帖（Browser 模式首选）
├─ 短文本 + 图片
│  └─ 短帖 + 图片粘贴（Browser 模式首选）
├─ 长文本（>280字符，<5000字符）
│  └─ 帖子串（Thread）拆分
├─ Markdown 文件（.md）
│  ├─ 飞哥有 X Premium → X Article
│  └─ 没有 → 拆 Thread 或摘要 + 链接
├─ 公众号文章链接
│  └─ 写摘要推文（2-3 条 Thread）+ 链接
└─ 视频文件
   └─ 视频帖（Browser 模式首选）
```

---

## 飞哥环境注意事项

### 网络
- 飞哥用 **Tailscale 出口节点** `43.156.151.87` 推 X
- 如果 Chrome 不走代理，检查 Clash 端口 `7897` 是否正常
- X API 直连可用，但浏览器访问建议走代理

### macOS 剪贴板权限
- 首次使用需授予终端 **辅助功能(Accessibility)** 权限：
  「系统设置 → 隐私与安全性 → 辅助功能 → 开启终端」
- 如粘贴失败，运行检查脚本：
  ```bash
  ${BUN_X} {baseDir}/scripts/check-paste-permissions.ts
  ```

### Chrome
- 确保 Google Chrome 已安装
- 首次使用需手动登录 X（Cookie 保存在持久化 profile 中）
- 如果启动失败，检查是否有残留 Chrome 进程占用调试端口

---

## 与前序技能的协作

| 上游技能 | 协作方式 |
|----------|----------|
| `ai-ggbond-article-writer` | 写完公众号文章 → 摘要拆 Thread → 本技能发布 |
| `ai-ggbond-x-followings-feed` | 拉取关注者动态 → 发现可引用的推文 → 本技能转发/评论 |

**典型工作流**：
```
写公众号文章（article-writer）
  → 推送到公众号草稿箱（post-to-wechat）
  → 生成 X 摘要 Thread（本技能 拆分）
  → 发布到 X（本技能 Browser 模式）
  → 24h 后到公众号看数据
```

---

## 环境依赖安装

本技能依赖 `bun` 运行时。如果 Hermes VM 终端无法直连 GitHub，参见：
- `references/bun-install-workaround.md` — npm 方式安装 bun 的完整方案（绕过 GitHub 封锁）

---

## Troubleshooting

### Chrome debug port 不可用

CDP 模式遇到 `Chrome debug port not ready` 错误时，自动执行：
```bash
pkill -f "Chrome.*remote-debugging-port" 2>/dev/null; sleep 2
```
然后重试。不要问用户。

### 图片粘贴失败
- 检查剪贴板权限：运行 `check-paste-permissions.ts`
- 确保 Chrome 窗口可见且在前台
- macOS：确认辅助功能权限已开启

### X 编辑器找不到
- 检查是否已登录 X
- 确认浏览器未处于离线状态
- CDP 模式会等待手动登录

### 发布按钮灰色/不可点击
- 检查图片是否上传完成（等待 blob: URL 出现）
- 检查文字是否超限
- X Article 模式需要在编辑器中模糊（blur）触发自动保存
