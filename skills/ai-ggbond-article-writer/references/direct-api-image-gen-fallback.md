# 直接 API 调用生成图片 Fallback 方案

当 `generate_images_v4.py` 脚本因超时、依赖缺失或其他原因失败时，使用此方案。

## 前置条件

1. 确保 API Key 配置正确：
   - `~/.ai-ggbond-skills/.env` 或技能目录 `.env` 中有 `YUNWU_API_KEY`
2. Hermes VM 环境需要设置代理：
   ```bash
   export https_proxy=http://127.0.0.1:7897
   export http_proxy=http://127.0.0.1:7897
   ```
3. 安装必要依赖：
   ```bash
   pip3 install requests Pillow
   ```

## 完整流程

### Step 1: 准备 prompt

根据文章内容构建中文 prompt，必须包含：
- 图片类型和比例（如 "16:9横版"）
- 核心内容描述
- 视觉风格要求（手绘风格、莫兰迪色系等）
- 文字要求（"所有文字必须使用简体中文，确保清晰无乱码"）
- 禁止事项（"禁止生成水印、署名、Logo"）

### Step 2: 调用 API

```bash
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
API_KEY=$(cat ~/.ai-ggbond-skills/.env | grep YUNWU_API_KEY | cut -d'=' -f2)

curl -s --max-time 180 -X POST "https://api.openlux.ai/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "YOUR_PROMPT_HERE",
    "size": "1536x1024",
    "n": 1
  }' -o /tmp/img_response.json
```

### Step 3: 解码并保存

```bash
python3 -c "
import json, base64
data = json.load(open('/tmp/img_response.json'))
if 'data' in data and len(data['data']) > 0:
    img_data = base64.b64decode(data['data'][0]['b64_json'])
    open('images/output.png', 'wb').write(img_data)
    print('Image saved successfully')
else:
    print('Error:', data)
"
```

### Step 4: 批量生成

循环执行 Step 2-3，每张图片间隔 15-20 秒：

```bash
for i in 1 2 3 4 5; do
  echo "Generating image $i..."
  # curl 调用 + python 解码
  sleep 20
done
```

## 常见 Pitfall

1. **不要用 `curl | python3` 管道模式**
   - 安全扫描会拦截（HIGH severity warning）
   - API 返回空响应时 JSON 解析会崩溃
   - 必须先保存到文件，再单独解析

2. **API 返回空响应**
   - 原因：prompt 过长、网络超时、API 限流
   - 解决：缩短 prompt、增加超时时间、增加重试间隔

3. **中文文字乱码**
   - 在 prompt 中明确要求："所有文字必须使用简体中文，确保清晰无乱码"
   - 使用结构化网格布局（如"三行表格每行固定单元格"），不用叙述性段落

4. **限流（429 错误）**
   - 等待 15-30 秒后重试，最多 3 次
   - 3 次仍失败则暂停，通知用户

## 与脚本模式的对比

| 对比项 | 脚本模式 | 直接 API 模式 |
|--------|----------|---------------|
| 依赖 | 需要 requests, Pillow | 只需要 curl, python3 |
| 超时 | 可能超时（>300s） | 可控（--max-time） |
| 错误处理 | 脚本内部处理 | 手动检查 JSON 响应 |
| 批量生成 | 自动 | 手动循环 |
| 适用场景 | 依赖齐全、网络稳定 | 脚本失败、依赖缺失、网络受限 |
