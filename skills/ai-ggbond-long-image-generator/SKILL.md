---
name: ai-ggbond-long-image-generator
description: AI朱朱侠长图生成技能。使用云雾API（GPT-Image-2）生成有实际内容的信息图长图，支持小红书竖图、公众号横图、超长图等多种预设。HTML+CSS渲染为备选方案。
version: 1.1.0
tags: [image, infographic, long-image, social-media, design]
author: AI朱朱侠
triggers: ["长图生成", "信息图", "小红书图", "公众号图", "竖版图", "横版图"]
---

# AI朱朱侠长图生成

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
- **尺寸**：900 × 383 px（2.35:1）
- **适用**：微信公众号封面、头条封面
- **特点**：横向宽幅，标题突出

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

### ⚠️ API 错误码速查

| 状态码 | 含义 | 处理 |
|--------|------|------|
| 200 | 成功 | 保存图片 |
| 401 | 无效令牌（过期/错误） | 要求用户到 https://api.openlux.ai 重新生成 key |
| 403 | 有效 key 但无模型权限 | 检查云雾后台模型权限，换模型或升级套餐 |
| 429 | 限流（频繁失败触发） | 等待 120 秒后重试 |

### ⚠️ execute_code 中 API Key 截断

长 API Key（56字符）在 `execute_code` 中可能只收到 13 字符。**不要硬编码 key**，从 config.yaml 读取：

```python
import yaml
with open('/Users/admin/.hermes/profiles/gongcheng/config.yaml') as f:
    api_key = yaml.safe_load(f)['image_gen']['api_key']
```

详见 `references/yunwu-api-config.md`。

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

### 0. 检查 API 配置
```bash
# 验证 image_gen 配置存在且 key 有效
cat ~/.hermes/config.yaml | grep -A 5 "image_gen:"
```
如果 key 为空或返回 401，要求用户提供新 key。

### 1. 接收用户输入
```yaml
内容: "{用户提供的文字内容}"
尺寸: "{预设名称或自定义宽×高}"
风格: "{deep_tech/light/brand:{颜色}}"
模板: "{A/B/C/D/auto}"
```

### 2. 内容分析与结构化
- 提取标题、副标题
- 识别数据点、列表项
- 确定逻辑结构（并列/递进/对比）

### 2. 使用 GPT-Image-2 生成

```bash
# 单张生成
python scripts/render_gpt.py --prompt "内容描述" --preset xiaohongshu --output output.png

# 超长图（自动分段）
python scripts/render_gpt.py --prompt "内容描述" --preset super_long_medium --output long.png
```

### 3. 输出结果
```
✅ 长图已生成
📁 文件位置：{path}
📐 尺寸：{width} × {height} px
🎨 风格：{style}
```

## 注意事项

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
