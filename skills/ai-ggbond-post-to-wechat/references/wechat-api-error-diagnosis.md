# 微信 API 错误诊断速查

## 错误码速查

| 错误码 | 含义 | 症状 | 修复 |
|--------|------|------|------|
| **40125** | `invalid appsecret` | access_token 获取失败 | AppSecret 错误 **或** IP 不在白名单 |
| **40164** | `invalid ip, not in whitelist` | access_token 获取失败 | IP 不在白名单，需添加 |
| **40013** | `invalid appid` | access_token 获取失败 | AppID 格式错误或不存在 |
| **45166** | `invalid content hint` | 贴图(newspic)推送失败 | 微信内容审核拦截，降级到 Browser 模式 |
| **ECONNRESET** | socket 断连 | 图片上传中断 | 图片 >1MB，需压缩；或代理问题 |

## ⚠️ 关键坑：40125 ≠ 一定是 AppSecret 错误

**2026-06-15 实战教训**：40125 错误码同时覆盖两种情况：
1. AppSecret 确实错误
2. AppSecret 正确，但出口 IP 不在白名单

**诊断步骤（必须按顺序执行）**：

```bash
# Step 1: 确认出口 IP（必须 unset 代理）
unset https_proxy && unset http_proxy && curl -s ifconfig.me
# 记录输出的 IP

# Step 2: 用 curl 直接测试 access_token
curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=你的APPID&secret=你的APPSECRET"

# Step 3: 判断错误
# - 返回 40125 → AppSecret 可能错误，但也可能是 IP 问题
# - 返回 40164 → 明确是 IP 白名单问题
# - 返回 40013 → AppID 错误
# - 返回 access_token → 一切正常
```

**区分 AppSecret 错误 vs IP 白名单错误**：
- 用一个**明显错误的 AppID**（如 `wxtest123`）测试，如果返回 `40013`，说明 AppID 格式正确
- 用一个**明显错误的 Secret**（如 `test`）测试，如果也返回 `40125`，说明无法区分
- **最终判断方法**：确认出口 IP 后，检查该 IP 是否在白名单中。如果不在，先加白名单再测试

**绝不应该做的事**：反复让用户重置 AppSecret 5 次，最后才发现是 IP 白名单问题。

## 出口 IP 变化场景

Mac Mini 的出口 IP 会变化：
- **VPS 固定 IP**（通过 Tailscale exit node）：`43.156.151.87` ✅ 已在白名单
- **本机公网 IP**（直接连接）：`163.125.188.202` 等，动态变化
- **代理 IP**（通过 Clash 等）：`50.7.252.67` 等，不在白名单

**推送前必须确认出口 IP**：
```bash
unset https_proxy && unset http_proxy && curl -s -4 ifconfig.me
```

如果返回的不是 `43.156.151.87`，说明 Tailscale exit node 未生效，需要：
1. 手动在 Tailscale App 中选择 exit node，或
2. 将当前 IP 加入微信公众号白名单
