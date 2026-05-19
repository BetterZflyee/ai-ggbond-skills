# 踩坑记录 / Pitfalls & Learnings

## `bird home` vs `bird following`

- `bird home --json -n N` → Home Timeline 推文（正确，返回推文内容）
- `bird following --json -n N` → 关注用户列表/Profile（不是推文！）
- 早期版本的脚本用错了命令，已修复为 `bird home`

## 网络连通性预检

- bird CLI 在网络不通时会挂起 30 秒以上才超时
- 脚本中加了 `curl -s -o /dev/null -w "" --max-time 5 https://x.com` 预检
- 预检失败时直接报错，避免用户等待 30 秒+

## macOS `date` 命令差异

- Linux: `date -d "3 days ago" +%s`
- macOS: `date -v-3d +%s`
- 脚本中两者都试，用 `||` 串联

## 推文链接生成

- bird 输出的 JSON 包含 `author.username` 和 `id` 字段
- 链接格式: `https://x.com/{username}/status/{id}`
- 脚本用 python3 后处理自动添加 `url` 字段
- 引用推文 (quotedTweet) 也需要补链接

## shell 变量嵌入 python 的安全问题

- 不要用 `python3 -c "... $VAR ..."` 方式嵌入 JSON 数据
- 特殊字符（引号、反斜杠等）会导致 shell 注入
- 正确做法: `echo "$VAR" | python3 -c "import json,sys; data=json.load(sys.stdin); ..."` 通过 stdin 管道传递

## .env 环境变量生效

- 写入 ~/.hermes/.env 后需要重启 gateway 才能生效
- `hermes gateway restart` 或从消息平台发 `/restart`
