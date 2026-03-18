# Troubleshooting

## 常见问题

| 问题 | 排查与修复 |
|---|---|
| 缺少 API Key | 检查 `.env` 是否设置 `YUNWU_API_KEY` |
| 请求地址异常 | 检查 `YUNWU_BASE_URL` 是否为 `https://yunwu.ai` |
| 模型不符合预期 | 检查 `YUNWU_DEFAULT_MODEL` 是否为 `gemini-3.1-flash-image-preview` |
| 生成 429 或超时 | 稍后重试；脚本已支持多端点自动切换 |
| 中文文字乱码 | 使用 `gpt-image-1` 或 `qwen-image-edit-2509` 并加强中文约束 |
| 输出目录不对 | 通过 `WECHAT_STICKER_OUTPUT_DIR` 或 `--output-dir` 指定 |
| 比例不符合预期 | 在提示词开头和结尾都声明比例，并检查 `--ratio` 参数 |

## 环境检查

```bash
python --version
python -c "import requests, PIL; print('ok')"
```

## 最小可用命令

```bash
python scripts/generate_sticker_images_v2.py --list-styles
python scripts/sticker_manager.py --title "测试标题" --content "测试内容"
```
