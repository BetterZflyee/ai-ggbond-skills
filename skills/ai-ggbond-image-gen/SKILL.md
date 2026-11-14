---
name: ai-ggbond-image-gen
description: 用 GPT-Image-2 (OpenLux) 做通用内容生图与图片编辑。
version: 1.1.0
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

## 已知坑（2026-11 修复）

- `--style` 非 raw 模式曾全线崩溃：`TypeError: argument of type 'function' is not iterable`（`style_key not in style_bundle` 把函数当字典）。已修成 `set(STYLE_ALIASES.values())`。若再次出现同类报错，先查这条守卫。
- 大标题里混拉丁字母容易被画坏（`AI 录音笔` → `A/录音笔`）。标题位尽量用纯中文，拉丁词放到副标题或正文小块。

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
| `business-report` | 商务咨询报告(白底藏青) | medium | 商务信息图/客户汇报 |

> 用户说"商务风格信息图"时一律用 `business-report`，不要用 `tech-neon`。

> 风格只是 prompt 模板辅助。**默认先走 `--style`**，风格库里有能对上的就不要手写；`--raw` 只在两种情况下用：风格库确实没有匹配（例如特殊版式复刻），或需要对版面做像素级指定。手写 raw prompt 最容易的失败是“只给三张卡几根线，就只画三张卡几根线”，出来像 PPT 骨架。

## 中文提示词铁律（信息图场景）

1. **结构化网格 > 叙述段落**：显式描述网格/单元格/边框（"左侧30%上下两卡"），模型按格子渲染中文成功率大幅提升
2. **短标签策略**：中文标签 2-4 字，越长越易乱码
3. **数据原文直传**：品牌名、百分比、金额必须原样进 prompt
4. **#标签不上图**：`#标签` 只属于 Markdown 正文
5. **不擅自换模型**：默认 gpt-image-2；遇到 429/错误先报告，等用户决定
6. **比例反复强调**：16:9 / 9:16 / 1:1 必须在 prompt 开头和结尾重复

详见 `references/chinese-grid-strategy.md` 与 `references/prompt-method.md`。

## 质感由密度决定（科技感/高级感不是靠配色）

同一模型、同一比例，出图“像 PPT”还是“像发布会主视觉”，差别几乎全在提示词里有没有写**图层与材质**：

- 前/中/后景分层（背景网格 → 悬浮玻璃面板 → 前景光点与刻度）
- 材质词：1px 发光描边、内部高光、边缘折射、柔和投影、体积光、光尘
- 密度词：数据刻度、角标括号、扫描线、连线节点
- 字号层级：标题为正文 2–3 倍，字距舒展

只写“深蓝底 + 三张卡 + 几根线”，任何模型都只能给你一个版式骨架。**要高级感，就把光和层次写进 prompt；要简洁，就明确写“极简，只保留标题与两张卡”，不要指望模型自己把握分寸。**

## 执行通道陷阱（2026-09 实测，导致多次生图失败）

1. **不要用内置 `image_generate` 工具**：它走官方 OpenAI 端点（key 常为 `dummy`）→ 必报 `401 Incorrect API key provided: dummy`。生图一律用本技能 `scripts/image_gen.py`。
2. **Key 来源要验证**：Key 可能只在某个 profile 下（如 `~/.hermes/profiles/<name>/config.yaml` 的 `image_gen.api_key`，OpenLux，key_len≈51），默认 `~/.hermes/config.yaml` 可能没有有效 key → 脚本按优先级遍历所有 profile config。
3. **环境变量污染**：若 env 有 `OPENAI_API_KEY=dummy`，会盖掉真 key → 用 `env -u OPENAI_API_KEY` 兜底。
4. **交互会话（飞书/Telegram）：**`execute_code` 需要用户在审批弹窗点"允许"才能跑；未点/超时=**秒级 BLOCKED**，且规则禁止无同意重试。遇到 BLOCKED 就停下来，把命令交给用户在终端跑，不要反复重试。
5. **cron 后台任务拦得更死**：无人可批 → `execute_code` 硬性拒绝，原文提示 `set approvals.cron_mode: approve`；且 `cronjob` 的 `script` 参数只接受 `~/.hermes/scripts/` 下的**相对路径**，不接受绝对路径。
6. **成本基线**：`--size 3840x2160 --quality high` 一次约 100 秒、output ≈13k-14k image tokens。

## 三栏映射信息图模板（高密度·中文稳）

需要"问题 → 根因 → 方案"这类推导型信息图时，用 `references/three-column-mapping-template.md` 的骨架：
左栏放**原始问题**、中栏放**层层剖析**（现象/机制/深层三个小标签）、右栏放**方案 + 出处**。
比上下堆叠的布局中文成功率更高，因为每格都是短标签。

### ⚠️ 三栏网格的致命短板：用户会说"这就是个 Excel 表格"（2026-09 实测被批评两次）

三栏网格 + 细黑线 + 单元格 + 行号，中文渲染确实最稳，但**视觉上就是一张放大的 Excel 表**。
飞哥的原话反馈：**"它就是一个 Excel 工具的内容"＋"文字内容上也没办法让我看到颅内高潮"**。

结论：**三栏网格 = 信息搬运，不是信息图。** 只在"让我查得到"的需求下用它。
需要"让我有感觉"时，改用**认知冲击版式** → 见 `references/cognitive-impact-layout.md`。

判别口诀：**查得到 → 表格；有感觉 → 分区 + 图形。**

## 手绘视觉笔记版式（hand-drawn sketch note）

需要"不生硬"、"不像 PPT"、"有手帐感"时用。骨架见 `references/hand-drawn-visual-note.md`。
已实测：3840x2160，40-50 秒一张，米白纸纹 + 手写中文 + 黄色荧光笔 + 便签贴纸 + 图钉胶带。

### ⚠️ 手写体中文的固有缺陷：错字率随字数线性上升（2026-09 实测 5 轮）

手写字形接近，模型会随机把字替换成形近字：会→发、开→值、空→实、工→正、闲→问、仓→合、她→望。

**实测规律**：
| 轮次 | 结果 |
|------|------|
| v4 | 2 处错字（会→发、开→值） |
| v4 edit | 没改对（无效） |
| v5 | 修对旧 2 处，冒新 2 处（工→正、闲→问） |
| v6 | 修对旧 2 处，冒新 1 处（空→实） |
| v6 edit | **反而搞坏其他区域**（文字错位、她→望、仓→合） |

**硬结论**：
1. **`--edit` 修中文错字不可靠**——两次实测：一次无效，一次破坏其他区域。**不要用它修文字**。
2. **整张重跑优于 edit**（快 40-50s，且不会破坏已对区域），但会引入新错字。
3. **错字收敛后应止损**：当只剩 1 处且语义不被误读时，停止重试，**如实告知用户并让其决定**，不要烧 token 打地鼠。
4. **降低错字率的唯一有效手段**：减少总字数 + 避免形近字 + 在 prompt 里把易错词单独列出来强调（实测能修对，但不能保新字不错）。
5. **零错字诉求下选印刷体**：要保证零错字，改用"清晰楷体 + 手绘装饰元素"的混合风格。

## 出图方向确认门槛（批量前必做）

**一次只出 1 张样图，让用户确认方向，再批量。** 不要一口气生成 3–6 张再交付——方向错了全部作废，还要重跑几十分钟。

样图交付时只问两个问题：质感能不能接受、版式方向对不对。用户点头再扩量。

如果视觉复核通道不可用（只能 OCR 验字），**不要用“文字全对”假装图没问题**——明确告诉用户“我验得了字，验不了好看”，把观感判断交回给用户。

## 质检门禁（每次生图必做）

### 先试全模型，失败再降级代码压字（2026-11-01 实测修订）

**默认流程改了两步走，不要一上来就用 PIL 压字：**

1. 先用 gpt-image-2 直接生成**含文字的完整成品**（结构化网格 prompt + 短句文字块）。
2. 立刻 OCR 全量核对。**全对 → 直接用**，视觉融合度比代码压字好。
3. 只要有一处错字/错数字 → 重试 1 次；再错 → 退回“模型出无字底图 + 代码压字”。

依据：同日同模型，全模型版一次通过 18 行中文含 `48,635` 全对；但历史上 12 张里错过 5 处（`70%`→`10%`、`2.4`→`24`、`它`→`已`、`晚上机器干完`→`晚上枧嚣干亮`）。**是命中率问题，不是能力问题**，所以先试、再验、后降级，而不是默认绕开。

代码压字仍是兜底：确定性 100%，但文字与画面分层，观感偏“贴上去”。

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
- `references/three-column-mapping-template.md` — 三栏映射信息图骨架（查得到）
- `references/cognitive-impact-layout.md` — 认知冲击型分区版式（有感觉）
- `references/hand-drawn-visual-note.md` — 手绘视觉笔记骨架（手帐感）
