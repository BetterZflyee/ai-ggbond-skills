# CDP Cookie 注入方案

当 Chrome profile 无 X cookies 导致 CDP 脚本挂起时，通过 Python + websocket 直连 Chrome DevTools Protocol，注入 auth cookies 后直接操作 X 编辑器。

**适用范围**：短帖、Thread 回复、引用转发。不支持图片/视频（需剪贴板粘贴方案）。

---

## 前置条件

- Python 3 + `websocket-client` 已安装：`pip3 install websocket-client requests`
- Chrome 已安装
- `~/.hermes/.env` 有 `AUTH_TOKEN` 和 `CT0`
- Clash 代理 `127.0.0.1:7897` 运行中

---

## 完整流程

### Step 1：启动 Chrome（CDP + 代理）

```bash
pkill -f "Google Chrome" 2>/dev/null; sleep 3
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --proxy-server="http://127.0.0.1:7897" \
  --user-data-dir="/Users/admin/Library/Application Support/ai-ggbond-skills/chrome-profile" \
  --no-first-run --no-default-browser-check &
```

**关键 flag 说明**：

| Flag | 为什么必须 |
|------|----------|
| `--remote-allow-origins=*` | 否则 Python websocket 被 403 Forbidden |
| `--proxy-server="http://127.0.0.1:7897"` | X.com 被墙/限速，不走代理会超时 |
| `--remote-debugging-port=9222` | CDP 端口 |

### Step 2：验证 Chrome 启动

```bash
curl -s http://127.0.0.1:9222/json/version | python3 -c "import sys,json; print(json.load(sys.stdin).get('Browser','FAIL'))"
# 预期输出：Chrome/148.0.7778.179
```

### Step 3：注入 Cookies 并发帖

使用以下 Python 模板：

```python
import json, os, time
from websocket import create_connection
import requests

# === 读取认证 ===
with open(os.path.expanduser("~/.hermes/.env")) as f:
    env = {}
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v.strip('"')

AUTH_TOKEN = env["AUTH_TOKEN"]
CT0 = env["CT0"]

# === 连接 CDP ===
r = requests.get("http://127.0.0.1:9222/json")
pages = r.json()
x_page = next(p for p in pages if 'x.com' in p.get('url',''))
ws = create_connection(x_page['webSocketDebuggerUrl'], timeout=25)

mid = [0]
def cmd(method, params=None):
    mid[0] += 1
    ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
    while True:
        resp = json.loads(ws.recv())
        if resp.get('id') == mid[0]:
            return resp
        # 跳过事件消息（method != null 且无 id）

# === 启用域（必须！） ===
cmd("Runtime.enable")
cmd("Page.enable")
cmd("Network.enable")

# === 注入 X Cookies ===
cmd("Network.setCookie", {
    "name": "auth_token", "value": AUTH_TOKEN,
    "domain": ".x.com", "path": "/",
    "httpOnly": True, "secure": True, "sameSite": "Lax"
})
cmd("Network.setCookie", {
    "name": "ct0", "value": CT0,
    "domain": ".x.com", "path": "/",
    "secure": True, "sameSite": "Lax"
})

# === 导航到发帖页 ===
cmd("Page.navigate", {"url": "https://x.com/compose/post"})
time.sleep(5)  # 等页面加载

# === 填入文字 ===
TEXT = "你的推文内容"

js = f'''
(function() {{
    const editor = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (!editor) return 'NO_EDITOR';
    editor.focus();
    document.execCommand('insertText', false, {json.dumps(TEXT)});
    return 'OK: ' + editor.innerText.substring(0, 30);
}})();
'''
r = cmd("Runtime.evaluate", {"expression": js, "returnByValue": True})
print(r.get('result',{}).get('result',{}).get('value','?'))

ws.close()
print("✅ 文字已填入 Chrome 窗口，请用户检查后点击发布。")
```

### Step 4：Thread 回复

每条回复导航回原始推文并点击回复按钮：

```python
# 导航到首条推文
cmd("Page.navigate", {"url": "https://x.com/Zflyee/status/{TWEET_ID}"})
time.sleep(4)

# 点击回复按钮
js_click = '''(function() {
    const btn = document.querySelector('[data-testid="reply"]');
    if (btn) { btn.click(); return 'OK'; }
    return 'FAIL';
})();'''
cmd("Runtime.evaluate", {"expression": js_click, "returnByValue": True})
time.sleep(2)

# 填入回复文字
js_type = f'''(function() {{
    const e = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (!e) return 'NO_EDITOR';
    e.focus();
    document.execCommand('insertText', false, {json.dumps(REPLY_TEXT)});
    return 'OK';
}})();'''
cmd("Runtime.evaluate", {"expression": js_type, "returnByValue": True})
```

---

## 常见坑

| 坑 | 现象 | 解 |
|----|------|-----|
| 忘加 `--remote-allow-origins=*` | WebSocket handshake 403 | 重启 Chrome 加 flag |
| 忘调 `Runtime.enable` | `evaluate` 返回 `?` | 先 `cmd("Runtime.enable")` |
| Cookie 注入了但还是登录页 | 页面在注入前就加载了 | `Page.navigate` 到 compose/post 让页面用新 cookie 刷新 |
| `execCommand` 不生效 | contenteditable 没 focus | 先 `editor.focus()` |
| 等待时间太短 | DOM 还没渲染 | navigate 后等 4-6s，click 后等 2-3s |
| CDP 消息混入事件 | `recv()` 读到 method 消息 | 循环读，只取 `'id' in resp` 的消息 |
| `document.querySelector` 找不到元素 | X DOM 结构变了 | 先 `console.log(document.body.innerText.substring(0,200))` 排查 |

---

## 使用原则

- **每条推文用户手动点发布**：绝不自动点 Post 按钮，安全第一
- **发完等用户说"好了"再继续**：不连续填多条，避免串位
- **如果用户说"直接发"**：可以尝试 JS `click()` 发布按钮（`[data-testid="tweetButton"]`），但默认不这么做
