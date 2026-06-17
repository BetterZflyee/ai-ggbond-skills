# Tailscale Exit Node macOS 路由问题排查

## 问题现象

VPS 端已设置 exit node，Mac 端 Tailscale App 显示已连接，但 `curl ifconfig.me` 仍返回 Mac 本机公网 IP（非 VPS IP）。

## 根因

macOS 路由优先级问题。Tailscale 接口（utun20）虽有默认路由，但系统同时有 WiFi（en0）/以太网（en1）的默认路由，优先级更高。

检查方法：
```bash
netstat -rn | grep default
# 会看到多条 default 路由，utun20 可能不是最高优先级
```

## 解决方案（按优先级）

### 方案 A：Tailscale App 手动切换 exit node
1. 点击菜单栏 Tailscale 图标
2. Settings → Use exit node
3. 选择 VPS
4. 验证：`curl -s ifconfig.me` 应返回 VPS 公网 IP

### 方案 B：VPS 上装 tinyproxy（推荐备用）
当 Tailscale exit node 持续不生效时：
```bash
# VPS 上执行
apt update && apt install -y tinyproxy
# 允许 Tailscale 内网 IP 访问
echo "Allow 100.x.x.x" >> /etc/tinyproxy/tinyproxy.conf
systemctl restart tinyproxy
ufw allow 8888
```

Mac 端使用：
```bash
export http_proxy=http://VPS公网IP:8888
export https_proxy=http://VPS公网IP:8888
```

### 方案 C：临时加白名单（不推荐）
动态 IP 环境下每次 IP 变化都需重新加白名单，非长久之计。

## 关键细节

- 微信 API（api.weixin.qq.com）在国内可直连，**不需要代理**
- 如果用了代理反而可能 ECONNRESET，应 `unset http_proxy https_proxy`
- Tailscale 虚拟 IP（100.x.x.x）≠ VPS 公网 IP，白名单填公网 IP
- `ifconfig utun20` 可查看 Tailscale 接口状态
