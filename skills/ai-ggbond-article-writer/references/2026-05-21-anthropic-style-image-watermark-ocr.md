# 2026-05-21 配图风格、水印与 PaddleOCR 质检复盘

## 场景
为公众号文章《我越来越确定：AI 工具的下一站，不是更聪明，而是接管工作流》生成 7 张配图。初版为科技蓝信息图，用户反馈“不讨喜”，要求改成 Anthropic 官网气质的暖色科技风。

## 关键用户纠偏

1. **风格纠偏**
   - 不要默认科技蓝。
   - 用户明确要求“Anthropic 网站上的配色和风格”。
   - 实操定义：暖米白/羊皮纸底色、深炭黑文字、陶土橙/赭石棕/鼠尾草绿/暖灰辅助色，高留白、克制、学术感、可信感。

2. **水印纠偏**
   - 不要让图像模型在画面中额外画水印、署名、Logo、角标或“AI朱朱侠”。
   - 只保留代码后期加的水印。
   - 水印位置：右上角。
   - 第一版大水印用户反馈：实际效果不像预期“透明圆角框”，反而像一个很大的黑体字，抢主体注意力。
   - **当前用户确认的更稳妥水印设置**：封面 ratio≈0.0325，正文图 ratio≈0.0275；文字透明度 50%（RGBA alpha=128）；不画圆角底框，只叠加半透明深炭黑文字。
   - 圆角底框不是硬性要求；如果出现贴纸感、黑体字过重、压主体，优先取消底框并降低字号/透明度。
   - 旧方案 B（封面 6.5%、正文 5.5%、半透明暖白圆角底 + 深炭黑文字）仅作为历史记录，不再默认使用。

3. **OCR 质检纠偏**
   - 用户已安装 PaddleOCR，后续生成图片后优先用 PaddleOCR 做中文文字识别质检。
   - OCR 结果不能机械等同于图片错误；部分图标/装饰会被 OCR 误识别。要结合语义判断：标题/关键标签/金句错字是硬伤，图标噪声可忽略。

## Anthropic 风格提示词片段

```text
Anthropic 官网气质的高级科技信息图风格：温暖极简、学术感、低饱和、高留白；不要科技蓝。主背景为暖米白/羊皮纸色 #F7F1E8 或 #F4EFE7，主文字深炭黑 #2B2723，辅助色使用陶土橙 #C15A3A、赭石棕 #8A5A44、鼠尾草绿 #7A8B6F、暖灰 #D8CFC3。整体像 Anthropic/Claude 官网的克制、高级、可信风格。使用细线框、圆角卡片、网格、流程箭头、抽象几何、简洁图标。信息密度高但排版必须有秩序、有留白、不能拥挤。所有中文必须大而清晰，尽量使用短标签，绝对禁止乱码、拼音、变形字、重影。禁止生成英文水印、Logo、角标、作者名、“AI朱朱侠”；品牌水印只由后期代码统一添加。
```

## 代码水印推荐函数参数（当前默认）

用户最新纠偏后，默认采用“低存在感文字水印”：

```python
# 封面 ratio=0.0325，正文 ratio=0.0275
# text alpha=128，约 50% 透明度
font_size = max(24, int(img_height * ratio))
margin_x = max(24, int(img_width * 0.02))
margin_y = max(18, int(img_height * 0.02))
x = img_width - text_width - margin_x
y = margin_y
ImageDraw.Draw(img).text((x, y), watermark_text, font=font, fill=(35, 31, 28, 128))
```

如果未来用户重新要求“标签感/角标感”，才考虑恢复圆角底框；默认不要加底框。

历史大水印方案（不再默认）：封面 ratio=0.065，正文 ratio=0.055，`background_fill=(245,239,230,165)`，`text_fill=(35,31,28,235)`。


## PaddleOCR 质检命令

从 `paddleocr-text-recognition` skill 根目录执行：

```bash
uv run scripts/ocr_caller.py --file-path "/absolute/path/to/image.png" --stdout --pretty
```

批量检查示例：

```bash
for f in cover.png infographic.png 02-tool-vs-platform.png 03-copilot-vs-agent.png 04-agent-runtime-architecture.png 05-control-and-quota.png 06-workflow-assets.png; do
  echo "=== $f ==="
  uv run scripts/ocr_caller.py --file-path "/path/to/images/$f" --stdout --pretty \
    | python -c 'import sys,json; d=json.load(sys.stdin); print("OK=", d.get("ok")); print(d.get("text") or "[NO TEXT]")'
done
```

## 质检判断规则

- 标题、核心标签、金句出现错字：重生或局部重做。
- OCR 识别出 `</>`、`O`、`白`、`占` 等图标噪声：先肉眼判断，不直接判错。
- `AI/Al` 混淆：如果来自模型内生水印，必须禁止模型水印；如果来自代码水印，检查字体与 OCR，不一定是视觉错误。
- 信息密度越高，小字越容易错；重生时应减少小字，保留 4–6 个大标签 + 图形结构。

## 安全处理

不要用 `rm` 删除旧图；将旧图移动到归档目录，例如：

```bash
mkdir -p images/archive-blue-v1
mv images/*.png images/archive-blue-v1/
```
