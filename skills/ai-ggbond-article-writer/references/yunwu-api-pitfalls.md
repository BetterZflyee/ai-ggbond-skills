# 云雾 API 生图已知问题

> 版本：v1.0 | 更新日期：2026-05-11

---

## 问题：V4 脚本 response_format 参数报错

### 症状

使用 `generate_images_v4.py` 脚本调用 gpt-image-2 时，返回：
```
Unknown parameter: 'response_format'
```

### 根因

V4 脚本在调用 OpenAI Images API 时传了 `response_format` 参数，但云雾 API (yunwu.ai) 的 gpt-image-2 代理不支持此参数。

### 解决方案

绕过 V4 脚本，直接用原始 API 调用，**不传 `response_format`**：

```python
import requests, base64

def gen_image(api_key, prompt, filename, output_dir, size='1792x1024'):
    """用 gpt-image-2 生成图片，不传 response_format"""
    url = 'https://yunwu.ai/v1/images/generations'
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

### 正确的 size 参数

| 模型 | 支持的尺寸 |
|------|-----------|
| gpt-image-2 | 1024x1024, 1536x1024, 1024x1536, 1792x1024, auto |
| gpt-image-1 | 1024x1024, 1536x1024, 1024x1536, auto |

### 批量生成建议

- 每张图约 90-120 秒
- 每批 3-4 张，间隔 12 秒
- 分多批执行，避免 terminal 超时（600s）
