---
name: ai-ggbond-design-spec
description: AI朱朱侠设计规范引擎。任何海报/品牌/产品/网页/UI/社媒/电商视觉需求，先查 design-kb 知识库定风格（首选+备选+必须先问的反问），再产出含具体数值的设计规范和可执行生图提示词。当用户说"按 design-kb 推荐风格""这个海报用什么风格""做个视觉规范""设计规范""配图风格""该用什么风格""visual spec"或提任何设计/视觉需求时触发。
version: 1.0.0
author: AI朱朱侠
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [design, visual, style, spec, prompt, design-kb, branding, ui, poster]
    category: creative
    related_skills: [ai-ggbond-image-gen, ai-ggbond-long-image-generator, ai-ggbond-poster-portrait, ai-ggbond-sticker-writer, ai-ggbond-article-writer]
triggers: ["按 design-kb 推荐风格", "设计规范", "这个海报用什么风格", "视觉规范", "配图风格", "该用什么风格", "帮我定风格", "visual spec", "设计风格推荐", "用什么设计风格"]
---

# AI朱朱侠设计规范引擎

**本技能不出图。** 它只做两件事：从 design-kb 知识库**决定长什么样**，以及**把要求写成 AI 能执行的具体话**。出图交给 `ai-ggbond-image-gen` / `ai-ggbond-long-image-generator` / `ai-ggbond-poster-portrait`。

## 知识库位置（唯一权威，不复制内容）

```
/Users/zhufei/.dsh/bot/workspace/design-kb/
```

**本技能不内联任何风格数据。** 所有风格特征、配色、雷区、提示词一律现查现读，理由：知识库会更新（加风格/改提示词/修核验状态），内联副本一定过期，过期副本比没有更糟。

| 要什么 | 读哪个文件 | 关键字段 |
|---|---|---|
| 场景→风格路由 | `data/route.json` | `trigger` / `primary` / `alt` / `question` / `note` |
| 风格完整特征 | `data/styles.json` | `visual` / `palette` / `typo` / `caution` / `sites` / `family` |
| 现成生图提示词 | `data/top10.json` | `prompt` / `core` / `pro` / `con` / `ref` |
| 混搭组合 | `data/combos.json` | `name` / `logic` / `visual` / `prompt_extra` |
| 受众依据 | `data/audience.json` | `seg` / `evidence` / `note` |
| 参考网站 | `data/sites.json` | `name` / `url` / `verify` / `verify_level` |
| 网站↔风格 | `data/site-style-map.json` | 站名 → 风格名数组 |
| 接入说明 | `如何引用本知识库.md` | 四段输出格式、红线 |

**读之前先确认文件存在**（`ls` 一下）。知识库不在就直说「design-kb 未找到，请确认路径」，**不要靠记忆编风格特征**。

---

## 执行入口：有脚本就别手搓

本技能自带 `scripts/advise.py`，**优先跑脚本**（它已经实现了路由匹配、缺口兜底、四段输出、红线附加）：

```bash
S=~/.agents/skills/ai-ggbond-design-spec/scripts/advise.py

python3 $S "做一张电商主图"          # 标准四段输出
python3 $S --json "做一张电商主图"    # JSON，程序化调用
python3 $S --style clean-app         # 查某风格完整规格
python3 $S --list                    # 16 风格 / 13 路由 / 6 组合
python3 $S --doctor                  # 知识库体检
```

**退出码：`0`=命中或成功 · `1`=未命中路由（需人工判断，不是报错）· `2`=知识库缺失或数据损坏。**

`1` 和 `2` 的处理方式不同：`1` 要追问用户补约束，`2` 要报「知识库不可用」并停止——**不许在 `2` 的情况下凭记忆编风格**。

脚本只是加速手段。它的输出若有缺失（比如你用 `--style` 查了风格但还需要组合方案），仍按下面五步手工补全。

---

## 核心流程（五步，顺序不可跳）

### 第 1 步 · 定约束（缺失就问，别猜）

必须问清的五件事，**一次问完，不要挤牙膏**：

1. **交付物类型**：海报 / PPT / 官网 / UI 界面 / 长图 / 社媒封面 / 包装 / 视频帧？
2. **投放渠道与尺寸**：公众号首图 2.35:1 / 小红书 3:4 / 电商主图 1:1 / 网页 16:9？
3. **受众是谁**：B端决策者 / 消费者 / Z世代 / 专业用户？
4. **要传递什么情绪**：理性可信 / 冲击吸睛 / 温暖亲和 / 高级克制？
5. **有没有现成的品牌色/字体/设计系统**？

**若用户没给，按飞哥历史基线垫底，并明确标注「这是我按你的历史偏好替你定的」：**

- 主色：白底为主，**不用深色主题**（PPT 尤其）
- 点缀色：品牌红 `#E41E2C`，**仅作点缀，绝不做主色**
- 配图：学术风高密度信息图（像论文 Figure），拒绝科普风 PPT 图
- 文章配图：白底黑字高留白 + 少量技术蓝

### 第 2 步 · 查库路由（禁止跳过直接给结论）

```python
import json
KB = "/Users/zhufei/.dsh/bot/workspace/design-kb"
route  = json.load(open(f"{KB}/data/route.json",   encoding="utf-8"))
styles = {s["key"]: s for s in json.load(open(f"{KB}/data/styles.json", encoding="utf-8"))}
top10  = {t["key"]: t for t in json.load(open(f"{KB}/data/top10.json",  encoding="utf-8"))}
combos = json.load(open(f"{KB}/data/combos.json", encoding="utf-8"))
```

**匹配规则（按优先级）：**

1. 用需求原文逐条比对 `trigger` 词数组，命中即取该条的 `primary` + `alt` + `question`
2. 命中多条时，取**命中词最多**的那条（例如「电商主图」同时命中「电商」和「主图」，取同一条）
3. **一条都没命中**：不要硬套。从 `styles.json` 的 `family`（克制型/秩序型/氛围型/叙事型/亲和型/反叛型/复古型）按情绪反向挑 2-3 个候选，并说明「未命中路由，按风格族反查」

**必须同时给出 `question` 字段里那句反问。** 13 个场景里 11 个有真实分叉（潮 vs 高级、产品 vs 数据、冲击 vs 质感），直接给唯一答案必然返工。

### 第 3 步 · 取规格与雷区

命中的 `primary` 和每个 `alt`，都从 `styles.json` 取这五个字段：`visual` / `palette` / `typo` / `caution` / `sites`。

**`caution` 必须原样呈现给用户**，这是本库最有价值的部分——它是踩过的坑，不是免责声明。

### 第 4 步 · 出提示词（组合而非套用）

**优先级：`top10.json` 的 `prompt` → 没有则用 `styles.json` 特征拼装 → 需要混搭则叠加 `combos.json` 的 `prompt_extra`。**

**⚠️ 覆盖缺口（必读）：`top10.json` 只有 10 条提示词，而 `styles.json` 有 16 种风格。以下 6 种没有现成 prompt，必须用特征拼装，不许说"没有模板"：**

| 无 prompt 的风格 | 拼装依据（读 styles.json 对应字段） |
|---|---|
| `minimal` 极简主义 | `visual` 留白+细线+单色块；`palette` 白/近白+#111+单一强调 |
| `glass` 玻璃拟态 | `visual` 磨砂层+背景模糊+1px 白内描边；**必须附带对比度警告** |
| `y2k` 千禧复古 | `visual` 金属+气泡高光+扫描线；`palette` 银灰+荧光青/品红 |
| `motion3d` 动态三维 | `visual` PBR 材质+物理光照；注意 AI 生成常塑料感 |
| `collage` 解构拼贴 | `visual` 剪贴重组+撕裂边缘+错位叠压 |
| `retro-print` 复古印刷 | `visual` 套色错位+网点颗粒+油墨溢出 |

**另注：`collage` / `glass` / `y2k` 三种风格在 13 条路由里既不是首选也不是备选**，只会在「按风格族反查」或用户点名时用到。

**拼装公式（必须带齐五项，缺一项不合格）：**

```text
【任务】为 {对象} 设计 {交付物类型}
【风格】{style.name}（风格族：{style.family}；副风格：{可选}）
【配色】{style.palette 拆成具体色值}
【字体】标题 {字体} {字号}px/字重 {数值}/字距 {数值}；正文 {字体} {字号}px/行高 {数值}
【版式】栅格 {列数} 列；外边距 {数值}px；模块间距 {数值}px；圆角 {数值}px
【内容】{具体要放什么}
【禁止】{负向清单，见下}
```

### 第 5 步 · 自查（交付前逐条过）

- [ ] 风格是从 `route.json` 按场景选的，不是拍脑袋？
- [ ] 给了首选 + 1-2 个备选，不是唯一答案？
- [ ] 附上了那句必须先确认的反问？
- [ ] 说明了「为什么选这个风格」（受众 + 场景 + 避开了哪个雷）？
- [ ] 提示词里色值/字号/行高/间距/圆角**全部是具体数字**？
- [ ] 带了负向清单？
- [ ] `caution` 原样呈现了？
- [ ] 没有踩米白+陶土、科技暗色发光这两个雷？

---

## 输出格式（固定四段，少一段就是没做完）

```
✅ 首选：{风格名}（{风格族}）
   配色：{具体色值}
   字体：{字体} {字号}/字重 {数值}
   版式：{栅格} / 外边距 {数值}px / 圆角 {数值}px
   ⚠️ 已知风险：{styles.json 的 caution 原文}
   参考站：{sites 前 2-3 个}

◻ 备选：{1-2 个，各一句为什么可能更合适}

❓ 反问：{route.json 的 question 原文}

🎯 提示词（可直接喂生图技能）：
{完整拼装后的 prompt}
```

---

## 三条硬性红线（违反即返工）

1. ⚠️ **永不推荐「米白底 `#F5EFE6` + 陶土色 `#C67B5C` + 无衬线大标题」**。飞哥明确否决过，这是 AI 味识别符。用 `warm-natural` 时必须换成真实摄影 + 独特排版破局。
2. ⚠️ **科技暗色（`tech-dark`）必须附风险提示**，且默认降级为「去特效版」——不要发光边框、不要光束、不要粒子星空。
3. ⚠️ **提示词必须含具体数值**。禁止「高级一点」「大气一些」「有质感」这类空话——AI 理解不了，只会返回它自己的默认审美。

## 万能负向清单（附加到任何 prompt 末尾）

```text
【禁止】米白底 #F5EFE6 + 陶土色 #C67B5C 的组合；深色底 + 发光边框 + 光束特效；
卡片内再套卡片；「01 / 02 / 03」式编号小标题；斜体衬线大标题配细字重；
提示框左侧一根彩色竖条；无来源的环境光与发光；过度圆角（>16px）配大阴影；
彩虹式多色数据图；居中对称却无层级的标题堆叠；纯装饰性图标（不带信息量）。
```

---

## 与其它技能的边界

| 技能 | 负责什么 | 与本技能的关系 |
|---|---|---|
| **本技能** | 定风格、出规格、写提示词、自查 | **不出图** |
| `ai-ggbond-image-gen` | 调 GPT-Image-2 出图 | 本技能的下游，吃本技能产出的 prompt |
| `ai-ggbond-long-image-generator` | 长图/信息图 | 本技能的 `data-viz` 风格直接喂给它 |
| `ai-ggbond-poster-portrait` | 女性肖像海报 | 本技能的 `film` 提供布光与调色参数 |
| `ai-ggbond-sticker-writer` | 微信贴图排版 | 本技能的 `editorial` 提供排版节奏 |
| `ai-ggbond-article-writer` | 写文章 | 本技能提供配图风格方向 |
| `gpt-image-2-style-library` | 外部 awesome-gpt-image-2 风格库 | **不重叠**：它是通用 GPT 风格模板，本技能是飞哥专属的知识库路由 |

**推荐链路：**

```
需求 → 本技能 route.json 定风格 → styles.json 取配色/字体/雷区
     → top10.json 取提示词（缺则按特征拼装）
     → 交给 ai-ggbond-image-gen 出图
     → 出图后按 Vercel 规范 / Impeccable 62 项自查
```

---

## 诚实边界（不许含糊）

- 知识库只有 **16 种风格 / 13 条场景路由 / 10 条现成提示词**。需求超出覆盖范围时，**直说「知识库没有直接对应的风格」**，然后按风格族反查或新造组合并说明理由，不要假装命中。
- `sites.json` 里每条有 `verify_level` 和 `verify` 字段。**引用站点时若 `verify_level` 是 C 或说明里带「已修正/失效」，必须把状态一并告诉用户**，不许把未核验的站当已确认事实。
- `audience.json` 里 `note` 字段标了「推测」的，引用时说明这是推测。

---

## 📝 版本迭代记录

| 版本 | 日期 | 更新内容 | 操作人 |
|------|------|---------|--------|
| v1.0.0 | 2026-11-17 | 创建。基于 design-kb（16 风格/13 路由/10 提示词）建规范引擎，补 6 种无 prompt 风格的拼装兜底与 3 种未入路由风格的说明 | 朱飞 |
