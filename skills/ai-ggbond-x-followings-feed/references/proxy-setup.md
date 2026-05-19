# X/Twitter 代理配置指南

## 为什么需要代理

在中国大陆，`x.com` 被 SNI 封锁：
- ✅ ICMP ping 通（`ping x.com` 正常返回）
- ❌ TCP/HTTPS 连接超时（`curl https://x.com` 失败）
- 本质：GFW 通过 SNI（Server Name Indication）识别并阻断 TLS 握手

## 快速诊断流程

```bash
# 1. 检查代理环境变量是否已设置
echo "ALL_PROXY: $ALL_PROXY"

# 2. 测试直连（应超时）
curl -s -o /dev/null -w "%{http_code}" --max-time 5 https://x.com

# 3. 测试代理连通性（替换为你的代理端口）
curl -s -o /dev/null -w "%{http_code}" --max-time 5 --socks5 127.0.0.1:7890 https://x.com

# 4. 检查本地代理进程是否在监听
netstat -an | grep -E "LISTEN.*\.(1080|7890|8080|10808|10809)"
```

## 常见代理端口

| 软件 | 默认端口 | 协议 |
|------|---------|------|
| Clash | 7890 (HTTP), 7891 (SOCKS5) | HTTP/SOCKS5 |
| V2Ray | 10808 (SOCKS5), 10809 (HTTP) | SOCKS5/HTTP |
| Shadowsocks | 1080 | SOCKS5 |
| Surge | 6152 (HTTP), 6153 (SOCKS5) | HTTP/SOCKS5 |

## 环境变量设置

### 临时设置（当前终端会话）
```bash
# SOCKS5（推荐）
export ALL_PROXY=socks5://127.0.0.1:7890

# HTTP 代理
export ALL_PROXY=http://127.0.0.1:7890
```

### 持久化到 Hermes（推荐）
```bash
# 添加到 ~/.hermes/.env
echo 'ALL_PROXY=socks5://127.0.0.1:7890' >> ~/.hermes/.env
# 重启 gateway 使生效
```

### 验证
```bash
source ~/.hermes/.env
curl -I --max-time 5 https://x.com
# 应返回 HTTP/2 200 或 302
```

## 踩坑记录

1. **ping ≠ 可用**：ICMP 能通不代表 TCP 能通，GFW 的 SNI 封锁只影响 TLS 握手层
2. **bird CLI 无代理参数**：bird CLI 不支持 `--proxy` 参数，必须通过环境变量 `ALL_PROXY` 设置
3. **Tailscale exit node 冲突**：如果使用 Tailscale，exit node 的代理可能覆盖本地代理设置，检查 `tailscale status`
4. **环境变量继承**：子进程会继承父进程的环境变量，但 Hermes gateway 启动时加载 `.env`，运行中修改需重启 gateway
