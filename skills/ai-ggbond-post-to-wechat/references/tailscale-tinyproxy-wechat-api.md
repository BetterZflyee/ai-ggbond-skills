# Tailscale + tinyproxy 代理方案（动态 IP 环境）

## 背景

飞哥的 Mac Mini 是动态公网 IP，无法固定加入微信公众号 IP 白名单。解决方案：通过 VPS 的固定 IP（45.156.151.87）代理访问微信 API。

## 架构

```
Mac Mini (动态 IP) 
  → Tailscale 网络 (100.117.255.36:8888) 
  → VPS tinyproxy 
  → 微信 API (出口 IP: 43.156.151.87)
```

## VPS 配置

```bash
# 安装 tinyproxy
apt update && apt install -y tinyproxy

# 配置白名单（允许 Tailscale IP 访问）
echo "Allow 100.119.152.20" >> /etc/tinyproxy/tinyproxy.conf
echo "Allow 100.117.255.36" >> /etc/tinyproxy/tinyproxy.conf

# 启动
systemctl restart tinyproxy

# 腾讯云安全组需要放行 TCP 8888
```

## Mac Mini 推送命令

```bash
export http_proxy=http://100.117.255.36:8888
export https_proxy=http://100.117.255.36:8888

npx -y bun wechat-api.ts article.html \
  --title "标题" \
  --summary "摘要" \
  --author "作者" \
  --cover cover.jpg
```

## ⚠️ 踩坑记录

### 1. Tailscale exit node 不等于出口 IP 变更

即使 VPS 端配置了 exit node，macOS 客户端需要在 App 中手动启用 "Use exit node"。但即使启用后，`curl ifconfig.me` 可能仍返回动态 IP（路由优先级问题）。

**结论：不要依赖 exit node 改变出口 IP，改用 Tailscale IP 直接访问 tinyproxy。**

### 2. 公网 IP 访问 VPS 自身的问题

从 Mac（走 exit node 出口 43.156.151.87）访问 `43.156.151.87:8888` 会触发云厂商 hairpin/NAT 问题，连接失败。

**正确做法：用 Tailscale IP `100.117.255.36:8888` 访问 tinyproxy。**

### 3. tinyproxy 不支持 HTTPS 隧道

tinyproxy 默认不支持 CONNECT 方法（HTTPS 隧道）。但微信 API 的 token 获取接口是 HTTPS，需要 tinyproxy 支持。

**解决方案：确认 tinyproxy 配置中 `ConnectPort 443` 已启用（默认应该有）。**

## 验证命令

```bash
# 测试代理连通性
curl -s --max-time 10 -x http://100.117.255.36:8888 https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=SECRET

# 成功返回：{"access_token":"...","expires_in":7200}
# 失败返回：{"errcode":40164,"errmsg":"invalid ip ..."}
```
