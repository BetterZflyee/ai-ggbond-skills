---
name: ai-ggbond-remove-ai-marks
description: 清除 AI 生成图片的水印——可见水印（Gemini火花）、不可见水印（SynthID/C2PA/EXIF）及元数据。基于 wiltodelta/remove-ai-watermarks v0.6.9，深度集成 Python API。当飞哥说"去水印""清除AI标记""洗图""clean watermark"时触发。
version: 1.1.1
license: MIT
---

# AI朱朱侠 — Remove AI Marks

深度集成 [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) v0.6.9，通过内置 Python 脚本直接调用 GeminiEngine / InvisibleEngine / metadata cleaner，不依赖 CLI。对接 `ai-ggbond-article-writer` 和 `ai-ggbond-sticker-writer`，配图管线自动清除水印。

---

## 架构

```
飞哥配图管线
  ├─ ai-ggbond-article-writer（生图）
  ├─ ai-ggbond-sticker-writer（贴图）
  └─ ai-ggbond-remove-ai-marks（洗图）★
       ├─ scripts/clean.py        ← 单张清洗（Python API）
       ├─ scripts/batch_clean.py  ← 批量扫描+清洗
       └─ 底层：remove-ai-watermarks 库
            ├─ GeminiEngine       ← 可见水印（Alpha 反算）
            ├─ InvisibleEngine    ← 不可见水印（扩散重生成）
            └─ noai.cleaner       ← 元数据剥离（C2PA/EXIF/XMP）
```

---

## 快速使用

### 单张清洗

```bash
# 全清（可见 + 不可见 + 元数据）⭐最常用
python3 scripts/clean.py input.png -o clean.png

# 仅可见水印（Gemini 火花，CPU，~0.05s）
python3 scripts/clean.py input.png --visible-only

# 仅元数据（C2PA/EXIF，不碰像素）
python3 scripts/clean.py input.png --metadata-only

# 识别水印结构
python3 scripts/clean.py input.png --identify --json

# 加胶片颗粒对抗 AI 检测
python3 scripts/clean.py input.png --humanize 4.0
```

### 批量处理

```bash
# 扫描目录
python3 scripts/batch_clean.py ./images/ --dry-run

# 执行清洗
python3 scripts/batch_clean.py ./images/

# 输出到指定目录
python3 scripts/batch_clean.py ./images/ --output-dir ./clean/

# 原地替换（直接覆盖原图）⭐「直接替换掉」
# batch_clean.py 不支持原地覆盖 → 先输出到临时目录再 cp 回
python3 scripts/batch_clean.py ./images/ --output-dir /tmp/clean-tmp/
cp /tmp/clean-tmp/*.png ./images/
python3 scripts/batch_clean.py ./images/ --dry-run  # 验证
rm -rf /tmp/clean-tmp/
```

---

## Python API（内置）

```python
# 在技能脚本中直接调用
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".local/share/uv/tools/remove-ai-watermarks/lib/python3.10/site-packages"))

from remove_ai_watermarks.gemini_engine import GeminiEngine       # 可见水印
from remove_ai_watermarks.invisible_engine import InvisibleEngine # 不可见水印
from remove_ai_watermarks.noai.cleaner import remove_ai_metadata, has_ai_content  # 元数据
```

---

## 配图管线集成

### 文章配图 → 自动洗图

```
generate_images_v4.py 生图
  → 写入 images/ 目录
  → batch_clean.py --dry-run 扫描
  → batch_clean.py 清洗有水印的图
  → 发布到公众号
```

### 一键管线（推荐）

```bash
# 生图 + 洗图 + 质检 一键完成
python3 scripts/generate_images_v4.py --article 文章.md  # 生图
python3 scripts/batch_clean.py 文章目录/images/           # 洗图
# → 配图已干净，直接发布
```

### 贴图管线

```bash
# sticker-writer 输出 → 批量洗图 → 发布
python3 scripts/batch_clean.py ~/SuperIp/stickers/20250527/
```

---

## 支持的水印矩阵

| 来源 | 可见 | 不可见 | 元数据 | 清除引擎 |
|------|------|--------|--------|----------|
| **Gemini / Nano Banana** | ✅ 火花 | ✅ SynthID v1+v2 | ✅ C2PA | GeminiEngine + InvisibleEngine |
| **gpt-image-2** | — | ⚠️ 像素水印 | ✅ C2PA | InvisibleEngine + metadata |
| **DALL·E 3** | — | — | ✅ C2PA | metadata |
| **Stable Diffusion** | — | ✅ DWT-DCT | ✅ PNG chunks | InvisibleEngine + metadata |
| **FLUX** | — | ✅ DWT-DCT | ✅ C2PA | InvisibleEngine + metadata |
| **Midjourney** | — | — | ✅ EXIF/XMP | metadata |
| **Firefly** | — | — | ✅ C2PA | metadata |
| **Microsoft Designer** | — | ✅ SynthID | ✅ C2PA | metadata |

---

## 飞哥场景决策

| 场景 | 命令 |
|------|------|
| Gemini 生的图 | `python3 scripts/clean.py img.png -o clean.png`（全清） |
| gpt-image-2 配图 | `python3 scripts/clean.py img.png --metadata-only`（C2PA 剥离即可） |
| 不确定来源 | `python3 scripts/clean.py img.png --identify` 先查 |
| 文章配图目录 | `python3 scripts/batch_clean.py images/ --dry-run` → 确认 → 执行 |
| 发帖前安全检查 | `python3 scripts/batch_clean.py images/ --dry-run --json` |
| 对抗 AI 检测 | `python3 scripts/clean.py img.png --humanize 4.0` |

---

## 安装

```bash
# 已完成（飞哥环境）
uv tool install git+https://github.com/wiltodelta/remove-ai-watermarks.git

# 更新
uv tool upgrade remove-ai-watermarks

# GPU 支持（不可见水印清除）
uv tool install git+https://github.com/wiltodelta/remove-ai-watermarks.git --with 'remove-ai-watermarks[gpu]'
```

---

## 环境

- Python 3.10+ ✅
- 可见水印：CPU ~0.05s/张
- 不可见水印：需 `[gpu]` + ~2GB 模型（首次下载）
- macOS MPS：有限支持，大图建议 `--device cpu`

---

## 元数据剥离 PIL 兜底（2026-06-09 实测有效）

当 `remove-ai-watermarks` 库未安装或 `cv2` 缺失时，用 PIL 重新保存图片即可剥离 C2PA/EXIF/XMP 元数据：

```python
from PIL import Image
from pathlib import Path

img_path = Path("input.png")
img = Image.open(img_path)
clean = Image.new(img.mode, img.size)
clean.putdata(list(img.getdata()))
clean.save(img_path, "PNG")  # 原地覆盖
```

**原理**：`putdata()` 只复制像素数据，不复制元数据块。重新保存为 PNG 时生成全新的干净文件头。

**限制**：
- ✅ 有效：C2PA、EXIF、XMP、PNG chunks
- ❌ 无效：可见水印、像素级隐写水印（需要 InvisibleEngine）
- ⚠️ 文件大小会略有变化（元数据被移除）

**批量处理**：

```python
from PIL import Image
from pathlib import Path

for p in Path("./images").glob("*.png"):
    img = Image.open(p)
    clean = Image.new(img.mode, img.size)
    clean.putdata(list(img.getdata()))
    clean.save(p, "PNG")
    print(f"  Cleaned: {p.name}")
```

## 注意事项

- **gpt-image-2 配图**：默认无水印，仅 C2PA 元数据 → `--metadata-only` 足够
- **Gemini 配图**：必有火花标志 → 必须 `clean.py` 全清
- **不可见水印清除会微改像素**：扩散重生成 strength 0.05，肉眼不可见但 MD5 会变
- **首次运行下载模型**：`InvisibleEngine` 首次触发会下载 ~2GB 权重
- **脚本路径**：技能 scripts/ 下的脚本已在 Hermes 中可用，直接 `python3 scripts/clean.py` 即可
- **`--metadata-only` 不指定 `-o` 时**：输出文件名为 `input_clean.png`（添加 `_clean` 后缀），不会原地覆盖。需要原地替换时先 `-o` 指定同名或事后 `mv`
- **清洗后验证**：重新跑 `--identify --json` 确认 `visible/metadata/gemini_confidence` 三项全绿
- **`batch_clean.py` 默认输出到 `clean/` 子目录**，不会原地覆盖。飞哥说「直接替换掉」时，走临时目录+cp回覆盖流程（见上方批量处理-原地替换）
- **首次运行 clean.py 可能因脚本 bug 全部失败**：检查 `import cv2` 是否存在、`clean_all()` 中 `img = cv2.imread()` 和 `tmp_path`→`tmp` 是否正确（v1.1.0 → v1.1.1 已修复）

## 典型工作流（以本次会话为例）

```bash
# 1. 先识别
python3 scripts/clean.py img.png --identify --json
# → {"visible": false, "metadata": true, "gemini_confidence": 0.16}

# 2. 有元数据→剥离
python3 scripts/clean.py img.png --metadata-only
# → 输出 img_clean.png

# 3. 替换原图
mv img_clean.png img.png

# 4. 再次验证
python3 scripts/clean.py img.png --identify --json
# → {"visible": false, "metadata": false, "gemini_confidence": 0.16}  ✅
```
