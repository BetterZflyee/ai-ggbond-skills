---
name: ai-ggbond-image-gen
description: 用 GPT-Image-2 (OpenLux) 做通用内容生图与图片编辑。
version: 1.0.0
author: AI朱朱侠
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [image, gpt-image-2, infographic, content-image, api]
    category: creative
    related_skills: [ai-ggbond-sticker-writer, ai-ggbond-long-image-generator, ai-ggbond-poster-portrait, ai-ggbond-remove-ai-marks]
---

# AI朱朱侠 GPT-Image-2 通用内容生图

从 `ai-ggbond-sticker-writer` 独立出来的**通用生图内核**。本技能不处理微信文案/贴图排版/小红书标题/去AI味文章，只负责一件事：**用 GPT-Image-2（OpenLux 链路）把内容变成高质量图片，并做质检交付**。

## 与其它技能的边界

| 技能 | 分工 |
|------|------|
| **ai-ggbond-image-gen（本技能）** | 生图能力本身：文生图、图生图编辑、风格库、中文提示词、质检 |
| ai-ggbond-sticker-writer | 微信贴图文案 + 排版 + 标签 + 小红书标题，内部调用生图 |
| ai-ggbond-long-image-generator | 超长图分段拼接、尺寸预设（1:1~超长） |
| ai-ggbond-poster-portrait | 女性肖像海报专用 |
| ai-ggbond-remove-ai-marks | 去水印/元数据 |

## 核心链路（OpenLux，已实测 2026-09）

- Base URL：`https://api.openlux.ai/v1`
- 文生图：`POST /v1/images/generations`
- 图生图/编辑：`POST /v1/images/edits`（multipart，字段 `image` + `prompt`，**不要传 `format`** —— OpenLux 会报 `Unknown parameter: 'format'`）
- 模型：`gpt-image-2`（`gpt-image-2-c` 也在模型列表，默认用 `gpt-image-2`）
- 旧域名 `yunwu.ai` / `api.apiplus.org` / `api3.wlai.vip` 均已迁移，**不要再调用**

## API Key 来源（脚本自动解析）

优先级：

1. 环境变量 `YUNWU_API_KEY` / `OPENAI_API_KEY`
2. `~/.ai-ggbond-skills/.env` 中 `YUNWU_API_KEY`
3. `~/.hermes/profiles/*/config.yaml` 与 `~/.hermes/config.yaml` 中 `image_gen.api_key` + `image_gen.base_url`

**⚠️ Key 安全铁律**：长 Key 由 Agent 工具传递会被截断/掩码。设置 Key 必须由用户在终端手动编辑 `config.yaml` 或 `.env`，不要让 Agent 通过 write_file/execute_code 写入完整 Key。

## 快速使用

```bash
# 文生图
python3 scripts/image_gen.py --prompt "..." --style tech-neon --ratio 16:9 -o out.png

# 自定义尺寸 / 模型 / 质量
python3 scripts/image_gen.py --prompt "..." --size 1536x1024 --quality high --model gpt-image-2 -o out.png

# 图生图编辑（修错字 / 局部修改 / 重绘区域）
python3 scripts/image_gen.py --edit --image input.png --prompt "只把第6项的 import reqestb 改成 import requests" -o fixed.png

# 使用自定义 raw prompt（不套风格模板）
python3 scripts/image_gen.py --raw --prompt "你的完整提示词" --size 2160x3840 --quality high -o big.png
```

可用风格：`--style` 传入风格名（见下方）。

## 风格库

| 风格代码 | 名称 | 密度 | 适合 |
|---------|------|------|------|
| `high-density` | 高密度信息大图 | high | 干货/数据/拆解 |
| `retro-pop` | 复古波普网格 | medium | 对比/清单/工具 |
| `folder` | 文件夹档案 | medium | 方法论/流程 |
| `receipt` | 打印热敏纸 | medium | 步骤/教程 |
| `vintage-journal` | 复古手帐 | low | 经验/故事 |
| `vector-illustration` | 矢量插图 | medium | 概念/教育 |
| `tech-neon` | 科技风(深蓝霓虹) | high | AI/工具/技术 |
| `editorial-notes` | 技术杂志/编辑手帐 | medium | 去AI味的技术长图 |

> 风格只是 prompt 模板辅助。需要精确排版/中文信息图时，更推荐 `--raw` 手写结构化提示词（见 `references/chinese-grid-strategy.md`）。

## 中文提示词铁律（信息图场景）

1. **结构化网格 > 叙述段落**：显式描述网格/单元格/边框（"左侧30%上下两卡"），模型按格子渲染中文成功率大幅提升
2. **短标签策略**：中文标签 2-4 字，越长越易乱码
3. **数据原文直传**：品牌名、百分比、金额必须原样进 prompt
4. **#标签不上图**：`#标签` 只属于 Markdown 正文
5. **不擅自换模型**：默认 gpt-image-2；遇到 429/错误先报告，等用户决定
6. **比例反复强调**：16:9 / 9:16 / 1:1 必须在 prompt 开头和结尾重复

详见 `references/chinese-grid-strategy.md` 与 `references/prompt-method.md`。

## 质检门禁（每次生图必做）

1. **文件真实存在**：图片非空、尺寸正确（`sips -g pixelWidth -g pixelHeight` 或 PIL）
2. **中文无乱码/无错字**：用 `vision_analyze` 逐字抄录核对；不行用 PaddleOCR
3. **比例正确**：输出符合目标比例；不符合则重做或裁切（裁切前确认安全区）
4. **无额外文字/水印/Logo**：参照 `ai-ggbond-remove-ai-marks` 清洗
5. **交付用 MEDIA:**：`MEDIA:/绝对路径/文件`，并核实文件真实存在再报告成功

**连续 3 次中文乱码 → 停止重试**，向用户提供 prompt 让其自行生成或授权换模型，不要反复烧 token。

## 使用工作流

1. 确认需求：内容类型（信息图/海报/概念图/编辑图）、风格、比例、数量
2. 编写 prompt：风格库模板 或 `--raw` 结构化提示词
3. 生成：运行 `scripts/image_gen.py`
4. 质检：vision_analyze 核对文字/比例/裁切
5. 修正：有错用 `--edit` 图生图局部修复，而不是整张重来
6. 交付：`MEDIA:` + 验证状态

## 常见错误速查

| 现象 | 原因 | 处理 |
|------|------|------|
| 401 无效令牌 | Key 过期/截断/旧站 Key | 到 api.openlux.ai 新建 Key，手动写入配置 |
| 403 账号已迁移 | 仍调旧域名 | Base URL 换 `https://api.openlux.ai/v1` |
| Unknown parameter: format | edits 接口不支持 format 参数 | 去掉 `format` 字段 |
| HTTP 429 | 上游负载饱和 | 等待后重试，或询问用户是否换模型 |
| 中文乱码 | prompt 自由排版 / 长句 | 改用结构化网格 + 短标签 |
| 尺寸不支持 | 请求了超 API 范围的尺寸 | 用 1024x1024 / 1536x1024 / 1024x1536 / 2048x2048 / 2160x3840 / 3840x2160 |

## References

- `references/api-config.md` — 配置与 OpenLux 迁移说明
- `references/chinese-grid-strategy.md` — 中文信息图提示词策略
- `references/prompt-method.md` — 提示词方法论与去AI味视觉
- `references/styles.md` — 风格模板细节
