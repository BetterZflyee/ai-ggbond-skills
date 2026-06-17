# 调查手记风配图风格

适用于「调查实验型」文章的配图风格。核心隐喻：像自己在做实验时拍的记录——软木板证据板、拆图截图、手绘笔记、随手写的便签。

## 触发条件

当文章原型为 ai-ggbond-writer 的「调查实验型」时使用此风格，替代学术风高密度信息图。

识别信号：
- 文章开头是"事情是这样的""上周我做了个实验"
- 叙事弧是英雄之旅：发现→困惑→探索→踩坑→解法→卧槽结果
- 文章主角是人（的实验和发现），不是工具（的技术原理）

## 六种子风格

| # | 子风格 | 适用场景 | 提示词关键词 |
|---|--------|----------|-------------|
| 📔 | 编辑杂志风封面 | 封面图 | dark background, dramatic lighting, torn paper metaphor, bold title |
| 📊 | 软木板证据板 | 实验对比/数据揭示 | corkboard texture, pushpins, red string, sticky notes, handwritten annotations |
| 🖥️ | 终端截图感 | 元数据发现/拆解过程 | dark terminal screen, green monospace text, highlighted lines, cursor blinking |
| 📝 | 手绘笔记风 | 概念对比/分类讲解 | hand-drawn sketch notes, off-white paper, pencil lines, colored pencil accents |
| 🔧 | 手绘流程图 | 工具流程/架构说明 | hand-drawn workflow, simple boxes, arrows, whiteboard drawing feel |
| 🛡️ | 暖色调金句卡 | 观点/结论/金句 | warm cream paper texture, letterpress print, amber brown tones |

## 对比：学术风 vs 调查手记风

| | 学术高密度信息图 | 调查手记风 |
|---|---|---|
| 适用文章类型 | 技术拆解/架构对比（产品手册型） | 调查实验/个人发现（故事型） |
| 文字密度 | 40-60% 文字 | 15-25% 文字 |
| 配色 | 白底黑字，严谨 | 暖米白/软木色，有人味 |
| 读者感受 | "停下来仔细看" | "我也想去试试" |
| 代表元素 | 表格网格、公式标注、性能指标 | 图钉、红线、便签、手写笔迹 |
| gpt-image-2表现 | 中文高密度时容易自由发挥 | 视觉叙事为主，中文量少，更稳定 |

## 已成功案例

2026-05-28 remove-ai-marks 文章：从学术风（v1，文章是产品手册型→配图也是学术风）→ 调查手记风（v2，文章重写为调查实验型→配图同步切换）。

v2最终配图清单：
- cover: 编辑杂志风暗底+撕裂照片隐喻
- infographic: 软木板证据板（203 vs 1100，图钉+红线+便签）
- 02-discovery: 终端截图（manufacturer:OpenAI 高亮）
- 03-three-marks: 手绘笔记（三层标记对比，铅笔线分隔）
- 04-engine-layers: 手绘流程图（三个盒子+箭头）
- 05-self-defense: 暖色调金句卡（奶油纸质感）
