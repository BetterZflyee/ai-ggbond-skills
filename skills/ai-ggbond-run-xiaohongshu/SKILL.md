---
name: ai-ggbond-run-xiaohongshu
version: 2.0.0
author: "AI朱朱侠 (Felix Zhu)"
description: "小红书全链路运营技能 — 即插即用，任意用户通过 Hermes Memory 自动适配。覆盖账号定位、选题研究、内容生产、发布执行、评论回复、爆款复刻与复盘沉淀。核心理念：你是谁，我读你的 Memory；你该发什么，我结合你的定位分析。"
trigger_keywords: ["小红书", "xhs", "小红书运营", "小红书发布", "小红书分析", "小红书选题", "小红书评论", "小红书复刻", "爆款笔记", "账号分析"]
---

# ai-ggbond-run-xiaohongshu — 即插即用 · Memory驱动小红书运营

## 一句话说明

**你是谁，我读你的 Memory。你该发什么，我结合你的定位分析。**

换个用户，换套 Memory，同样的 skill 给出完全不同的分析结论和内容——因为结论是从「你」推导出来的，不是从模板抄出来的。

---

## 0) 启动时自动加载用户上下文（核心机制）

**执行任何小红书操作前，skill 自动完成以下步骤——对使用者完全透明：**

### Step 0.1: 从 Hermes Memory 读取「你是谁」

Memory 在每次对话中已自动注入到上下文。Skill 启动时从中提取：

```
User Profile → 你的身份画像:
  - 核心身份：你是做什么的？（AI从业者/设计师/投资人/创业者/学生...）
  - 当前主线：你正在推进什么？（求职/副业/个人IP/学习/创业...）
  - 风格偏好：你喜欢什么调性？（专业严谨/幽默风趣/温暖治愈/犀利直接...）
  - 内容平台：你是否已有公众号/小红书/其他社交媒体？定位是什么？

Memory → 你的经验与边界:
  - 近期优先级：现在最重要的是什么？
  - 专业领域：你最擅长/最有积累的是什么？
  - 红线禁忌：什么话题绝对不能碰？
  - 已有案例：你做过什么、验证过什么？
```

**如果 Memory 中信息不足，skill 会主动问——不会假装知道。**

### Step 0.2: 从 Memory 构建你的 Persona

Persona 不来自预设模板——**来自你的 Memory**：

| Persona 要素 | 来源 |
|-------------|------|
| 身份定位 | User Profile → 核心身份 + 专业领域 |
| 口语风格 | User Profile → 风格偏好 + 过往对话风格 |
| 内容支柱 | Memory → 专业领域 + 已有经验 |
| 话题边界 | Memory → 红线禁忌 + 近期优先级 |
| 视觉偏好 | User Profile → 内容偏好 |

**可选覆盖：** 如果你说「用更轻松的语气」，Skill 在 Memory 基础上叠加轻松风格。但这只是微调——核心身份依然来自 Memory。

### Step 0.3: 构建运行时上下文（内部使用）

```yaml
runtime_context:
  identity: "从你的 Memory 自动提取"
  goals: ["从你的 Memory 自动提取"]
  expertise: ["从你的 Memory 自动提取"]
  tone: "从你的风格偏好自动推断"
  content_pillars: ["从你的专业领域自动推导"]
  forbidden: ["从你的红线禁忌自动提取"]
  xhs_account: "如有小红书链接则记录"
```

---

## 1) 能力矩阵

| 能力 | 怎么触发 | 核心流程 |
|------|---------|---------|
| 首页推荐流分析 | "分析我小红书首页推荐流" | `references/xhs-home-feed-analysis.md` |
| 账号分析 | "分析这个账号" | `references/xhs-account-analysis.md` |
| 选题灵感 | "给我几条小红书选题" | `references/xhs-topic-ideation.md` |
| 爆款复刻 | "复刻这篇爆款" | `references/xhs-viral-copy-flow.md` |
| 写笔记 | "帮我写一篇小红书笔记" | 本文第4节 |
| 发布 | "帮我发布" | `references/xhs-publish-flows.md` |
| 评论回复 | "检查并回复评论" | `references/xhs-comment-ops.md` |
| 知识沉淀 | "沉淀到知识库" | `references/xhs-knowledge-base.md` |
| 搜索浏览 | "搜索xxx相关笔记" | `references/xhs-runtime-rules.md` |

**每个能力都会自动注入你的 Runtime Context——不需要每次重复说明「我是谁、做什么的」。**

---

## 2) 环境与浏览器

- 使用 Hermes CDP 浏览器工具链：`browser_navigate` / `browser_snapshot` / `browser_click` / `browser_type` / `browser_console`
- 首次需在小红书页面扫码登录，后续复用登录态
- 优先 `browser_snapshot()` 轻量获取页面结构，减少完整加载
- 每个操作最多重试 1 次；失败改稳健路径并汇报

### 工具映射

| OpenClaw 原版 | Hermes 适配 |
|--------------|------------|
| `browser.start --profile openclaw` | `browser_navigate("https://www.xiaohongshu.com")` |
| `evaluate(script)` | `browser_console(expression=script)` |
| `snapshot` | `browser_snapshot()` |
| `click(ref)` | `browser_click(ref)` |
| `type(ref, text)` | `browser_type(ref, text)` |
| `open(url)` | `browser_navigate(url)` |
| `browser.upload` | Hermes 暂不支持，告知用户手动操作 |

---

## 3) Memory 如何改变每次分析

### 3.1 账号分析时

```
普通技能：
  "这个账号定位清晰度 4/5，它做对了ABC..."

本技能（读完你的 Memory 后）：
  "这个账号定位清晰度 4/5。
   你的定位是 {从Memory提取的身份}，目前在 {从Memory提取的目标}。
   对比来看：
   - 你可学的：它的 {具体做法} 适配你的 {具体场景}
   - 不适合你的：它的 {具体做法} 与你的 {红线/定位} 冲突
   - 你可改进的：用你的 {专业优势} 做类似的 {内容形式}"
```

### 3.2 选题时

```
普通技能：
  "给你 5 条选题：1.xxx 2.xxx 3.xxx..."

本技能（读完你的 Memory 后）：
  "给你 5 条选题，按与你的适配度排序：

   1. ★★★★★ {标题} — 高度契合你的 {专业领域} 定位，
      可以复用你已有的 {经验/案例}
   2. ★★★★☆ {标题} — 服务于你当前的 {首要目标}
   3. ★★☆☆☆ {标题} — 部分相关但需大改口吻
   4. ★☆☆☆☆ {标题} — 热点但不适合你，建议跳过
   5. ☆☆☆☆☆ {标题} — 与你的定位无关，不推荐"
```

### 3.3 评论回复时

```
普通技能：
  "回复：收到，谢谢关注～"

本技能（读完你的 Memory 后）：
  根据你的风格偏好 {从Memory提取的语气}：
  - 如果你的风格是专业严谨 → "好问题。核心逻辑是：___"
  - 如果你的风格是温暖治愈 → "看完你的留言好感动～___"
  - 如果你的风格是犀利直接 → "一句话：___，别的不用管"
```

---

## 4) 内容生成模板

每次产出至少 2 个备选，每个都过 Persona 自检：

- 标题：有立场/争议/反问，≤20字优先
- 开头钩子：1-2句抓人
- 正文：3段（观点→证据→延伸）
- 互动提问：1句引导评论
- 话题：5-8个
- **自检**：这段话像不像「你」会说的话？
- **风险标注**：是否踩线

---

## 5) 发布链路

执行 `references/xhs-publish-flows.md`（Hermes 适配版）。

强制检查：
- 三要素齐全：封面、标题、正文
- 标题 ≤20 字
- 到达「发布」按钮停手，用户确认后再点

---

## 6) 评论与回复

执行 `references/xhs-comment-ops.md`。

Memory 增强：
- 回复语气来自你的 Memory 风格偏好
- 高风险评论（辱骂/钓鱼/隐私请求）统一防御策略
- 优质回复可选沉淀到 knowledge-base

---

## 7) 爆款复刻

执行 `references/xhs-viral-copy-flow.md`。

Memory 增强：
- 复刻前检查源笔记与你的 Persona 兼容性
- 不兼容时保留结构，替换语气/案例/观点
- 复刻结果过 Persona 自检

---

## 8) 知识库 + Memory 双写

执行 `references/xhs-knowledge-base.md`。

高价值结论双写：
- 本地 knowledge-base：完整记录（证据、URL、截图）
- Hermes Memory：精简摘要 `[XHS-*]` 前缀，跨会话检索

---

## 9) 失败降级

- 自动化失败先重试一次
- 仍失败改稳健路径
- 不做无效重复；保留进度，报告用户需手动的步骤

---

## 10) 输出规范

- 优先「能对话」而非「写报告」
- 所有分析必须包含「对你意味着什么」
- 不编数据、不虚假承诺、不做与用户定位无关的热点

---

## 附录

### 风格微调（可选）

如果你对自动推断的语气不满意，可以说：
- 「用更轻松的语气」
- 「保持专业但加一点幽默」
- 「像写公众号那样深度一些」

这只是微调——你的核心身份和定位永远来自 Memory。

### 依赖
- Hermes CDP 浏览器工具
- Hermes Memory 系统（自动读取）
- Hermes 文件系统

### 基于
- 运营框架参考 `Xiangyu-CAS/xiaohongshu-ops`（MIT License）
- 增强：Memory 集成、Hermes 适配、通用 Persona 系统
