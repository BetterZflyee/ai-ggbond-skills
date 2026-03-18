---
name: 营销图片生成技能
description: 基于云雾API生成营销图片，支持多端点回退与多种图片比例。
read_when:
  - User asks to generate an image
  - User wants to create visual content
metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["node"],"env":["YUNWU_API_KEY"]},"description":"通过云雾API生成营销图片，使用环境变量中的API Key鉴权。"}}
---

# 营销图片生成技能

通过云雾API生成高质量营销图片，支持云雾多端点自动回退，适用于封面图、活动图、宣传图等快速产出场景。

## Prerequisites

- **YUNWU_API_KEY**: 必须在环境变量中配置。
- **Node.js**: Available in the environment.
- **Security Note**: 不要把API Key写入代码或提交到仓库，请使用环境变量管理。

## Usage

### Direct Script Execution

```bash
/home/ubuntu/clawd/skills/marketing-image-generator/scripts/generate.js \
  --prompt "电商大促主视觉海报，红金配色，立体字体，强烈促销氛围" \
  --output "/tmp/marketing.png" \
  --aspect-ratio "16:9"
```

### Arguments

- `--prompt` (Required): The marketing image description.
- `--output` (Optional): 图片输出路径（默认保存到系统图片目录）。
- `--aspect-ratio` (Optional): `1:1` (default), `16:9`, `9:16`, `4:3`, `3:4`。
- `--model` (Optional): 云雾生图模型（默认 `gpt-image-1`）。
- `--quality` (Optional): 画质等级（默认 `standard`）。

## Output

- The script writes the image to the specified path.
- It prints `MEDIA: <path>` to stdout, which allows Clawdbot to automatically detect and display the image.

## Troubleshooting

- **401/403**: 检查 `YUNWU_API_KEY` 是否正确。
- **429**: 配额达到上限，请稍后重试。
- **No image data found**: 模型拒绝生成或返回结构变化，建议更换提示词或模型。
