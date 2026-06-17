# 绕过 generate_sticker_images_v2.py 直接调 API + OCR 验证

## 问题

`generate_sticker_images_v2.py` 的 ContentAnalyzer 从 Markdown 标题/内容自动生成泛化提示词（如 "AI普惠时代" "驱动因素"），
**完全忽略** `images/prompt.md` 中的自定义提示词。导致图片与贴图文案严重脱节。

## 解决方案：直接 API 调用

```python
import os, base64, time, requests

# 读取 API key
api_key = os.environ.get("YUNWU_API_KEY", "")
if not api_key:
    config_path = os.path.expanduser("~/.ai-ggbond-skills/.env")
    if os.path.exists(config_path):
        for line in open(config_path):
            if line.startswith("YUNWU_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break

# 自定义提示词（必须包含 Markdown 中的所有数据点）
prompt = """复古波普网格风格，16:9，简体中文...
[贴图1对应：MiMo 99% / DeepSeek 75% / Qwen 全球第二 / 金句]
[贴图2对应：一分钱续费 / 百亿用户 / 锁客策略]
"""

endpoints = [
    "https://yunwu.ai/v1/images/generations",
    "https://api.apiplus.org/v1/images/generations",
    "https://api3.wlai.vip/v1/images/generations",
]

for endpoint in endpoints:
    for attempt in range(3):
        resp = requests.post(endpoint,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-image-2", "prompt": prompt, "n": 1, "size": "1792x1024"},
            timeout=180)
        if resp.status_code == 200:
            img_data = resp.json()["data"][0]
            if "b64_json" in img_data:
                with open("output.png", "wb") as f:
                    f.write(base64.b64decode(img_data["b64_json"]))
            elif "url" in img_data:
                img_resp = requests.get(img_data["url"], timeout=60)
                with open("output.png", "wb") as f:
                    f.write(img_resp.content)
            sys.exit(0)
        elif resp.status_code == 429:
            time.sleep(15 * (attempt + 1))
```

## 验证方法

生成后用 PaddleOCR 提取图片文字，逐项核对：

| 核对项 | 来源 |
|--------|------|
| 标题 | 与 md 的 H1 一致 |
| 品牌名/产品名 | MiMo 2.5 Pro / DeepSeek / Qwen 3.7 Max |
| 数据 | 99% / 80% / 75% / 百亿 / 一分钱 |
| 金句 | 与 md 底部加粗句一致 |
| 🔴 #标签 | 配图中不应出现，标签只放 Markdown 正文 |

核对不通过 → 调整提示词重新生成。

## 提示词铁律

1. **不写标签**：`#小米 #AI价格战` 这类标签绝不能出现在配图提示词中，只放 Markdown 正文末尾
2. **精确数据原文直传**：品牌名、百分比、金额必须原样写入提示词

## 适用场景

- 贴图包含精确数据（百分比、品牌名、金额）
- 贴图内容是系列化的具体案例（非泛泛主题）
- 用户反馈 "图文不符" 后重做
