# Tailscale Exit Node + Tinyproxy 代理方案（2026-06-07 实战）

## 背景

当 Mac Mini 的公网 IP 是动态的，无法固定加入微信公众号 IP 白名单时，需要通过 VPS 的固定 IP 推送文章。

## 方案架构

```
Mac Mini (动态 IP) → Tailscale 网络 → VPS tinyproxy (固定 IP 43.156.151.87) → 微信 API
```

## 配置步骤

### 1. VPS 端配置 tinyproxy

```bash
# 安装
apt update && apt install -y tinyproxy

# 配置白名单（允许 Tailscale IP 访问）
echo "Allow 100.119.152.20" >> /etc/tinyproxy/tinyproxy.conf

# 启动
systemctl restart tinyproxy

# 放行防火墙
ufw allow 8888
```

### 2. Mac Mini 端使用代理

**关键**：使用 VPS 的 **Tailscale IP**（100.x.x.x），不要用公网 IP（43.x.x.x）。

```bash
# ✅ 正确：用 Tailscale IP
export http_proxy=http://100.117.255.36:8888
export https_proxy=http://100.117.255.36:8888

# ❌ 错误：用公网 IP（会遇到 hairpin/NAT 问题）
export http_proxy=http://43.156.151.87:8888
```

### 3. 验证代理

```bash
# 测试微信 API 连通性
curl -s --max-time 15 -x http://100.117.255.36:8888 \
  "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APP_ID&secret=APP_SECRET"
```

## 常见问题

### 问题 1：Connection refused

**原因**：tinyproxy 未启动或防火墙未放行

**解决**：
```bash
# VPS 端检查
systemctl status tinyproxy
netstat -tlnp | grep 8888
ufw status
```

### 问题 2：使用公网 IP 访问 tinyproxy 失败

**原因**：云厂商 hairpin/NAT 问题，从 VPS 出口再访问 VPS 自己的公网 IP 会失败

**解决**：改用 Tailscale IP（100.x.x.x）

### 问题 3：Tailscale exit node 已开启但出口 IP 未变

**原因**：macOS 路由优先级问题，WiFi/以太网优先级高于 Tailscale

**解决**：
1. 在 Tailscale App 中确认 exit node 已选择
2. 或者直接使用 tinyproxy 代理方案（更稳定）

## 微信推送命令模板

```bash
cd ~/.hermes/skills/productivity/ai-ggbond-post-to-wechat/scripts

export WECHAT_APP_ID=wx...
export WECHAT_APP_SECRET=...
export http_proxy=http://100.117.255.36:8888
export https_proxy=http://100.117.255.36:8888

npx -y bun wechat-api.ts /path/to/article.html \
  --theme default \
  --title "标题" \
  --summary "摘要" \
  --author "AI朱朱侠" \
  --cover /path/to/cover.jpg
```
