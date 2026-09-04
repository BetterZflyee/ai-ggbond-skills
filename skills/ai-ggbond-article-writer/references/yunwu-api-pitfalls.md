# 云雾 API 生图已知问题

> 版本：v1.1 | 更新日期：2026-05-15

---

## ⚠️ 问题：gpt-image-2 间歇性不可用（2026-05 实测）

### 症状

调用 gpt-image-2 时返回：
```json
{"error":{"message":"当前分组上游负载已饱和，请稍后再试","code":"model_not_found"}}
```
或直接超时（180s+ 无响应）。

### 根因

yunwu.ai 的 gpt-image-2 渠道**间歇性不可用**，不是临时限流，是渠道本身不稳定。
- `api.apiplus.org` 备用节点同样受影响（同一后端）
- `api3.wai.vip` DNS 解析失败，不可用
- 短暂可用窗口可能只持续 10-20 分钟，之后再次下线
- `gpt-image-1` 可用但质量明显低于 gpt-image-2

### 应对策略

1. **生图前先探测**：用小 prompt（`size: 1024x1024`）测一次，确认 200 再批量生成
2. **不要无限重试**：3 次失败后通知用户，等待用户指示
3. **备用方案**：
   - 让用户在 ChatGPT 官网（chat.openai.com）手动生成，提示词准备好
   - 或等 API 恢复后用定时任务自动重试

### 探测脚本

```python
import requests, os
API_KEY = os.environ['YUNWU_API_KEY']
resp = requests.post('https://api.openlux.ai/v1/images/generations',
    headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
    json={'model': 'gpt-image-2', 'prompt': 'test', 'n': 1, 'size': '1024x1024'},
    timeout=60)
print(f'Status: {resp.status_code}')  # 200=可用, 429=不可用, timeout=不可用
```

---

## 问题：V4 脚本 response_format 参数报错

### 症状

使用 `generate_images_v4.py` 脚本调用 gpt-image-2 时，返回：
```
Unknown parameter: 'response_format'
```

### 解决方案

绕过 V4 脚本，直接用原始 API 调用，**不传 `response_format`**：

```python
import requests, base64

def gen_image(api_key, prompt, filename, output_dir, size='1792x1024'):
    url = 'https://api.openlux.ai/v1/images/generations'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    payload = {'model': 'gpt-image-2', 'prompt': prompt, 'n': 1, 'size': size}
    resp = requests.post(url, headers=headers, json=payload, timeout=300)
    if resp.status_code == 200:
        data = resp.json()
        img_data = data.get('data', [{}])[0]
        img_url = img_data.get('url', '')
        b64_data = img_data.get('b64_json', '')
        if img_url:
            r = requests.get(img_url, timeout=120)
            with open(f'{output_dir}/{filename}', 'wb') as f: f.write(r.content)
            return True, len(r.content)
        elif b64_data:
            b = base64.b64decode(b64_data)
            with open(f'{output_dir}/{filename}', 'wb') as f: f.write(b)
            return True, len(b)
    return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
```

---

## 问题：V4 脚本代理环境残留（2026-05-16 实测）

### 症状

用户已关闭代理（Clash），但 `generate_images_v4.py` 脚本仍报：
```
ProxyError('Unable to connect to proxy', RemoteDisconnected('Remote end closed connection without response'))
```
或直接超时 600 秒无响应。

### 根因

Python 的 `urllib3`（requests 底层）会读取系统级代理配置，即使用户在 shell 层面关了代理，进程内的环境变量可能仍保留 `HTTPS_PROXY` 值。脚本内部没有清除代理逻辑。

### 解决方案

**绕过脚本，直接用 Python requests 调 API，并显式清除代理：**

```python
import os, json, base64, requests

# 显式清除代理
for k in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:
    os.environ.pop(k, None)

# 加载 API Key
env_path = os.path.expanduser("~/.ai-ggbond-skills/.env")
api_key = ""
with open(env_path) as f:
    for line in f:
        if line.startswith("YUNWU_API_KEY="):
            api_key = line.strip().split("=", 1)[1]

# 直接调 yunwu.ai（最稳定端点）
resp = requests.post(
    "https://api.openlux.ai/v1/images/generations",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json={"model": "gpt-image-2", "prompt": prompt, "size": "1792x1024", "quality": "standard"},
    timeout=180
)
data = resp.json()
img_data = base64.b64decode(data["data"][0]["b64_json"])
with open("output.png", "wb") as f:
    f.write(img_data)
```

### API 端点稳定性排序（2026-05-16 实测）

| 端点 | 状态 | 备注 |
|------|------|------|
| `yunwu.ai` | ✅ 最稳定 | Python requests 直连，50-60 秒出图 |
| `api.apiplus.org` | ⚠️ 不稳定 | 有时返回空响应，有时返回 base64 |
| `api3.wai.vip` | ❌ 不可用 | DNS 解析失败或无响应 |

### 其他踩坑

1. **curl 处理 base64 大 JSON 会超时截断** → 必须用 Python requests
2. **`article_manager.py` 脚本硬编码 Windows 路径** `F:\\AI Workstation\\...` → macOS 上报 `FileNotFoundError`，需手动创建文件夹
3. **信息图生成耗时 50-60 秒**，封面图约 45 秒。脚本默认 300 秒超时如果同时生成两张可能不够
4. **`quality` 参数**：传 `"standard"` 即可，`"high"` 会显著增加耗时

---

## 正确的 size 参数

| 模型 | 支持的尺寸 |
|------|-----------|
| gpt-image-2 | 1024x1024, 1536x1024, 1024x1536, 1792x1024, auto |
| gpt-image-1 | 1024x1024, 1536x1024, 1024x1536, auto |

## 批量生成建议

- 每张图约 90-120 秒
- 每批 3-4 张，间隔 45 秒（2026-05 实测：45s 间隔更安全）
- 分多批执行，避免 terminal 超时（600s）
- 背景进程输出会被 Python 缓冲，无法实时看到进度——通过检查文件时间戳判断进度
