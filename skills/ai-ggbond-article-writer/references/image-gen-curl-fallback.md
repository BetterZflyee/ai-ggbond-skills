# 图片生成 curl 直接调用模式

## 场景
当 `generate_images_v4.py` 脚本卡住或超时时，直接用 curl 调用云雾 API。

## 两步法

### 第一步：curl 获取 base64 响应
```bash
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
API_KEY=$(cat /path/to/.env | grep YUNWU_API_KEY | cut -d'=' -f2)

curl -s --max-time 180 -X POST "https://yunwu.ai/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "图片描述...",
    "size": "1536x1024",
    "n": 1
  }' -o response.json
```

### 第二步：Python 解码 base64 保存图片
```bash
python3 -c "
import json, base64
data = json.load(open('response.json'))
img_data = base64.b64decode(data['data'][0]['b64_json'])
open('output.png', 'wb').write(img_data)
print('saved')
"
```

## 关键参数
- **size**: `1536x1024` (16:9), `1024x1024` (1:1), `1024x1536` (3:4)
- **model**: `gpt-image-2`（默认，中文渲染最佳）
- **timeout**: 建议 180 秒

## 注意事项
- 管道方式 (`curl | python3`) 有时会因安全检查被阻断
- 两步法（先保存 JSON 再解码）更稳定
- 每张图之间建议间隔 10-15 秒避免限流
- 生成后用 PaddleOCR 检查中文文字质量
