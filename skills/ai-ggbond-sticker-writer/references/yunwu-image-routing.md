# 云雾生图链路路由与重试策略

## 默认链路池

`generate_sticker_images_v2.py` 默认按顺序尝试三条 Base URL：

1. `https://yunwu.ai`
2. `https://api.apiplus.org`
3. `https://api3.wlai.vip`

图片生成端点默认拼接：`/v1/images/generations`。

可用环境变量覆盖：

```bash
YUNWU_BASE_URLS=https://yunwu.ai,https://api.apiplus.org,https://api3.wlai.vip
YUNWU_IMAGE_ENDPOINT=/v1/images/generations
YUNWU_MAX_RETRIES=3
YUNWU_RETRY_DELAY=8
YUNWU_IMAGE_INTERVAL=20
YUNWU_IMAGE_TIMEOUT=300
```

> 注意：`YUNWU_BASE_URL` / `YUNWU_BASE_URLS` 应填 Base URL，不要带 `/v1/images/generations`。脚本会自动清洗 `/v1`、`/v1/images/generations` 等后缀。

## 代理策略

默认尊重系统代理/VPN，不再强制删除 `HTTP_PROXY` / `HTTPS_PROXY`。

只有明确需要禁用代理时，设置：

```bash
YUNWU_DISABLE_PROXY=1
```

## 429 处理策略

遇到 `HTTP 429` 时，脚本会：

1. 立即切换下一条 Base URL；
2. 一轮链路池都失败后，按指数退避等待；
3. 多张图之间默认等待 `20秒`，避免连续硬冲同一上游。

命令行可临时调整：

```bash
python scripts/generate_sticker_images_v2.py \
  --markdown /path/to/贴图.md \
  --style retro-pop \
  --ratio 16:9 \
  --max-images 4 \
  --image-interval 30
```

## 图片数量控制

Markdown 章节数可能多于用户确认的图片数。必须用 `--max-images` 限制，避免自动为所有章节生图。

示例：用户确认只要4张图：

```bash
python scripts/generate_sticker_images_v2.py \
  --markdown /path/to/贴图.md \
  --max-images 4
```

## 模型选择红线

不要擅自换模型。

- 如果 `gpt-image-2` 返回429：先报告“当前模型/链路负载饱和”，询问是否等待、换端点、还是由用户决定换模型。
- 如果返回敏感词/500：先报告触发问题，建议改提示词或让用户确认是否换模型。
- 如果超时：先报告网络/API超时，建议重试间隔或简化提示词。
