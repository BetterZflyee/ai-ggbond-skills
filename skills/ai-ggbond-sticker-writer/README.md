# ai-ggbond-sticker-writer

将输入内容转换为微信贴图/小红书风格图文的完整技能，覆盖：

- 内容整理与去 AI 味改写
- 标题生成与 Markdown 排版
- 信息图风格选择与提示词生成
- 图片批量生成与水印处理

## 目录结构

```text
ai-ggbond-sticker-writer/
├── SKILL.md
├── assets/
│   └── 风格信息图检索.md
├── references/
│   ├── workflow.md
│   ├── styles.md
│   └── troubleshooting.md
├── scripts/
│   ├── sticker_manager.py
│   ├── generate_sticker_images_v2.py
│   └── generate_images.py
├── .env.example
└── evolution.json
```

## 环境准备

1. 复制配置模板：

```bash
cp .env.example .env
```

2. 安装依赖：

```bash
pip install requests Pillow
```

3. 配置云雾环境变量：

```env
YUNWU_API_KEY=sk-8lcvuMcVjtK1RkRpa640NLTzCmg9uIZtqFnviqTOIBwKxstB
YUNWU_BASE_URL=https://yunwu.ai
YUNWU_DEFAULT_MODEL=gpt-image-2
```

## 常用命令

```bash
# 列出风格
python scripts/generate_sticker_images_v2.py --list-styles

# 从 Markdown 生成配图（默认 16:9）
python scripts/generate_sticker_images_v2.py --markdown "demo.md" --style "retro-pop"

# 指定比例与输出目录
python scripts/generate_sticker_images_v2.py --markdown "demo.md" --ratio "1:1" --output-dir "./images"

# 创建标准贴图目录与文案文件
python scripts/sticker_manager.py --title "示例标题" --content "示例内容"
```

## 配置约定

- 默认输出目录：`./wechat_stickers/`
- 可通过 `WECHAT_STICKER_OUTPUT_DIR` 或 `--output-dir` 覆盖
- `YUNWU_DEFAULT_MODEL` 可设置默认生图模型（默认 `gpt-image-2`）

## 参考文档

- 工作流说明：`references/workflow.md`
- 风格决策：`references/styles.md`
- 故障排查：`references/troubleshooting.md`
