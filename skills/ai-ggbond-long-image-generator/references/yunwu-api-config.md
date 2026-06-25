# 云雾 API 图片生成配置指南

## 配置方法（必须用 hermes config set）

config.yaml 有安全写保护，不能直接 patch，必须用 CLI：

```bash
hermes config set image_gen.provider openai
hermes config set image_gen.model gpt-image-2
hermes config set image_gen.base_url https://yunwu.ai/v1
hermes config set image_gen.api_key 实际的key
```

## API Key 来源

Key 存储位置优先级：
1. `~/.hermes/config.yaml` → `image_gen.api_key`（image_generate 工具读取这个）
2. `~/.ai-ggbond-skills/.env` → `YUNWU_API_KEY`（贴图/海报 skill 的脚本读取这个）

⚠️ 两个位置的 key 可能不同！image_generate 工具只读 config.yaml 的 image_gen.api_key。

## 多链路（自动切换）

```
YUNWU_BASE_URLS=https://yunwu.ai,https://api.apiplus.org,https://api3.wlai.vip
```

贴图 skill 的脚本支持多链路自动切换。脚本会自动清洗 `/v1`、`/v1/images/generations` 等后缀。

## 模型选择

| 模型 | 特点 |
|------|------|
| gpt-image-2 | 默认推荐，中文支持最佳 |
| gpt-image-1 | 上一代，稳定 |
| gemini-3.1-flash-image-preview | 高质量 |
| gemini-2.5-flash-image | 快速 |
| dall-e-3 | OpenAI 原生 |
| flux-1.1-pro | 高质量快速 |

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `Incorrect API key provided: dummy` | api_key 未设置或为 dummy | `hermes config set image_gen.api_key 实际key` |
| `无效的令牌` (401) | API key 过期/无效 | 到 https://yunwu.ai 重新生成 key |
| `该令牌无权访问模型` (403) | Key 有效但无特定模型权限 | 检查云雾后台的模型权限，换模型或升级套餐 |
| `多次使用无效令牌` (429) | 频繁失败触发限流 | 等待 120 秒后重试 |
| `no plugin registered that name` | provider 设为 custom | `hermes config set image_gen.provider openai` |
| Key 长度只有 13 字符 | execute_code 中长字符串被截断 | 改用 terminal + 文件写入方式传递 key |

## 尺寸限制（GPT-Image-2）

- 1024x1024（正方形）
- 1024x1536（竖图，适合小红书）
- 1536x1024（横图）
- auto（自动选择）

超长图需要分段生成 + 拼接。

## API Key 截断问题（重要）

**现象：** 在 `execute_code` 中直接写长 API Key 字符串时，56 字符的 key 可能只收到 13 字符。

**原因：** execute_code 工具对超长字符串有截断处理。

**更广泛的问题：** 截断不仅发生在 execute_code，还发生在：
- `terminal` 命令中的变量赋值（`KEY='sk-xxx'` 也会被截断）
- `write_file` 工具（自动替换为 `***`）
- `hermes config set image_gen.api_key <key>` 命令（长 key 可能无法通过此方式设置）

**最终解决方案：** 用户必须手动在终端运行 `hermes config set` 命令：
```bash
hermes config set image_gen.api_key 用户的完整key
hermes config set image_gen.base_url https://yunwu.ai/v1
hermes config set image_gen.model gpt-image-2
```

**读取时的正确方式：** 从 config.yaml 读取（这个路径不截断）：
```python
import yaml
with open('/Users/admin/.hermes/profiles/gongcheng/config.yaml') as f:
    config = yaml.safe_load(f)
api_key = config['image_gen']['api_key']
```

⚠️ 不要试图通过 agent 工具传递完整 API Key，系统安全机制会自动隐藏/截断敏感信息。这是设计行为，不是 bug。

## 直接调用 API（绕过 image_generate 工具）

当 `image_generate` 工具报 dummy key 时，在 execute_code 中直接调用云雾 API：

```python
import yaml, requests, base64
from PIL import Image
from io import BytesIO

# 读取配置
with open('/Users/admin/.hermes/profiles/gongcheng/config.yaml') as f:
    config = yaml.safe_load(f)
ig = config['image_gen']

# 调用 API
response = requests.post(
    f'{ig["base_url"]}/images/generations',
    headers={'Authorization': f'Bearer {ig["api_key"]}', 'Content-Type': 'application/json'},
    json={'model': 'gpt-image-2', 'prompt': 'your prompt', 'n': 1, 'size': '1024x1536', 'quality': 'high'},
    timeout=120
)

# 处理响应
if response.status_code == 200:
    data = response.json()['data'][0]
    if 'b64_json' in data:
        img = Image.open(BytesIO(base64.b64decode(data['b64_json'])))
    elif 'url' in data:
        img = Image.open(BytesIO(requests.get(data['url']).content))
    img.save('output.png')
else:
    error = response.json().get('error', {})
    print(f'Error {response.status_code}: {error.get("message", "")}')
```

## 参考

贴图 skill 中的完整配置示例：`~/.hermes/profiles/gongcheng/skills/creative/ai-ggbond-sticker-writer/.env.example`
海报 skill 中的集成文档：`~/.hermes/profiles/gongcheng/skills/creative/ai-ggbond-poster-portrait/references/yunwu-api-integration.md`
