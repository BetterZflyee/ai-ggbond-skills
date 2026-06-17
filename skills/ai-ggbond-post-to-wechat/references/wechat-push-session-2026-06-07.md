# WeChat Push Session Log — 2026-06-07

## Scenario
Pushing article "睡觉时公司自己变好了，YC 的 AI 递归循环实战" (8046字, 7 images) to WeChat draft box.

## Pitfalls Encountered

### 1. Credential Configuration Path Confusion
**Symptom**: `Missing WECHAT_APP_ID or WECHAT_APP_SECRET` error even after writing to `~/.hermes/.env`.

**Root cause**: In the Hermes sandbox, `$HOME` resolves to `/Users/admin/.hermes/profiles/neirong/home`, not `/Users/admin`. The `.hermes/.env` file must be written to the sandbox HOME path.

**Solution**: Use `echo $HOME` to check actual home directory, then write credentials there. Or use `export WECHAT_APP_ID=... WECHAT_APP_SECRET=...` inline in the command.

**Lesson**: Always set credentials as inline `export` in the push command rather than relying on .env file location.

### 2. Proxy vs Direct Connection for WeChat API
**Symptom**: `ECONNRESET` socket error when using `https_proxy=http://127.0.0.1:7897`.

**Root cause**: WeChat API (`api.weixin.qq.com`) is a China domestic service. Routing it through an overseas proxy causes socket resets.

**Solution**: `unset https_proxy && unset http_proxy` before calling WeChat API. WeChat API should be called DIRECTLY, not through proxy.

**Lesson**: For China domestic APIs (WeChat, Douyin, etc.), disable proxy. Only use proxy for blocked sites (Google, YouTube, Twitter).

### 3. IP Whitelist Error (40164)
**Symptom**: `invalid ip 23.249.27.148 ipv6 ::ffff:23.249.27.148, not in whitelist`

**Root cause**: Tailscale exit node not properly activated. Current outbound IP was `23.249.27.148` (dynamic ISP IP), not `43.156.151.87` (VPS static IP in whitelist).

**Diagnostic command**: `curl -s ifconfig.me` (without proxy) to check current IP.

**Solution options**:
- Option A: Add current IP to WeChat whitelist (临时方案)
- Option B: Ensure Tailscale exit node is active (长期方案)

**Lesson**: Always verify IP with `curl -s ifconfig.me` (NO proxy) before attempting push. If IP ≠ 43.156.151.87, stop and ask user to fix Tailscale first.

### 4. Feishu send_message Target Format
**Symptom**: `invalid receive_id` error when using `feishu:ou_714d50c888dc32829dc4719d31c82fdc`.

**Root cause**: Used user_id (`ou_...`) instead of chat_id (`oc_...`).

**Solution**: Call `send_message action=list` first to get correct targets. Use `feishu:oc_99929d11c9332515fc59cfb22e1de2e0` format.

**Lesson**: When sending files via Feishu, always list targets first. The correct format is `feishu:{chat_id}`, not `feishu:{user_id}`.

## Push Checklist (Updated)
1. ✅ Markdown has `![alt](images/xxx.png)` references
2. ✅ Images compressed to <500KB (JPEG quality=75)
3. ✅ `curl -s ifconfig.me` returns 43.156.151.87 (NO proxy)
4. ✅ Credentials set as env vars inline
5. ✅ Proxy DISABLED for WeChat API calls
6. ✅ Use `--dry-run` first to validate config
