# 贴图推送完整失败矩阵 (2026-05-27)

## 背景

尝试推送2张微信贴图（`--type newspic`），四种模式全试遍，无一成功。

## 失败矩阵

| 模式 | 脚本 | 失败症状 | 根因 |
|------|------|----------|------|
| **API** | `wechat-api.ts --type newspic` | 45166 `invalid content hint` | 微信内容校验拦截，非政治内容也触发 |
| **API + 大图** | `wechat-api.ts --type newspic` | ECONNRESET `socket connection closed` | 图片 >1MB 触发微信上传断连；已压缩到 <200KB 后此问题消失 |
| **Browser CDP** | `wechat-browser.ts --type newspic --image` | Menu items: ["更多"] / 贴图 menu not found | 微信后台 UI 改版，脚本选择器失效 |
| **Agent Browser** | `wechat-agent-browser.ts --title --image --content` | Login timeout (反复 Waiting for login) | 需要用户手动扫码，无人值守超时 |

## 唯一可用方案（当前）

用户手动在公众号后台操作：

1. 打开 https://mp.weixin.qq.com/
2. 扫码登录
3. 点击「图文」→「贴图」
4. 上传图片 → 填标题(≤20字) → 填内容(≤1000字) → 保存草稿

## agent-browser 安装步骤

```bash
npm install -g agent-browser
# 如果 agent-browser 命令不可用，创建 symlink：
ln -sf /opt/homebrew/Cellar/node/$(node -v | cut -d. -f1)/lib/node_modules/agent-browser/bin/agent-browser.js /opt/homebrew/bin/agent-browser
```

注意：`npm bin -g` 在新版 npm 中已被移除，需要手动找到 bin 路径。

## 贴图推送前强制检查清单（补充）

1. ✅ 图片已压缩到 <500KB（推荐 50-200KB JPEG quality=75）
2. ✅ Tailscale 出口 IP = 43.156.151.87
3. ✅ Markdown 包含 `![配图](images/xxx.jpg)` 引用
4. ✅ 封面图通过 `--cover` 单独指定
5. ✅ **配图中不含 #标签**（标签是正文内容）
6. ✅ 标题 ≤20 字

## 适用场景

当用户说「推送到微信贴图」时，先尝试 API 模式（压缩图后），若 45166 则告知用户：自动推送贴图目前不可用，建议手动操作或改用文章模式。
