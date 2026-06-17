# 生图脚本故障与手动 API 回退方案

## 背景

`generate_images_v4.py` 脚本可能因缺少依赖或网络问题失败。手动调用 yunwu.ai API 是可靠的回退方案。

## 常见故障

### 1. 缺少 Python 依赖

```bash
# ModuleNotFoundError: No module named 'requests'
pip3 install requests

# ModuleNotFoundError: No module named 'PIL'
pip3 install Pillow
```

注意：Hermes VM 环境可能需要通过代理安装：
```bash
export https_proxy=http://127.0.0.1:7897 && pip3 install requests Pillow
```

### 2. 脚本超时

`generate_images_v4.py` 生成 7+ 张图片时可能超过默认超时（300s）。解决方案：
- 使用 `background=true, notify_on_complete=true` 后台运行
- 或手动调用 API 逐张生成

## 手动 API 回退方案

### 配置

```bash
# API 配置位置
~/.ai-ggbond-skills/.env  # 用户级
{skill_dir}/.env           # 技能级

# 内容
YUNWU_API_KEY=your-key
YUNWU_BASE_URL=https://yunwu.ai
YUNWU_DEFAULT_MODEL=gpt-image-2
```

### 生成单张图片

```bash
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897

API_KEY=$(cat ~/.ai-ggbond-skills/.env | grep YUNWU_API_KEY | cut -d'=' -f2)

curl -s --max-time 180 -X POST "https://yunwu.ai/v1/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "图片描述...",
    "size": "1536x1024",
    "n": 1
  }' -o response.json

# 解码 base64 并保存
python3 -c "import json, base64; data = json.load(open('response.json')); open('output.png', 'wb').write(base64.b64decode(data['data'][0]['b64_json']))"
```

### ⚠️ 踩坑

1. **base64 解码管道问题**：`curl | python3` 管道在 Hermes 沙箱中可能被安全扫描拦截。改为 `-o response.json` 再单独处理。

2. **代理导致 socket 断连**：微信 API 和图片 API 需要不同的代理策略。图片 API 走 Clash(7897)，微信 API 走 tinyproxy(100.117.255.36:8888)。

3. **每张图耗时**：gpt-image-2 约 60-90 秒/张，7 张全量约 10-15 分钟。

## 图片压缩

推送到微信前必须压缩到 <500KB（推荐 50-100KB）：

```python
from PIL import Image
import os

for f in os.listdir('.'):
    if f.endswith('.png'):
        img = Image.open(f)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        max_w = 1600 if 'cover' in f else 1200
        w, h = img.size
        if w > max_w:
            img = img.resize((max_w, int(h * max_w / w)), Image.LANCZOS)
        img.save(f.replace('.png', '.jpg'), 'JPEG', quality=75, optimize=True)
```
