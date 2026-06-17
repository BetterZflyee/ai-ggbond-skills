# Tailscale + Tinyproxy 代理方案（2026-06-07）

## 问题

Mac Mini 的 Tailscale exit node 配置后，`curl ifconfig.me` 仍返回本机公网 IP（23.249.27.148），不是 VPS IP（45.156.151.87）。原因是 macOS 路由优先级：WiFi/以太网默认路由优先于 Tailscale。

## 解决方案

在 VPS 上运行 tinyproxy，Mac 通过 Tailscale 内网 IP 访问代理。

### VPS 端配置

```bash
apt update && apt install -y tinyproxy

# 编辑 /etc/tinyproxy/tinyproxy.conf
# 注释掉: Allow 127.0.0.1
# 添加: Allow 100.x.x.x（Mac 的 Tailscale IP）
# 添加: Allow 163.x.x.x（Mac 的其他可能 IP）

systemctl restart tinyproxy
systemctl status tinyproxy

# 腾讯云安全组需放行 TCP 8888 端口
```

### Mac 端推送

```bash
export http_proxy=http://100.117.255.36:8888   # VPS 的 Tailscale IP
export https_proxy=http://100.117.255.36:8888
npx -y bun wechat-api.ts ...
```

### 验证

```bash
# 测试代理连通性
curl -s --max-time 10 -x http://100.117.255.36:8888 https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=xxx&secret=xxx

# 成功返回 access_token
```

## ⚠️ 关键坑

1. **不要用公网 IP（45.156.151.87:8888）**——从 VPS 出口再访问 VPS 自己的公网 IP 会遇到云厂商 hairpin/NAT 问题，连接失败。
2. **腾讯云安全组**必须放行 8888 端口，否则外部无法连接。
3. **tinyproxy 默认 Allow 127.0.0.1**——必须注释掉并添加 Mac 的 Tailscale IP。
4. **微信 API 不支持代理的 CONNECT 方法**——tinyproxy 默认支持 HTTP 代理，对 HTTPS 使用 CONNECT 隧道，这是正常行为。

## 为什么不用 Tailscale exit node

macOS 的 Tailscale App 配置 exit node 后，系统路由表中 Tailscale 默认路由优先级可能低于 WiFi/以太网。这是 macOS 的已知问题，目前没有可靠的命令行修复方式（Tailscale CLI 在 Mac 上不可用）。

通过 Tailscale 内网 IP 直连 tinyproxy 是更稳定的方案。
