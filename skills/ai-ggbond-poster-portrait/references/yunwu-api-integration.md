# 云雾API集成指南

## 概述
本skill使用云雾API（Yunwu AI）生成图像，支持多链路自动切换。

## API端点
- 主站：`https://yunwu.ai/v1/images/generations`
- 备用1：`https://api.apiplus.org/v1/images/generations`
- 备用2：`https://api3.wlai.vip/v1/images/generations`

## 配置文件位置
```bash
~/.ai-ggbond-skills/.env
```

**⚠️ Hermes环境注意**：`~` 展开为 `/Users/admin/.hermes/profiles/gongcheng/home`，非 `/Users/admin`。

## 配置内容
```bash
YUNWU_API_KEY=sk-8lc...
YUNWU_BASE_URLS=https://yunwu.ai,https://api.apiplus.org,https://api3.wlai.vip
YUNWU_IMAGE_ENDPOINT=/v1/images/generations
YUNWU_DEFAULT_MODEL=gpt-image-2
YUNWU_MAX_RETRIES=3
YUNWU_RETRY_DELAY=8
YUNWU_IMAGE_TIMEOUT=300
```

## 尺寸对照表
| 比例 | 尺寸 | 适用场景 |
|------|------|----------|
| 9:16 | 1024x1792 | 竖版海报、手机壁纸、小红书 |
| 16:9 | 1792x1024 | 横版海报、桌面壁纸、公众号封面 |
| 1:1 | 1024x1024 | 正方形、朋友圈、头像 |
| 4:5 | 1024x1280 | 竖版、Instagram |
| 3:4 | 1024x1365 | 竖版详细展示 |

## 错误处理
- **429 负载饱和**：自动切换下一条链路，按指数退避等待
- **401 无效令牌**：检查API密钥是否正确
- **500 敏感词**：调整提示词，用职位代替人名
- **超时**：检查网络，增加timeout

## 脚本使用
```bash
# 参数化生成
python3 scripts/generate_portrait.py \
  --scene "场景描述" \
  --style "摄影风格" \
  --clothing "服装描述" \
  --output output.png

# 使用提示词文件
python3 scripts/generate_portrait.py \
  --prompt prompt.txt \
  --output output.png

# 查看可用模型
python3 scripts/generate_portrait.py --list-models
```

## 来源
从 `ai-ggbond-sticker-writer` 的云雾API集成方案适配而来。