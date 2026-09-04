# 图片生成 API 路由与故障处理（2026-05-27 实战）

## 可用节点

| 节点 | URL | 状态 | 备注 |
|------|-----|------|------|
| 云雾主站 | `https://api.openlux.ai` | 高峰期 429 | 上游负载饱和时返回"当前分组上游负载已饱和" |
| 云雾国内 | `https://api3.wai.vip` | SSL 错误 | `UNEXPECTED_EOF_WHILE_READING`，不可靠 |
| 云雾 CF | `https://api.openlux.ai` | 403 | Cloudflare 拦截 |
| **本地代理** ⭐ | `http://127.0.0.1:8317/v1` | ✅ 可用 | 飞哥本地 gpt-image-2 代理，通过 Yunwu API Key 认证 |

## 推荐流程

1. **优先用本地代理** `http://127.0.0.1:8317/v1/images/generations`，`Authorization: Bearer <YUNWU_API_KEY>`
2. 本地代理不可用时，尝试云雾主站（等待 30s 重试，最多 3 次）
3. 3 次 429 后 → 暂停，通知用户

## Hermes 内置 image_generate 工具

- 默认后端：FAL（需要 `FAL_KEY`）
- OpenAI 后端：需要 `OPENAI_API_KEY`（真实 key，不能是 `dummy`）+ `OPENAI_BASE_URL`
- 配置位置：`~/.hermes/config.yaml` 的 `image_gen.provider: openai`
- **已知限制**：`OPENAI_API_KEY=dummy` 时返回 401。此时跳过内置工具，直接用 curl 调本地代理。

## 本地代理 curl 生图模板（⭐实测可用）

```bash
YUNWU_KEY=$(grep YUNWU_API_KEY ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '"')

curl -s http://127.0.0.1:8317/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $YUNWU_KEY" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "你的提示词",
    "n": 1,
    "size": "1792x1024",
    "response_format": "b64_json"
  }' | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
b64 = data['data'][0]['b64_json']
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(b64))
print('saved')
"
```

**批量生成技巧**：多张图用后台进程并行发起，每张间隔 3 秒避免限流：
```bash
curl ... & sleep 3
curl ... & sleep 3
curl ... &
wait
```

## 尺寸限制

本地代理 gpt-image-2 最小像素预算：不能使用 `512x512`，至少 `1024x1024` 以上。
推荐尺寸：`1792x1024`（16:9 横版）、`1792x768`（2.35:1 封面）。

## 生图耗时

gpt-image-2 每张约 50-170 秒，取决于 prompt 复杂度。批量生成时逐张调用，间隔 3 秒。

## 中文质检

- 视觉分析工具 502 时，切 PaddleOCR 做文字识别
- OCR 发现核心标签/标题有错字或乱码→单张重生，不整批返工
- 重生时降低文字密度，保留 3-5 个大标签
