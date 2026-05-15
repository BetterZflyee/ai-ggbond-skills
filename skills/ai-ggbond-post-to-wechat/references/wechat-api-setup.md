# WeChat API Setup & Tailscale IP Whitelist

## Problem

WeChat Official Account API requires caller IP in whitelist. Dynamic public IPs change frequently, making static whitelist impractical.

## Solution: Tailscale Exit Node

Route API traffic through a fixed-IP VPS via Tailscale VPN.

```
Mac Mini (dynamic IP) → Tailscale tunnel → VPS (fixed IP) → WeChat API
```

### VPS Setup (OpenCloudOS/Ubuntu/Debian)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Login
sudo tailscale up

# Advertise as exit node
sudo tailscale up --advertise-exit-node
```

Then approve at https://login.tailscale.com/admin/machines → machine → Edit route settings → Use as exit node ✅

### Mac Mini Setup

```bash
# Connect to VPS exit node
/Applications/Tailscale.app/Contents/MacOS/Tailscale up --exit-node=<vps-tailscale-ip> --accept-routes

# Verify - should show VPS public IP
curl -s ifconfig.me
```

### WeChat Whitelist

Add VPS's fixed public IP to: 微信公众平台 → 开发 → 基本配置 → IP白名单

### Switching Back (no exit node)

```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale up --exit-node= --accept-routes
```

## Tailscale Status Reference

```bash
# Check status
/Applications/Tailscale.app/Contents/MacOS/Tailscale status

# Shows: <tailscale-ip> <hostname> <account> <os> <status>
# Example:
# 100.106.39.79  tx-vps        zflyee@ linux  -
# 100.119.152.20 openclawmac-mini zflyee@ macOS  -
```

## Known Issues

- VPS may warn about UDP GRO forwarding (cosmetic, doesn't affect exit node functionality)
- `tailscale up` on macOS requires mentioning all non-default flags; use `--reset` or include `--accept-routes`
- Tailscale CLI on macOS is at `/Applications/Tailscale.app/Contents/MacOS/Tailscale` (not in PATH)
