# Hermes Agent 内置 OpenAI 图片生成配置

## 现状

Hermes Agent 原生支持 gpt-image-2（通过 OpenAI 插件），有三档：
- `gpt-image-2-low`    ~15s 最快
- `gpt-image-2-medium` ~40s 默认
- `gpt-image-2-high`   ~2min 最高质量

## 配置步骤

### 1. 设置 API Key

`~/.hermes/.env`：
```
OPENAI_API_KEY=sk-your-real-key
OPENAI_BASE_URL=http://127.0.0.1:8317/v1   # 如果用代理
```

### 2. 选择后端

`~/.hermes/config.yaml`：
```yaml
image_gen:
  provider: openai
```

### 3. 重启 gateway

```bash
hermes gateway restart
```

## 已知坑

- **OPENAI_API_KEY 不能是 `dummy`**。当前 `.env` 中是占位符，需替换为真实 key。
- **Gateway 不会热加载 `.env`**。修改后必须重启。
- **本地代理 127.0.0.1:8317 支持 gpt-image-2**（2026-05-27 验证通过）。

## 回退方案

如果内置 `image_generate` 工具不可用（FAL_KEY 未设置 / OPENAI_API_KEY 为 dummy），直接用 Python + urllib 调用本地代理：

```python
import json, urllib.request, ssl
req = urllib.request.Request(
    "http://127.0.0.1:8317/v1/images/generations",
    data=json.dumps({"model":"gpt-image-2","prompt":"...","n":1,"size":"1792x1024"}).encode(),
    headers={"Authorization":"Bearer <YUNWU_API_KEY>","Content-Type":"application/json"})
resp = urllib.request.urlopen(req, timeout=300, context=ssl.create_default_context())
```

云雾 API 主站（yunwu.ai）高峰期可能 429，本地代理更稳定。
