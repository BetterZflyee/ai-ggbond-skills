---
name: ai-ggbond-long-image-generator
description: AI朱朱侠长图生成技能。使用云雾API（GPT-Image-2）生成有实际内容的信息图长图，支持小红书竖图、公众号横图、超长图等多种预设。HTML+CSS渲染为备选方案。
version: 1.1.0
tags: [image, infographic, long-image, social-media, design]
author: AI朱朱侠
triggers: ["长图生成", "信息图", "小红书图", "公众号图", "竖版图", "横版图"]
---

# AI朱朱侠长图生成技能

## 内容型信息图质量门禁（飞哥场景，强制）

生成“高密度信息图”时，先完成信息架构，再写生图提示词；不能把“科技感、元素多、画面酷”误当成信息密度。

1. **先画论证链**：从文章提取“前提 → 冲突/机制 → 控制条件 → 结果”，多事件必须串成因果链，不能并列堆故事。
2. **模块必须有信息职责**：每栏至少包含模块标题、2—5个短标签和一句阶段结论；模块之间用方向明确的箭头连接。
3. **三秒理解测试**：没读文章的人，应能在3秒内说出“这张图在解释什么、为什么、最后得到什么结论”。做不到就重构，不以美观为由放行。
4. **独立阅读测试**：图片脱离正文后，仍能复述章节核心论证；只有标题、人物、舞台、裂缝、机器人等装饰元素的不算信息图。
5. **文字与表达双质检**：OCR无错字只是第一关；第二关必须检查因果、层级、箭头方向、模块对应关系、字号和移动端可读性。
6. **署名规则**：默认不添加作者名、日期、年份或“飞哥”落款，除非用户明确要求。可保留小型“AI朱朱侠”品牌水印，但不得抢占信息区。
7. **先单张测试再批量**：首张通过内容、文字、可读性三重质检后，才生成剩余图片，避免批量消耗后整体返工。

详细检查表见 `references/high-density-infographic-quality-gates.md`。

## 核心能力
使用 GPT-Image-2 (云雾API) 生成有实际内容的高质量信息图长图，支持多种社交平台尺寸预设。

## ⚠️ 关键教训

### ❌ 不要用 PIL 画空壳
PIL 生成的图片只有占位符色块和文字，没有实际视觉内容。用户明确要求"用云雾API的GPT-Image-2来生成长图，不能直接用PIL"。

### ✅ 正确方式：GPT-Image-2 + 分段拼接
1. 将长图分成多个 1024×1536 片段
2. 每段调用 GPT-Image-2 生成有实际内容的图片
3. 使用重叠区域智能拼接
4. PIL 仅用于拼接，不用于内容生成

**重要：必须使用 AI 图片生成（GPT-Image-2），不能用 PIL 画占位图。PIL 脚本仅用于快速原型测试。**

### 🔐 API Key 安全机制（重要）
Agent 工具（terminal/write_file/execute_code）会自动截断/隐藏长密钥（56char→13char或`***`）。这是系统级安全保护。

**正确做法**：
- ❌ 不要在脚本中硬编码 API Key
- ❌ 不要通过 execute_code 传递完整 Key
- ✅ 让用户手动运行 `hermes config set image_gen.api_key <KEY>`
- ✅ 脚本中从 `~/.hermes/config.yaml` 读取（yaml 库读取不截断）
- ✅ 或从环境变量 `YUNWU_API_KEY` 读取

### 🚨 Yunwu API 错误码
| 状态码 | 含义 | 解决方案 |
|--------|------|----------|
| 401 | 无效令牌 | API Key 过期或无效，需重新生成 |
| 403 | 无权限访问模型 | 该 Key 没有目标模型权限，换模型或换 Key |
| 429 | 频率限制 | 等待 120 秒后重试 |
| 200 | 成功 | 检查返回的 b64_json 或 url |

### 🎯 模型权限
不同 API Key 有不同模型权限：
- `dall-e-3` - 部分 Key 无权限（返回 403）
- `gpt-image-1` - 上一代模型
- `gpt-image-2` - 默认推荐，大多数 Key 支持
- `flux-1.1-pro` - 高质量快速生成

**建议**：先用 `gpt-image-2` 测试，失败时尝试其他模型。

## 参考文档

- `references/yunwu-api-config.md` - 云雾 API 配置详解、错误排查、多链路配置
- `references/troubleshooting.md` - 常见问题与解决方案、调试技巧
- `references/size-guide.md` - 各平台尺寸选择指南
- `references/README_YUNWU.md` - 快速开始指南

## 快速开始（3步）

### Step 1: 配置 API Key
```bash
bash ~/.hermes/skills/ai-ggbond-long-image-generator/scripts/setup_yunwu.sh 你的完整API_KEY
```

### Step 2: 测试连接
```bash
python3 ~/.hermes/skills/ai-ggbond-long-image-generator/scripts/test_yunwu_api.py
```

### Step 3: 生成长图
```bash
# 小红书竖图
python3 ~/.hermes/skills/ai-ggbond-long-image-generator/scripts/generate_long_image.py \
    --prompt "AI工具使用指南" --preset xiaohongshu --output /tmp/test.png

# 超长图（4倍高度）
python3 ~/.hermes/skills/ai-ggbond-long-image-generator/scripts/generate_long_image.py \
    --prompt "完整教程" --preset super_long_medium --output /tmp/long.png
```

## 支持的尺寸预设

### 1. 小红书竖图（默认）
- **尺寸**：1080 × 1440 px（3:4）
- **适用**：小红书笔记主图、Instagram竖图
- **特点**：竖向阅读，适合图文混排

### 2. 小红书长图
- **尺寸**：1080 × 2400 px（1:2.2）
- **适用**：教程类、步骤类、清单类内容
- **特点**：超长竖图，滚动阅读体验

### 2.1 超长图-小号
- **尺寸**：1080 × 3200 px（1:3）
- **适用**：深度教程、详细清单、多步骤指南
- **特点**：3倍宽度高度，适合内容丰富的干货

### 2.2 超长图-中号
- **尺寸**：1080 × 4320 px（1:4）
- **适用**：完整指南、详细对比、长篇文章配图
- **特点**：4倍宽度高度，信息承载量大

### 2.3 超长图-大号
- **尺寸**：1080 × 5400 px（1:5）
- **适用**：超详细教程、完整知识图谱、年度报告
- **特点**：5倍宽度高度，适合超长内容

### 2.4 超长图-极限
- **尺寸**：1080 × 7200 px（1:6.7）
- **适用**：完整课程大纲、详细百科、超长清单
- **特点**：极限长度，需要分段渲染保证稳定性

### 3. 公众号封面横图
- **尺寸**：900 × 383 px（约 2.35:1）；需要严格比例时优先使用 **1645 × 700 px（精确 2.35:1）**
- **适用**：微信公众号封面、头条封面
- **特点**：横向宽幅，标题突出
- **强制工作流**：封面必须在最终 2.35:1 画布上原生构图或确定性重排，**禁止先生成 16:9 再机械居中裁切**。标题、人物/图标和底部支点等核心元素必须完整落在最终安全区内；生成后读取真实像素尺寸并计算 `width / height`，再做视觉质检。
- **安全区**：标题与核心视觉距离上下边缘至少为画布高度的 8%；不要把标题放在 16:9 原稿顶部、再期待横幅裁切后仍可读。

### 4. 公众号正文配图
- **尺寸**：1080 × 720 px（3:2）
- **适用**：公众号文章内插图
- **特点**：横向阅读，信息密度适中

### 5. 正方形图
- **尺寸**：1080 × 1080 px（1:1）
- **适用**：Instagram Feed、头像、卡片
- **特点**：对称构图，视觉聚焦

### 6. 手机壁纸
- **尺寸**：1170 × 2532 px（19.5:9）
- **适用**：iPhone壁纸、锁屏
- **特点**：考虑安全区域，避开顶部刘海/底部横条

### 7. 电脑壁纸
- **尺寸**：2560 × 1440 px（16:9）
- **适用**：桌面壁纸、演示背景
- **特点**：横向宽幅，视觉主体居中

### 8. PPT幻灯片
- **尺寸**：1920 × 1080 px（16:9）
- **适用**：演示文稿、Keynote
- **特点**：标准16:9，适合投影和屏幕

### 9. 自定义尺寸
- **输入**：用户指定宽×高
- **限制**：最小 300×300，最大 3000×6000
- **适用**：特殊场景需求

## 设计风格指南

### 配色方案（默认：科技深色）
```
主背景：#0F1419（深蓝黑）
卡片背景：#1A2332（深蓝灰）
主文字：#FFFFFF（纯白）
次文字：#8B95A5（灰蓝）
强调色1：#00D4FF（霓虹蓝）
强调色2：#FF6B35（活力橙）
强调色3：#00E676（科技绿）
```

### 配色方案（备选：清新浅色）
```
主背景：#F8F9FA（浅灰白）
卡片背景：#FFFFFF（纯白）
主文字：#1A1A2E（深蓝黑）
次文字：#6C757D（中灰）
强调色1：#0066FF（经典蓝）
强调色2：#FF4757（珊瑚红）
```

### 排版规范
- **标题**：32-48px，加粗，主色或强调色
- **副标题**：20-24px，中等粗细，次文字色
- **正文**：16-18px，常规，主文字色
- **注释**：12-14px，常规，次文字色
- **行高**：1.6-1.8
- **段落间距**：24-32px
- **边距**：图片宽度的 5-8%

## 生成流程

### Step 1：确认需求
```
1. 内容类型：数据报告 / 教程步骤 / 观点卡片 / 清单列表 / 对比分析
2. 平台目标：小红书 / 公众号 / 朋友圈 / Instagram / 通用
3. 尺寸选择：使用预设或自定义
4. 风格偏好：深色科技 / 浅色清新 / 品牌定制
```

### Step 2：生成HTML模板
```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  /* 基础重置 */
  * { margin: 0; padding: 0; box-sizing: border-box; }
  
  /* 画布容器 */
  .canvas {
    width: {WIDTH}px;
    height: {HEIGHT}px;
    background: {BG_COLOR};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    position: relative;
    overflow: hidden;
  }
  
  /* 内容区域 */
  .content {
    padding: {PADDING}px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  /* 模块化组件 */
  .header { /* 头部区域 */ }
  .section { /* 内容区块 */ }
  .footer { /* 底部区域 */ }
  .card { /* 卡片容器 */ }
  .badge { /* 标签徽章 */ }
  .divider { /* 分隔线 */ }
</style>
</head>
<body>
<div class="canvas">
  <div class="content">
    <!-- 内容结构 -->
  </div>
</div>
</body>
</html>
```

### Step 3：渲染截图
```python
# 使用 playwright 截图
from playwright.sync_api import sync_playwright

def render_html_to_image(html_path, output_path, width, height):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': width, 'height': height})
        page.goto(f'file://{html_path}')
        page.screenshot(path=output_path, full_page=True)
        browser.close()
```

## 常用模板结构

### 模板A：数据报告卡片
```
┌─────────────────────────┐
│  [LOGO]  [标题]         │  ← 头部（品牌+标题）
├─────────────────────────┤
│  ┌─────────────────────┐│
│  │  核心数据/图表       ││  ← 主数据区
│  └─────────────────────┘│
│  ┌──────┐ ┌──────┐      │
│  │指标1 │ │指标2 │      │  ← 指标卡片
│  └──────┘ └──────┘      │
│  ┌─────────────────────┐│
│  │  详细说明/要点       ││  ← 正文区
│  └─────────────────────┘│
│  [来源]  [日期]         │  ← 底部（元信息）
└─────────────────────────┘
```

### 模板B：教程步骤图
```
┌─────────────────────────┐
│  [步骤标题]             │  ← 大标题
│  [副标题/说明]          │
├─────────────────────────┤
│  ① ──────────────────── │
│  [步骤1标题]            │  ← 步骤1
│  [步骤1说明]            │
│  ② ──────────────────── │
│  [步骤2标题]            │  ← 步骤2
│  [步骤2说明]            │
│  ③ ──────────────────── │
│  [步骤3标题]            │  ← 步骤3
│  [步骤3说明]            │
├─────────────────────────┤
│  [小贴士/总结]          │  ← 底部总结
└─────────────────────────┘
```

### 模板C：观点卡片
```
┌─────────────────────────┐
│  ┌─────────────────────┐│
│  │                     ││
│  │  "金句/核心观点"    ││  ← 引用框
│  │                     ││
│  └─────────────────────┘│
│                         │
│  [论述要点1]            │  ← 正文
│  [论述要点2]            │
│  [论述要点3]            │
│                         │
│  ── 作者/来源 ──        │  ← 署名
└─────────────────────────┘
```

### 模板D：对比分析图
```
┌─────────────────────────┐
│  [对比标题]             │
├──────────┬──────────────┤
│  [方案A] │   [方案B]    │  ← 对比标题
├──────────┼──────────────┤
│  ✓ 优点1 │   ✓ 优点1   │
│  ✓ 优点2 │   ✓ 优点2   │  ← 优缺点
│  ✗ 缺点1 │   ✗ 缺点1   │
├──────────┴──────────────┤
│  [结论/建议]            │  ← 总结
└─────────────────────────┘
```

## API 配置说明

> 云雾凭据排查与验证：当配置中存在多个 Key、掩码 Key 或文本/图片权限不同，必须先阅读 `references/yunwu-key-discovery-and-verification.md`。不要取配置文件中的第一个 `api_key`；正式批量生图前必须用 `/v1/images/generations` 做低成本单图探针。

**详细配置见 `references/yunwu-api-config.md`**

### ⚠️ API Key 设置必须由用户手动完成

Agent 无法自动设置 API Key（安全机制会截断长密钥）。当发现 `image_gen.api_key` 为空或无效时：

1. **不要**尝试通过 execute_code、terminal 变量、write_file 传递 key
2. **直接告诉用户**在终端运行：
   ```bash
   hermes config set image_gen.api_key 完整的key
   hermes config set image_gen.base_url https://api.openlux.ai/v1
   hermes config set image_gen.model gpt-image-2
   ```
3. 用户设置完成后，再继续生成任务

### 快速配置

config.yaml 有安全写保护，必须用 CLI：

```bash
hermes config set image_gen.provider openai
hermes config set image_gen.model gpt-image-2
hermes config set image_gen.base_url https://api.openlux.ai/v1
hermes config set image_gen.api_key 你的实际key
```

### 关键注意事项

1. `image_generate` 工具读取 `config.yaml` 的 `image_gen.api_key`，不是环境变量
2. 贴图 skill 的脚本读取 `~/.ai-ggbond-skills/.env` 的 `YUNWU_API_KEY`，位置不同
3. API Key 可能过期（返回 401 "无效的令牌"），需要到 https://api.openlux.ai 重新生成
4. `provider` 必须设为 `openai`，不能是 `custom`

## 渲染脚本说明

### 0. render_gpt.py - GPT-Image-2 生成（⭐ 首选）
- 使用云雾 API 调用 GPT-Image-2 生成有实际内容的图片
- 支持单张和超长图（自动分段+拼接）
- 需要有效的云雾 API Key

```bash
# 单张生成
python scripts/render_gpt.py --prompt "AI工具使用指南" --preset xiaohongshu --output output.png

# 超长图（自动分段）
python scripts/render_gpt.py --prompt "完整教程" --preset super_long_medium --output long.png

# 自定义尺寸
python scripts/render_gpt.py --prompt "内容" --width 1080 --height 5400 --output custom.png
```

### 1. render.py - 标准渲染脚本
- 适用于普通长图（高度 < 3000px）
- 支持 Playwright / Selenium / Puppeteer
- 高质量 2x Retina 清晰度

### 2. render_long.py - 超长图稳定渲染脚本
- 专门处理超长图（高度 > 3000px）
- **分段渲染 + 智能拼接**策略
- 自动重试机制（每段最多 3 次）
- 可配置分段高度和重叠区域

```bash
# 超长图渲染示例
python scripts/render_long.py --html input.html --output output.png --preset super_long_medium
python scripts/render_long.py --html input.html --output output.png --height 7200 --force-segment
```

### 3. render_lightweight.py - 轻量版渲染脚本
- **无需额外依赖**（仅需 Pillow）
- 使用 PIL 图片处理生成长图
- 稳定性最高，适合批量生成
- 支持所有预设尺寸

```bash
# 轻量版渲染示例
python scripts/render_lightweight.py --preset super_long_medium --output output.png
python scripts/render_lightweight.py --width 1080 --height 7200 --output output.png
```

### 脚本选择指南

| 场景 | 推荐脚本 | 原因 |
|------|----------|------|
| **有实际内容的长图** | render_gpt.py | GPT-Image-2 生成真实内容 ⭐首选 |
| 超长图（> 3000px） | render_gpt.py + 分段 | AI 分段生成 + 拼接 |
| HTML 精确还原 | render.py / render_long.py | 需要 Playwright 环境 |
| 快速占位/测试 | render_lightweight.py | 仅用于尺寸测试，不含实际内容 |
| **API Key 无法设置时** | 独立工具包 | 打包脚本让用户手动运行，见 `references/standalone-toolkit-pattern.md` |

### ⚠️ 关键 Pitfall

**绝对不要用 PIL 生成空壳图片给用户看！**

render_lightweight.py 只是用来测试尺寸和渲染流水线的，它生成的是没有任何实际内容的占位图。用户需要的是有真实文字、图表、设计的信息图。

正确流程：
1. 确认云雾 API Key 有效（见 `references/yunwu-api-config.md`）
2. 使用 render_gpt.py 调用 GPT-Image-2 生成
3. 超长图：分段生成每段，再拼接

如果 API Key 过期（401 错误），立即告知用户，不要用 PIL 空壳替代。

## 调用前强制验证（不要凭“没读到”就判定无 Key）

生成图片前执行以下诊断顺序：

1. 用 `hermes -p <当前profile> config env-path` 找到 Profile `.env`
2. 读取时只输出变量是否存在和长度，不输出完整值或可恢复前后缀
3. 加载 Profile `.env`，请求 `$OPENAI_BASE_URL/models`（未配置 Base URL 时使用 `https://api.openlux.ai/v1/models`）
4. 只有在 **HTTP 200 且模型列表包含 `gpt-image-2`** 后，才进入生图
5. 若 `OPENAI_API_KEY` 验证有效，而 `YUNWU_API_KEY` 缺失，补同 Profile 内的兼容变量后再次验证

> 常见误诊：当前进程环境显示 `YUNWU_API_KEY` 未导出、`config.yaml` 的 `image_gen.api_key` 为空，于是报告“没有 Key”。这不成立；必须继续检查当前 Profile `.env` 的 `OPENAI_API_KEY` / `OPENAI_BASE_URL`。

## API 错误码速查

| 状态码 | 含义 | 处理 |
|--------|------|------|
| 200 | 成功 | 保存图片 |
| 401 | 无效令牌（过期/错误） | 要求用户到 https://api.openlux.ai 重新生成 key |
| 403 | 有效 key 但无模型权限 | 检查云雾后台模型权限，换模型或升级套餐 |
| 429 | 限流（频繁失败触发） | 等待 120 秒后重试 |

**凭证验证铁律**：
- `sk-xxx...xxxx` 这类带省略号的值是展示掩码，不是真实可调用 Key。
- `/v1/models` 返回 200 不能证明图片生成权限；批量前必须用目标模型请求 `/v1/images/generations` 做一张低成本测试图。
- 配置存在多个 Key 时不得默认取第一个；逐个匿名验证目标生成端点，日志只记录指纹或序号，禁止输出完整 Key。

## ⚠️ render_gpt.py 已知 Bug（已修复）

### Bug 1：API Key 读取路径错误
`get_api_key()` 原本只从 `fallback_providers` 和 `providers.openai` 读取 key，但实际 key 在 `image_gen.api_key` 字段。

**修复**：在 `get_api_key()` 中优先检查 `config.get('image_gen', {}).get('api_key')`。

**症状**：401 错误 "无效的令牌"，即使 config.yaml 中 key 是正确的。

### Bug 2：模型名称硬编码
脚本中 `"model": "gpt-image-1"` 是硬编码的，忽略了用户 config.yaml 中的 `image_gen.model` 设置。

**修复**：将硬编码的 `gpt-image-1` 改为 `gpt-image-2`（或从 config 读取）。

**症状**：403 错误 "该令牌无权访问模型 gpt-image-1"。

### 排查顺序
如果生成失败，先检查这两个 bug 是否已修复：
```bash
grep -n "gpt-image-1" scripts/render_gpt.py  # 应该没有结果
grep -n "image_gen" scripts/render_gpt.py     # 应该有 api_key 读取逻辑
```

### ⚠️ 云雾链路与 API Key 真实性检查

用户明确要求使用本技能或 GPT-Image-2 时，优先按本技能的**云雾 API 链路**执行，不要因为通用 `image_generate` 工具处于默认 OpenAI/dummy 配置就误判为云雾不可用。

生成前必须做无泄露预检：

1. 优先读取当前 profile 的 `image_gen` 配置或 `YUNWU_API_KEY`；
2. Key 长度不足 20、等于 `dummy`、或包含 `...` 时，视为占位/掩码，禁止发起请求；
3. 配置备份和工具输出中显示的 `sk-xxx...xxxx` 通常只是脱敏文本，不能直接当真实 Key 使用；
4. 如果技能自带 `.env` 中存在完整 Key，可在不打印 Key 的前提下验证长度和调用状态；
5. 先生成一张测试图，确认状态码、模型权限和余额，再批量生成；
6. 401/403/余额错误应立即停止批量任务，报告真实错误，不换模型、不做 PIL 占位图。

云雾配置排查与安全测试流程见 `references/yunwu-key-resolution-and-batch-preflight.md`。

## 超长图渲染（稳定性保障）

### 为什么超长图需要特殊处理？

当图片高度超过 3000px 时，直接渲染可能遇到：
1. **内存溢出**：浏览器渲染超长页面时内存占用过高
2. **截图截断**：Playwright 截图可能出现空白区域
3. **内容缺失**：懒加载内容未完全加载
4. **字体闪烁**：Web字体未完全渲染

### 稳定渲染策略：分段渲染 + 智能拼接

```
┌─────────────────────┐
│     原始 HTML       │
└─────────────────────┘
          ↓
┌─────────────────────┐
│  分段渲染（2000px）  │
│  片段1: 0-2000px    │
│  片段2: 1900-3900px │  ← 100px 重叠
│  片段3: 3800-5400px │
└─────────────────────┘
          ↓
┌─────────────────────┐
│  智能拼接（去重叠）  │
└─────────────────────┘
          ↓
┌─────────────────────┐
│   最终超长图输出     │
└─────────────────────┘
```

### 超长图渲染命令

```bash
# 使用预设
python scripts/render_long.py --html input.html --output output.png --preset super_long_medium

# 自定义尺寸
python scripts/render_long.py --html input.html --output output.png --width 1080 --height 5400

# 强制分段渲染（即使高度 < 3000px）
python scripts/render_long.py --html input.html --output output.png --height 2500 --force-segment

# 自定义分段参数
python scripts/render_long.py --html input.html --output output.png --height 7200 \
    --segment-height 2500 --overlap 150 --scale 2

# 列出所有超长图预设
python scripts/render_long.py --list-presets
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| --segment-height | 2000 | 每段渲染高度（px） |
| --overlap | 100 | 重叠区域（px），用于平滑拼接 |
| --scale | 2 | 清晰度倍数（2x = Retina） |
| --force-segment | false | 强制分段渲染 |

### 稳定性最佳实践

1. **分段高度选择**
   - 推荐：2000-2500px
   - 太小：增加拼接次数，可能出现接缝
   - 太大：可能触发内存问题

2. **重叠区域**
   - 推荐：100-150px
   - 太小：拼接处可能有可见接缝
   - 太大：增加渲染时间

3. **清晰度**
   - 推荐：2x（Retina 清晰度）
   - 1x：文件小但模糊
   - 3x：超清晰但文件大

4. **HTML 设计优化**
   - 避免使用 `position: fixed`
   - 图片使用 `loading="eager"`
   - 字体使用 `font-display: block`

## 超长图使用示例

### 示例1：生成 4 倍长图（教程）

```bash
# 1. 生成 HTML
python scripts/quick_gen.py --template steps \
    --title "AI工具完整使用指南" \
    --subtitle "从入门到精通" \
    --steps '[{"title":"选择工具","desc":"..."},{"title":"安装配置","desc":"..."},{"title":"基础使用","desc":"..."},{"title":"进阶技巧","desc":"..."},{"title":"高级功能","desc":"..."},{"title":"实战案例","desc":"..."},{"title":"常见问题","desc":"..."},{"title":"总结","desc":"..."}]' \
    --output tutorial.html

# 2. 渲染超长图
python scripts/render_long.py --html tutorial.html --output tutorial.png --preset 4x
```

### 示例2：生成极限长图（年度报告）

```bash
# 1. 准备 HTML（自定义内容）
# 2. 渲染极限长图
python scripts/render_long.py --html report.html --output report.png --preset super_long_xl
```

## 执行步骤（GPT-Image-2 优先）

### 0. 批量任务先做单张预检（强制）

当用户要求为一篇文章生成多张章节图时，禁止在未验证配置的情况下直接并行生成整批图片。必须遵循：

```text
检查当前 Profile 配置 → 生成1张低文字密度样图 → 检查中文与风格 → 再按2—3张分批生成 → 每批质检
```

多 Profile 环境必须读取当前 Profile 的 `config.yaml`，不要默认读取 `~/.hermes/config.yaml`。详细预检、`dummy` 密钥诊断和中文乱码止损规则见 `references/batch-image-generation-preflight.md`。

### 1. 检查 API 配置
```bash
# 验证 image_gen 配置存在且 key 有效
cat ~/.hermes/config.yaml | grep -A 5 "image_gen:"
```
如果 key 为空或返回 401，要求用户提供新 key。

### 0.1 云雾凭据发现与生成级验证（重要）

当当前 `image_gen` 配置为 `dummy`、Key 被 `...` 掩码，或历史配置里存在多个候选 Key 时，**禁止默认取第一个完整 Key**。同一配置文件可能同时包含失效的主模型 Key和有效的图片专用 Key。

必须：

1. 收集并去重全部未掩码候选 Key；忽略 `dummy`、含 `...`、长度不足以及 `.env.example` 示例值。
2. 日志只输出 Key 的哈希指纹和来源路径，禁止输出完整 Key。
3. 不以 `/v1/models` 返回 200 作为最终判断；必须调用 `/v1/images/generations` 做一次低成本 `gpt-image-2` 实际生成探针。
4. 正式批量生成前先做一张章节图，并完成中文白名单质检。

详细排查与验证方法见 `references/yunwu-key-discovery-and-generation-probe.md`。

### 0.2 中文信息图的隐藏英文检查

除了标题和标签，还要检查图标内部。模型可能在表格、软件、设备图标中自动加入 `X` 等字母。提示词应写明“图标内部不放任何字母、数字、文字或软件标志”，并在生成后按文字白名单检查；出现任何未指定字母，单张重做。

### 1. 接收用户输入
```yaml
内容: "{用户提供的文字内容}"
尺寸: "{预设名称或自定义宽×高}"
风格: "{deep_tech/light/brand:{颜色}}"
模板: "{A/B/C/D/auto}"
```

### Step 2：内容分析与结构化
- 提取标题、副标题
- 识别数据点、列表项
- 确定逻辑结构（并列/递进/对比）
- **章节信息图优先构建递进因果链**，不能只画氛围或做简单左右对比
- 高密度章节图的设计、提示词和双重质检详见 `references/high-density-section-infographic.md`

### 2. 使用 GPT-Image-2 生成

```bash
# 单张生成
python scripts/render_gpt.py --prompt "内容描述" --preset xiaohongshu --output output.png

# 超长图（自动分段）
python scripts/render_gpt.py --prompt "内容描述" --preset super_long_medium --output long.png
```

### Step 3：双重质量门禁（不可跳过）

生成成功不等于信息表达成功，必须同时检查：

1. **文字门禁**：逐字核对标题与标签；检查乱码、错字、漏项，以及图标内部偷偷出现的英文、软件标志和伪文字。
2. **语义门禁**：让没读文章的人看图，必须能在 3 秒内说清“条件/输入 → 变化/机制 → 结果 → 结论”。如果只能感受到科技氛围，却说不清因果关系，立即重构版式，不得因为美观而放行。

批量任务必须先生成 1 张代表图，通过双重门禁后再批量。详细规则见 `references/semantic-infographic-quality-gate.md`。

### Step 4：输出结果
```
✅ 长图已生成并通过文字+语义质检
📁 文件位置：{path}
📐 尺寸：{width} × {height} px
🎨 风格：{style}
```

## 与文章配图任务的边界

当用户要求“给现有文章配图”时，先判断图片承担的是**证据功能**还是**氛围功能**：

- 价格、政策、产品能力、Benchmark、官方声明、产品界面等事实节点，优先使用官方原始页面截图或官方图表，并做紧裁与可读性检查。
- GPT-Image-2 更适合封面、抽象概念、流程解释和没有原始视觉材料的观点图，不应替代可获得的官方证据图。
- 不要因为本技能可生图，就强制所有文章走生图；配图的目标是帮助论证和阅读，而不是展示模型能力。
- 官方图已经足够时，可直接进入公众号排版；只有需要自制解释图时，才执行本技能的 API 检查与生成流程。

## 注意事项

> 微信公众号封面如涉及 2.35:1，请先读 `references/wechat-cover-235-safe-layout.md`，按最终画布原生构图并完成尺寸 + 视觉双重质检。

1. **文字渲染**：HTML渲染保证文字锐利，避免图片模糊
2. **字体选择**：优先系统字体，中文用苹方/微软雅黑
3. **安全区域**：壁纸类图预留刘海/横条空间
4. **文件大小**：控制在 2MB 以内，优化加载速度
5. **中文字体**：确保服务器/本地安装中文字体
6. **颜色对比**：文字与背景对比度 ≥ 4.5:1（WCAG AA标准）

## 使用示例

```
用户：帮我生成一张小红书竖图，内容是「AI工具推荐TOP5」
AI：好的，使用模板C（观点卡片），尺寸1080×1440，深色科技风格...
```

```
用户：公众号封面图，标题「2024年最值得关注的AI产品」
AI：好的，使用公众号封面横图900×383，浅色清新风格...
```

```
用户：自定义尺寸 1200×800，做一张对比图
AI：好的，使用模板D（对比分析图），自定义尺寸1200×800...
```
