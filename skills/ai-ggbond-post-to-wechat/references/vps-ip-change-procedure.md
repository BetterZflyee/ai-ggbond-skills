# VPS 出口 IP 变更全量替换操作手册

当飞哥更换 VPS（Tailscale exit node 的公网 IP）后，必须执行以下全量替换，不得遗漏任何引用。

## 替换清单

### 1. 记忆文件
- 文件：`/Users/admin/.hermes/memories/MEMORY.md`
- 搜索：`推WeChat需Tailscale出口IP`
- 替换 IP 为新的 VPS 公网 IP

### 2. 技能 SKILL.md
- 文件：`/Users/admin/.hermes/skills/productivity/ai-ggbond-post-to-wechat/SKILL.md`
- 搜索：所有旧 IP 出现位置（通常 4-5 处）
- 包括：架构图注释、验证命令、常见失败场景示例、正确出口 IP 说明

### 3. 技能参考文档
- `references/session-2026-05-19-ai-tools-article-push.md`（2 处）
- `references/session-2026-05-21-html-precision-push.md`（如有）
- `references/wechat-api-pitfalls.md`（如有引用示例 IP）

### 4. SOUL.md（如有引用）

## 验证步骤

替换完成后，执行：
```bash
grep -r "旧IP" /Users/admin/.hermes/skills/productivity/ai-ggbond-post-to-wechat/
grep "旧IP" /Users/admin/.hermes/memories/MEMORY.md
```
确认无残留旧 IP 引用。

## 推送前验证

```bash
# 1. 用户确认 Tailscale 已开
# 2. 验证出口 IP
curl -s --max-time 8 ifconfig.me
# 应返回新 VPS 公网 IP
```

## 当前有效 IP

**43.156.151.87**（2026-05-25 更新）