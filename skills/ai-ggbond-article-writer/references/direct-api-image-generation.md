# 直接调用云雾 API 生图（当脚本依赖缺失时）

## 场景
`generate_images_v4.py` 缺少依赖（requests/PIL）或网络问题导致无法运行时，直接用 curl 调用 API。

## API 调用模板
```bash
export https_proxy=http://127.0.0.1:7897 && \
export http_proxy=http://127.0.0.1:7897 && \
API_KEY=$(cat ~/.hermes/profiles/neirong/skills/creative/ai-ggbond-article-writer/.env | grep YUNWU_API_KEY | cut -d'=' -f2) && \
curl -s --max-time 180 -X POST "https://api.openlux.ai/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "图片描述...",
    "size": "1536x1024",
    "n": 1
  }' -o /path/to/response.json && \
python3 -c "import json, base64; data = json.load(open('/path/to/response.json')); img_data = base64.b64decode(data['data'][0]['b64_json']); open('/path/to/output.png', 'wb').write(img_data); print('saved')"
```

## Pitfall
1. **必须设代理**：yunwu.ai 需要代理才能访问
2. **超时设置**：生图需要 60-120 秒，`--max-time 180`
3. **先保存响应再解码**：不要用管道（`curl | python3`），JSON 解析会失败
4. **API Key 路径**：`~/.hermes/profiles/neirong/skills/creative/ai-ggbond-article-writer/.env`

## 依赖安装
```bash
export https_proxy=http://127.0.0.1:7897 && \
pip3 install requests Pillow
```
