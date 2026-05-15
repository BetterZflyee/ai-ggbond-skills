# Hermes 适配说明

> 本文件记录 aiggbond-post-to-wechat 技能在 Hermes Agent 环境下的适配修改。

## 路径修改

**原版**：所有配置路径使用 `~/.ai-ggbond-skills/`
**修改后**：所有配置路径改为 `~/.ai-ggbond-skills/`

修改原因：统一使用 `~/.ai-ggbond-skills/` 作为所有技能的配置根目录，避免在 home 目录下创建多个散落文件夹。

### 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `scripts/wechat-extend-config.ts` | EXTEND.md 和 .env 搜索路径 |
| `scripts/wechat-api.ts` | 凭证搜索路径提示文字 |
| `scripts/check-permissions.ts` | 环境变量文件检查路径 |
| `scripts/wechat-extend-config.test.ts` | 测试用例中的路径 |
| `references/*.md` | 所有文档中的路径引用 |
| `SKILL.md` | 配置说明中的路径 |

### 凭证存储

```
~/.ai-ggbond-skills/.env 中添加：
WECHAT_APP_ID=<your_app_id>
WECHAT_APP_SECRET=<your_app_secret>
```

## Tailscale Exit Node（动态 IP 解决方案）

微信公众号 API 要求 IP 白名单。如果 Mac Mini 使用动态公网 IP，需要通过 Tailscale Exit Node 走固定 IP 的云服务器。

### 配置步骤

1. VPS 上安装 Tailscale 并开启出口节点：
```bash
tailscale up --advertise-exit-node
```

2. Tailscale 后台批准出口节点：
https://login.tailscale.com/admin/machines → 机器 → Edit route settings → Use as exit node ✅

3. 微信公众号白名单添加 VPS 固定 IP

4. Mac Mini 连接出口节点：
```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale up --exit-node=<vps-tailscale-ip> --accept-routes
```

5. 验证：
```bash
curl -s ifconfig.me
# 应输出 VPS 的固定公网 IP
```

## bun 运行时

技能脚本使用 TypeScript，需要 bun 运行时：
```bash
npm install -g bun
```
