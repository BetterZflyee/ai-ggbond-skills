# 图片生成踩坑记录

> 实战中遇到的问题和解决方案，按出现频率排序。
> 更新日期：2026-05-11

---

## 坑1：yunwu.ai gpt-image-2 持续限流（429）

**表现**：三个 API 端点（yunwu.ai / api3.wai.vip / api.apiplus.org）同时返回 429 或"当前分组上游负载已饱和"。

**根因**：gpt-image-2 走 Azure OpenAI Sweden Central，共享配额池，工作日上午容易饱和。`generate_images_v4.py` 脚本内置重试间隔太短（3秒），快速轮询端点会加剧限流。

**解决方案**：
1. **降级到 gpt-image-1**（推荐）：质量接近，限流阈值更高，且走不同渠道
2. **手动控制请求间隔**：每次请求间隔 **12秒以上**，避免连锁限流
3. **直接调用 API**：用 `config_loader` 加载密钥后直接 `requests.post`，比脚本更可控

---

## 坑2：gpt-image-1 尺寸参数不同于 gpt-image-2

**表现**：`gpt-image-1` 传 `1792x1024` 报错 `Invalid size`。

**gpt-image-1 支持的尺寸**：
- `1024x1024`（正方形）
- `1024x1536`（竖版 2:3）
- `1536x1024`（横版 3:2）← **公众号封面/配图用这个**
- `auto`

**gpt-image-2 支持的尺寸**：
- `1792x1024`（16:9 横版）
- `1024x1792`（9:16 竖版）
- `1024x1024`（正方形）
- `auto`

**教训**：降级模型时必须同步修改 size 参数。

---

## 坑3：FAL_KEY 未配置

**表现**：`image_generate` 工具报错 "FAL_KEY environment variable not set"。

**解决方案**：在 `~/.ai-ggbond-skills/.env` 中添加 `FAL_KEY=your-key`，或继续使用 yunwu.ai API。

---

## 坑4：API Key 被临时封禁

**表现**：多次使用无效令牌后，返回"您多次使用无效令牌，请等待 120 秒后再试"。

**根因**：通过 `execute_code` 工具提取 API Key 时，Hermes 会将密钥脱敏为 `***`，导致传入无效 Key。

**解决方案**：始终在 `terminal` 工具中使用 `config_loader` 加载密钥，不要尝试从输出中提取 Key。

---

## 降级调用模板（gpt-image-1）

```python
import os, requests, base64, time
from config_loader import load_all_env, apply_env_to_os
apply_env_to_os()

api_key = os.environ.get('YUNWU_API_KEY')
url = 'https://yunwu.ai/v1/images/generations'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

def gen_image(prompt, output_path, size='1536x1024'):
    """生成单张图片，自动处理 URL 和 base64 两种响应格式"""
    payload = {
        'model': 'gpt-image-1',
        'prompt': prompt,
        'n': 1,
        'size': size
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=180)
    if resp.status_code != 200:
        print(f'❌ HTTP {resp.status_code}: {resp.text[:200]}')
        return False
    
    data = resp.json()
    img_data = data.get('data', [{}])[0]
    img_url = img_data.get('url', '')
    b64_data = img_data.get('b64_json', '')
    
    if img_url:
        img_resp = requests.get(img_url, timeout=60)
        with open(output_path, 'wb') as f:
            f.write(img_resp.content)
    elif b64_data:
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(b64_data))
    else:
        return False
    return True

# 批量生成时，每次间隔12秒
images = [
    ('prompt1...', 'images/cover.png'),
    ('prompt2...', 'images/infographic.png'),
]
for prompt, path in images:
    if gen_image(prompt, path):
        print(f'✅ {path}')
    time.sleep(12)  # 防限流
```

---

## 端点优先级

| 端点 | 状态 | 备注 |
|------|------|------|
| `https://yunwu.ai` | 主站，限流最严 | gpt-image-2 高峰期不可用 |
| `https://api3.wai.vip` | 国内服务器 | SSL 偶发问题 |
| `https://api.apiplus.org` | CF站 | 超时较多 |

**建议**：默认用 yunwu.ai，失败后等待 12 秒重试，不要快速轮询。
