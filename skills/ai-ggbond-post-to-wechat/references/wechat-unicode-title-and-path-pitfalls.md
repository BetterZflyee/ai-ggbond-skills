# WeChat 推送踩坑：Unicode 标题编码 & Bash 路径展开

## 问题1：Unicode 转义导致标题超限（2026-06-09 实战）

**症状**：
```
Error: Publish failed 45003: title size out of limit
```

**根因**：当标题通过 `python3 -c "print('中文标题')"` 或 heredoc 变量注入传入 bash 脚本时，中文字符可能被序列化为 Unicode 转义序列（如 `\u6211\u51b3\u5b9a`），而非 UTF-8 原始字节。微信 API 收到转义序列后按字节数计算长度，导致远超 64 字符限制。

**复现**：
```bash
# 错误：python3 生成的脚本中中文被转义
python3 -c "
script = 'npx -y bun wechat-api.ts --title \"\u6211\u51b3\u5b9a\"'
open('/tmp/push.sh','w').write(script)
"
# /tmp/push.sh 中 title 变成字面量 \u6211\u51b3\u5b9a 而非中文
```

**解法**：
1. 标题使用纯 ASCII 英文（最稳）
2. 或在 bash heredoc 中直接写中文（确保终端 UTF-8）：
   ```bash
   cat > /tmp/push.sh << 'EOF'
   #!/bin/bash
   npx -y bun wechat-api.ts --title "中文标题直接写"
   EOF
   ```
3. 或用 `printf` 解码：
   ```bash
   TITLE=$(printf '%b' '\u6211\u51b3\u5b9a')
   ```

**验证**：推送前检查脚本内容：
```bash
cat /tmp/push.sh | grep title
# 应显示中文，不应显示 \uXXXX
```

---

## 问题2：Bash 脚本中 `~` 展开到 Hermes HOME（2026-06-09 实战）

**症状**：
```
cd: /Users/admin/.hermes/profiles/neirong/home/.hermes/skills/.../scripts: No such file or directory
```

**根因**：Hermes terminal 中 `~` 展开为 `/Users/admin/.hermes/profiles/neirong/home`（Hermes 沙箱 HOME），而非 `/Users/admin`（真实 HOME）。当 bash 脚本通过 `cat > /tmp/push.sh << 'EOF'` 创建时，如果 heredoc 未加引号（`<< EOF` vs `<< 'EOF'`），shell 会在写入时展开 `~`。

**解法**：脚本中使用绝对路径，不用 `~`：
```bash
# ❌ 错误
cd ~/.hermes/skills/productivity/...

# ✅ 正确
cd /Users/admin/.hermes/skills/productivity/...
```

**更稳的做法**：在脚本顶部动态获取路径：
```bash
REAL_HOME=$(dscl . -read /Users/admin NFSHomeDirectory | awk '{print $2}')
cd "$REAL_HOME/.hermes/skills/productivity/..."
```

---

## 问题3：标题长度限制

**微信公众号标题限制**：64 个字符（中文算 1 个字符）。

**安全建议**：标题控制在 **20 个中文字符以内**，留余量给英文章节标题。

**被拒案例**：
- "我决定不再自己写提示词了——聊聊Loop Engineering这件小事"（23字符）→ 通过
- 但如果包含 Unicode 转义 `\u6211\u51b3...` → 按字节计数远超限制 → 被拒

**最佳实践**：推送前用 `wc -m` 检查标题字符数：
```bash
echo -n "你的标题" | wc -m
# 应 < 64
```
