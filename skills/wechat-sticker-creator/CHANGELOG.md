# Changelog

## 2.1.0 - 2026-03-09

- 新增 `README.md`，补齐安装、配置、命令和目录说明
- 新增 `references/` 结构，拆分工作流、风格与故障排查文档
- 新增 `.gitignore`，避免提交本地敏感与生成文件
- 优化 `SKILL.md`：
  - 增加 `Script Directory` 与 `References` 段落
  - 修正脚本调用路径为 `{baseDir}/scripts/...`
  - 统一输出目录约定为 `./wechat_stickers/`（支持自定义覆盖）
  - 对齐 V2 脚本默认比例与模型参数说明
- 优化 `scripts/generate_sticker_images_v2.py`：
  - 默认比例改为 `16:9`
  - `--model` 默认读取 `YUNWU_DEFAULT_MODEL`，未配置回退 `gemini-3.1-flash-image-preview`
- 优化 `scripts/sticker_manager.py`：
  - 默认输出目录支持 `WECHAT_STICKER_OUTPUT_DIR`
  - Markdown 文件名与文件夹名保持一致
  - `prompt.md` 比例字段支持按参数写入（默认 `16:9`）
