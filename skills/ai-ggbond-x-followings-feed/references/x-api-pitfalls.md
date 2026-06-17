# X/Twitter 信息流获取踩坑记录

## 1. bird CLI 命令区别

| 命令 | 说明 | 适用场景 |
|------|------|----------|
| `bird following --json` | 获取关注用户列表（Profile） | 查看关注了谁 |
| `bird home --json -n 20` | 获取 "For You" 推荐流 | 看算法推荐内容 |
| `bird home --following --json -n 20` | 获取 "Following" 关注流 | **看关注博主的推文** |

**关键区别**：
- `bird home` = "For You" 推荐流（算法推荐，混入大量非关注内容）
- `bird home --following` = "Following" 关注流（你关注的人的推文，按时间排序）

## 2. 数据结构差异

### For You 推荐流 (HomeTimeline)

用户信息路径：
```
tweet_results.result.core.user_results.result.legacy.screen_name
tweet_results.result.core.user_results.result.legacy.name
```

### Following 关注流 (HomeLatestTimeline)

用户信息路径：
```
tweet_results.result.core.user_results.result.core.screen_name
tweet_results.result.core.user_results.result.core.name
```

**注意**：Following 流的用户信息在 `.core` 不是 `.legacy`！解析时需兼容两种结构。

### 推荐的解析代码

```python
user_result = tweet_result.get("core", {}).get("user_results", {}).get("result", {})
user_core = user_result.get("core", {})
user_legacy = user_result.get("legacy", {})

# 优先用 .core（Following流），fallback 到 .legacy（For You流）
username = user_core.get("screen_name") or user_legacy.get("screen_name", "")
name = user_core.get("name") or user_legacy.get("name", "")
```

## 3. bird CLI 不支持代理

bird CLI 是 Node.js 脚本（v0.8.4），使用原生 `fetch` API，**不响应** `HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY` 环境变量。

**症状**：
- 设置了代理，curl 可以访问 x.com
- 但 bird CLI 报 `fetch failed` 或超时

**解决方案**：使用 Python 脚本 + `requests` 库（自动响应代理环境变量）

## 3.5. requests 不可用时的 curl Fallback（2026-06-03 新增）

**场景**：Hermes VM 系统 Python 3.9 未安装 `requests`，且 `pip install` 因网络不通失败（pip 源被墙或代理不透传）。

**尝试过的方案**：
1. `pip3 install requests` → `Failed to establish a new connection`（pip 不走 HTTPS_PROXY）
2. Python `urllib` + `ProxyHandler` → 请求返回 **401 Unauthorized**

**可靠方案**：直接用 `curl -x` 调 X GraphQL API。curl 的代理实现与 X API 完全兼容。

**关键差异**：同一组 Cookie + Bearer Token + Headers，curl 返回 200，urllib 返回 401。不要浪费时间调试 urllib 代理问题，直接切 curl。

详见 `references/curl-x-api-workflow.md`。

## 4. Clash Verge 代理端口

飞哥机器上 Clash Verge 的 `mixed-port` 是 **7897**（不是默认的 7890）。

配置代理时用：
```bash
export HTTPS_PROXY=http://127.0.0.1:7897
```

检查 Clash 配置文件确认端口：
```bash
grep "mixed-port" ~/Library/Application\ Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml
```

## 5. X GraphQL API

### Following 流 Endpoint

```
POST https://x.com/i/api/graphql/{queryId}/HomeLatestTimeline
```

Query ID: `iOEZpOdfekFsxSlPQCQtPg`（可能随 X 更新变化）

### For You 流 Endpoint

```
POST https://x.com/i/api/graphql/{queryId}/HomeTimeline
```

Query ID: `HJFjzBgCs16TqxewQOeLNg`（可能随 X 更新变化）

### 分页机制

X API 支持 cursor 分页：
- 请求参数：`variables.cursor` = 上一页返回的 Bottom cursor
- 响应位置：`instructions[].entries[].content.cursorType == "Bottom"` 的 `value` 字段
- 每页约 40 条推文（包含推文 + cursor + 广告）

### 请求参数

```json
{
  "variables": {
    "count": 40,
    "includePromotedContent": false,
    "latestControlAvailable": true,
    "requestContext": "launch"
  },
  "features": { ... }
}
```

## 6. 数据量偏好

**用户明确表示**：只获取 20-40 条推文太少，希望获取更多数据。

**建议**：
- 默认使用分页脚本获取 3-5 页（120-200 条推文）
- 用户说"数据量太少"时，增加页数到 5-10 页

## 7. Query ID 更新

X 会定期更新 GraphQL Query ID。如果 API 返回 `{"errors":[{"message":"queryId ... not found"}]}`，需要：

1. 访问 x.com，打开 DevTools → Network
2. 搜索 `graphql` 请求
3. 找到 `HomeLatestTimeline` 或 `HomeTimeline` 的请求
4. 从 URL 中提取新的 queryId

## 8. Cookie 过期

AUTH_TOKEN 和 CT0 来自浏览器 session cookie。如果：
- 浏览器登出 X
- Session 刷新
- 长时间未使用

需要重新从浏览器提取 cookie：
1. 登录 x.com
2. DevTools → Application → Cookies → x.com
3. 复制 `auth_token` 和 `ct0` 的值
