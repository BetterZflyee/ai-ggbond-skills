# Session note: PIL fallback for WeChat sticker generation when image APIs/vision fail

## Context
User asked to generate WeChat sticker images for a Karpathy → Anthropic article. The normal cloud image generation route failed with repeated `HTTP 429 当前分组上游负载已饱和` across all configured Yunwu endpoints. The native image generation tool also failed because `FAL_KEY environment variable not set`. Vision analysis of user-provided reference images failed repeatedly with `502`.

## What worked
Use deterministic local image generation with Pillow as a fallback to create acceptable sticker-style JPGs without external image APIs.

### Workflow
1. Save user-provided images into the target `images/` directory with clear sequential names.
2. If `vision_analyze` fails, inspect image dimensions locally with Pillow:
   ```python
   from PIL import Image
   im = Image.open(path)
   print(im.size, im.mode)
   ```
3. Match the user's reference-image canvas size instead of forcing the skill default ratio. In this session both reference images were around `750x670` / `750x644`, so generated stickers used `750x670`.
4. Generate several static JPG cards with Pillow:
   - cream/paper background
   - grid/noise texture
   - folder/archive visual language
   - blue/red annotations
   - rounded cards, labels, arrows
   - Chinese text rendered with system fonts such as `/System/Library/Fonts/PingFang.ttc`
5. Verify outputs by reopening with Pillow and printing size/mode/file size.

### Naming pattern used
Generated images were saved as:
- `03-生成贴图-封面-高手更会翻译.jpg`
- `04-生成贴图-方法论-4个问题.jpg`
- `05-生成贴图-金句-影响力.jpg`
- `06-生成贴图-对比-库存到资产.jpg`

## Pitfalls
- Do not keep retrying `vision_analyze` after repeated 502s; switch to local inspection or ask user to visually review.
- Do not silently change cloud image models after 429; report the issue and ask/obey user preference. But if user still wants images and local deterministic generation can satisfy the task, local Pillow generation is a safe no-model-change fallback.
- The skill's default 16:9 is not always best after user supplies reference images. Match the reference-image dimensions when the user says “结合这两张图”.

## Reusable snippet outline
```python
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out_dir = Path('/Users/admin/SuperIp/stickers/<project>/images')
out_dir.mkdir(parents=True, exist_ok=True)
W, H = 750, 670
im = Image.new('RGB', (W, H), (247,243,232))
d = ImageDraw.Draw(im)
font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 36)
d.text((40, 80), '标题', font=font, fill=(24,28,35))
im.save(out_dir/'03-生成贴图-封面.jpg', quality=95)
```
