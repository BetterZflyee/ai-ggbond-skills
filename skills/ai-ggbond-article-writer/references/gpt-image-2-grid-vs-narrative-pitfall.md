# gpt-image-2 结构化网格 vs 叙述性段落陷阱

## 核心发现

gpt-image-2 处理中文高密度信息图时，**叙述性段落 prompt 会导致模型"自由发挥"**——输出与 prompt 要求完全无关的内容。

## 失败案例（2026-05-28）

**Prompt**: 详细叙述性段落描述"三层清除引擎技术架构"
**实际输出**: "AI内容发布前的透明标注流程 / C2PA provenance & disclosure overview"——完全无关

**Prompt**: 详细叙述性段落描述"remove-ai-marks 技术全景四区域布局"
**实际输出**: "AI内容发布前的透明标注流程 / provenance disclosure overview"——同样偏离

## 策略一：结构化网格布局

**结构化网格 > 自由排版**。用明确的网格/表格/四象限布局指令替代叙述性段落：

| 布局类型 | Prompt模式 | 成功率 |
|----------|-----------|--------|
| 三列表格 | "三列并排，每列浅灰背景色块，左列标题X中列标题Y右列标题Z" | ✅ 高 |
| 三行表格 | "三行表格，每行固定单元格：输入→方法→参数→性能" | ✅ 高 |
| 2×2四象限 | "2x2四个方块，每块灰色边框+标题+三条列表" | ✅ 高 |
| 叙述性段落 | "布局分四个区域。左上区问题…右上区原理…" | ❌ 低 |

**口诀：结构化网格 > 自由排版。OCR验证后再替换。**

---

## 策略二：极简中文 + 英文标签（2026-06-08 补充）

当配图是**流程图、架构图、对比图**（非网格/表格类）时，结构化网格策略不适用。此时用**极简中文 + 英文节点标签**。

### 核心原则

- **中文只留 1 个标题**（3-5 个字），如"手册重建流程""人效5倍增长"
- **节点标签全用英文**（Audio → Classify → Manual → Update → Agent）
- **强调 "Minimal text, maximum visual"**，让模型把精力放在图形而不是文字渲染上
- **用图标替代文字**：Microphone icon、Brain icon、Gear icon 等视觉锚点

### 成功案例（2026-06-08）

**失败 Prompt**（原始版，大量中文描述）：
```
高密度信息大图风格，科技蓝图配色（深蓝背景#0a1628，亮蓝线条#00d4ff，白色文字）。
展示YC用户手册重建流程：2000小时录音 → AI主题分类 → 150页手册 → 月度自动更新 → AI Agent查询。
用技术架构图风格，包含数据流箭头、处理节点图标、输出指标。中文标注。无水印。
```
→ 中文全部乱码，字形扭曲不可读

**成功 Prompt**（极简版）：
```
Technical blueprint infographic, dark navy background #0a1628, cyan lines #00d4ff, white text.
Linear pipeline flow chart with 5 nodes connected by arrows: Microphone icon → Brain/AI icon → Book icon → Refresh icon → Robot icon.
Only ONE large Chinese title at top: 手册重建流程.
Each node label in English only: Audio → Classify → Manual → Update → Agent.
Minimal text, maximum visual. Clean vector style. No watermark.
```
→ 中文标题清晰，英文标签无乱码，视觉效果好

### 更多成功 Prompt 模板

**增长曲线图**：
```
Technical blueprint infographic, dark navy background #0a1628, cyan lines #00d4ff, white text.
Exponential growth curve chart. X-axis: months 0-18, Y-axis: efficiency 1x-5x.
Only ONE large Chinese title at top: 人效5倍增长.
Three milestone dots labeled in English: 30% Auto, 70% Auto, 85% Auto.
Minimal text, maximum visual. No watermark.
```

**对比图**：
```
Technical blueprint infographic, dark navy background #0a1628, cyan lines #00d4ff, white text.
Comparison diagram: Left side Builder (code icon, wrench icon), Right side DRI (shield icon, target icon), large VS in center.
Only TWO large Chinese labels: Builder on left, DRI on right.
English sub-labels below each: Code Design Build vs Decide Own Ship.
Minimal text, maximum visual. No watermark.
```

---

## 适用场景选择

| 配图类型 | 推荐策略 | 原因 |
|----------|----------|------|
| 表格/网格对比 | 结构化网格（策略一） | 单元格内文字少，网格边界约束模型 |
| 流程图/架构图 | 极简中文+英文标签（策略二） | 节点多、连线多，中文太密必乱码 |
| 数据图表 | 极简中文+英文标签（策略二） | 坐标轴/数据点用英文更可靠 |
| 概念图/隐喻图 | 结构化网格（策略一） | 区域划分明确，网格约束有效 |
| 高密度科技图+大量中文 | **分层合成（策略三）⭐** | 中文由浏览器渲染，清晰无乱码 |

⚠️ **用户明确禁止的方案**（2026-06-08 确认）：
- matplotlib/代码绘图 → "代码绘出来的结果效果非常差，这是我明令禁止的"
- Pillow 后贴文字 → "文字本身可能会和后面的图分离，看上去很丑"
- 全英文标注（除专业术语外）→ "除了专业的词语，其他不能用英文"
- 简化内容降低密度 → "太丑了...不要重新简化成这么简单的内容"

---

## 策略三：分层合成（⭐推荐，2026-06-08 新增）

当需要**高密度科技蓝图风格 + 大量中文标注**时，以上两种策略都无法满足。唯一可行方案：将信息图拆为两层，分别用最适合的工具处理。

| 层 | 工具 | 负责内容 |
|---|------|---------|
| 视觉层 | gpt-image-2 | 科技蓝图背景、图标、线条、网格、图表形状 |
| 文字层 | HTML/CSS + Playwright 截图 | 中文标题、标签、描述、指标数据 |

### 工作流

1. **gpt-image-2 生成纯视觉背景**：prompt 中明确 `NO TEXT, NO LETTERS, NO CHARACTERS`
2. **HTML/CSS 叠加中文文字**：PingFang 字体 + 发光 text-shadow + 半透明卡片
3. **Playwright 截图合成**：1536x1024 精确尺寸，输出 JPEG

### 文字与背景融合的关键

用户拒绝"后贴膏药"感。融合靠 CSS 设计：
- `text-shadow: 0 0 20px rgba(0,212,255,0.5)` — 文字发光，呼应科技背景
- `background: rgba(10,22,40,0.7)` — 半透明卡片，透出背景纹理
- `border: 1px solid rgba(0,212,255,0.4)` — 边框颜色呼应背景线条
- 精确坐标定位，每个文字元素配合背景图的节点位置

### 文字语言规则

- 专业术语用英文：DRI、Builder、AI Agent、VS、Auto
- 描述性文字必须中文：标题、标签、说明、指标单位

详见：`references/layered-html-playwright-image-gen.md`

## 实践经验

- 表格网格最多5列，超过会拥挤
- 四象限每块内容不超过4条
- 标题用"标题大字：XXX"明确标注
- 生成后用 PaddleOCR 验证内容是否匹配 prompt，不匹配立即重生
- 极简中文策略下，中文标题控制在3-5个字，超过5个字容易出问题
