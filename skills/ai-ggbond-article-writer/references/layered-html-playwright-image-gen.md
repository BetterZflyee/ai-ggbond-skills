# 分层合成信息图方案：gpt-image-2 纯视觉背景 + HTML/CSS 文字叠加

**产生日期**：2026-06-08
**适用场景**：需要高密度科技蓝图风格信息图，且包含大量中文标注
**核心矛盾**：gpt-image-2 中文渲染必乱码，但用户要求高密度+中文描述性文字

## 方案概述

将信息图生成拆为两层，分别用最适合的工具处理：

| 层 | 工具 | 负责内容 |
|---|------|---------|
| 视觉层 | gpt-image-2 | 科技蓝图背景、图标、线条、网格、图表形状 |
| 文字层 | HTML/CSS + Playwright 截图 | 中文标题、标签、描述、指标数据 |

两层天然一体——HTML 直接引用背景图作为 `<img>`，截图出来就是完整的一张图。

## 为什么不用其他方案

| 方案 | 问题 |
|------|------|
| gpt-image-2 直接生成含中文的图 | 中文必乱码（笔画缺损、偏旁错位） |
| 全英文标注 | 用户明确拒绝："除了专业词语，其他不能用英文" |
| matplotlib/Pillow 代码绘图 | 用户明确禁止："代码绘出来的结果效果非常差，这是我明令禁止的" |
| Pillow 后贴文字 | 用户反馈："文字本身可能会和后面的图分离，看上去很丑" |
| 简化文字量 | 用户拒绝："太丑了...不要重新简化成这么简单的内容" |

## 完整工作流

### Step 1: 生成纯视觉背景（gpt-image-2）

Prompt 中**明确禁止任何文字**：

```
High-density technical blueprint background, deep navy #0a1628,
glowing cyan lines #00d4ff, grid overlay.
[描述图表结构、图标、节点、连线]
NO TEXT, NO LETTERS, NO WORDS, NO CHARACTERS anywhere.
Pure visual elements only.
```

关键点：
- 强调 `NO TEXT, NO LETTERS, NO WORDS, NO CHARACTERS`
- 保留所有视觉元素描述（节点形状、图标、连线、网格）
- 输出为 PNG（无损）

### Step 2: 创建 HTML/CSS 叠加模板

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { width: 1536px; height: 1024px; overflow: hidden; position: relative; }
.bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
.overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }

/* 中文字体：PingFang > STHeiti > Microsoft YaHei */
.title {
  position: absolute;
  font-family: 'PingFang SC', 'STHeiti', 'Microsoft YaHei', sans-serif;
  font-size: 42px; font-weight: 700; color: #00d4ff;
  text-shadow: 0 0 20px rgba(0,212,255,0.5), 0 0 40px rgba(0,212,255,0.2);
  letter-spacing: 4px;
}
/* ... 更多样式 */
</style>
</head>
<body>
<img class="bg" src="03-bg.png" />
<div class="overlay">
  <div class="title">中文标题</div>
  <!-- 更多文字叠加 -->
</div>
</body>
</html>
```

关键 CSS 技巧：
- `text-shadow` 发光效果让文字和科技背景融为一体
- `position: absolute` 精确定位每个文字元素
- 半透明背景卡片 `background: rgba(10,22,40,0.7)` 让文字可读
- 边框 `border: 1px solid rgba(0,212,255,0.4)` 呼应背景线条

### Step 3: Playwright 截图

```python
import asyncio
from playwright.async_api import async_playwright

async def screenshot(html_file, output_file):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1536, "height": 1024})
        await page.goto(f"file://{html_file}", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=output_file, full_page=False, type="jpeg", quality=95)
        await browser.close()
```

首次使用需安装：
```bash
pip3 install playwright
python3 -m playwright install chromium
```

## 文字与背景融合的关键

用户拒绝"后贴膏药"感。融合的关键是 CSS 设计：

1. **发光效果**：`text-shadow` 让文字有科技蓝图的光晕
2. **半透明卡片**：`rgba(10,22,40,0.7)` 既遮挡背景又透出纹理
3. **边框呼应**：卡片边框颜色和背景线条颜色一致（如 `#00d4ff`）
4. **字号层次**：标题 42px、副标题 18px、标签 16px、描述 13px
5. **精确坐标**：每个文字元素的 `top/left` 需要配合背景图的节点位置

## 飞哥的文字语言规则

- **专业术语用英文**：DRI、Builder、AI Agent、VS、Auto
- **描述性文字必须中文**：标题、标签、说明、指标单位
- **禁止全英文标注**：用户原话"除了专业的词语，否则其他不能够用英文啊！"

## 已验证案例

2026-06-08 "睡觉时公司自己变好了" 文章 4 张章节配图：
- 03-yc-manual-rebuild.jpg（手册重建流程）
- 04-5x-growth.jpg（人效5倍增长曲线）
- 05-builder-vs-dri.jpg（Builder vs DRI 对比）
- 06-action-checklist.jpg（三件事行动清单）

模板文件保存在：文章目录 `images/overlay-{NN}.html`
