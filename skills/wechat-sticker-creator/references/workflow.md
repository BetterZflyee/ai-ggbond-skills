# Workflow

## 目标

把用户输入转成可发布的微信贴图内容与配图产物。

## 标准流程

1. 确认输入来源：总结前序对话或直接使用新输入
2. 执行内容优化：两轮审校 + 去 AI 味
3. 生成标题：提供 3-5 个可选标题
4. 落地文件：创建 `./wechat_stickers/[时间戳-标题]/`
5. 选择风格与比例：优先给出 2-3 个风格建议，默认比例 16:9
6. 生成配图：调用 `scripts/generate_sticker_images_v2.py`

## 产物规范

- Markdown：与文件夹同名
- 图片目录：`images/`
- 提示词文件：`images/prompt.md`

## 执行命令

```bash
python {baseDir}/scripts/sticker_manager.py --title "标题" --content "内容"
python {baseDir}/scripts/generate_sticker_images_v2.py --markdown "./wechat_stickers/xxx/xxx.md"
```
