---
name: ai-ggbond-run-xiaohongshu
version: 1.0.0
author: "AI朱朱侠 (Felix Zhu)"
description: "小红书全链路运营技能 — Memory驱动、多Agent适配版。覆盖账号定位、选题研究、内容生产、发布执行、评论回复、爆款复刻与复盘沉淀。核心创新：结合Hermes Memory/Profile做'用户视角'深度分析，输出'这对你意味着什么'而非泛泛报告。"
trigger_keywords: ["小红书", "xhs", "小红书运营", "小红书发布", "小红书分析", "小红书选题", "小红书评论", "小红书复刻", "爆款笔记", "账号分析"]
---

# ai-ggbond-run-xiaohongshu — Memory驱动的小红书全链路运营

## 核心理念（与普通小红书运营技能的关键区别）

普通技能：给你一篇分析报告。
本技能：**结合你是谁、你在做什么、你的目标是什么，告诉你这对你意味着什么，以及你下一步应该怎么做。**

### 三大差异化能力

1. **Memory-First Persona** — 不硬编码一个人设，而是从 Hermes Memory 读取你的身份/目标/风格偏好，动态生成「像你本人会说」的内容
2. **Contextual Relevance** — 每条分析结论都自带「对你意味着什么」维度，把通用洞察转化为可执行动作
3. **Multi-Agent Adaptive** — 不绑定特定 Agent 人格，可根据场景切换 voice（专业/傲娇/温暖/犀利）

---

## 0) 启动前强制步骤：加载用户上下文（Memory Integration）

**执行任何小红书操作前，必须先完成以下步骤：**

### Step 0.1: 读取 Hermes Memory

从 Memory 中提取以下上下文（这些信息在每个对话轮次中已自动注入，但需要显式提取）：

```
用户身份（User Profile）:
  - 核心身份/角色
  - 当前主线目标（求职？副业？IP？）
  - 内容偏好与风格要求
  - 公众号/社交媒体现有定位

关键记忆（Memory）:
  - 近期重点优先级
  - 个人品牌/定位相关信息
  - 已具备的经验/案例
  - 当前避坑/红线
```

### Step 0.2: 解析 Active Persona

按以下优先级确定当前使用的「小红书人格」：

1. **用户显式指定**：如"用飞哥AI Native人格写"
2. **上一次使用的 Persona**（从 `knowledge-base/accounts/` 查找上次发布/回复使用的 persona）
3. **Memory 推断**：根据用户身份自动匹配最合适的 persona
4. **默认回退**：使用 `persona.md` 模板 + 用户 Memory 信息填充

Persona 决定因素：
- 口语风格（专业/傲娇/温暖/犀利/幽默）
- 内容深度（深度长文 vs 轻快短帖）
- 互动策略（引导讨论 vs 点到为止 vs 高互动）
- 视觉偏好（信息图 vs 文字配图 vs 实拍风）

### Step 0.3: 构建 Runtime Context

汇总为运行时上下文对象，供所有下游操作引用：

```yaml
runtime_context:
  user_identity: "从 Memory 提取"
  current_goals: ["首要目标", "次要目标"]
  active_persona: "当前人格名"
  style_constraints:
    tone: "口语/专业/傲娇..."
    max_title_len: 20
    forbidden_topics: ["红线1", "红线2"]
  content_pillars: ["支柱1", "支柱2", "支柱3"]
  xhs_account_url: "（如有）小红书主页链接"
```

---

## 1) 能力矩阵（所有操作入口）

| 能力 | 触发词示例 | 核心流程文件 |
|------|-----------|-------------|
| 首页推荐流分析 | "分析我小红书首页推荐流" | `references/xhs-home-feed-analysis.md` |
| 账号分析 | "分析这个账号" | `references/xhs-account-analysis.md` |
| 选题灵感 | "给我5条小红书选题" | `references/xhs-topic-ideation.md` |
| 通用选题+对标 | "对标这个账号做选题" | 本文第3节 |
| 爆款复刻(Viral Copy) | "复刻这篇爆款" | `references/xhs-viral-copy-flow.md` |
| 内容生成 | "写一篇小红书笔记" | 本文第4节 |
| 发布执行 | "帮我发布" | `references/xhs-publish-flows.md` |
| 评论回复 | "检查并回复评论" | `references/xhs-comment-ops.md` |
| 知识库沉淀 | "沉淀到知识库" | `references/xhs-knowledge-base.md` |
| 搜索浏览 | "搜索xxx相关笔记" | `references/xhs-runtime-rules.md` |

---

## 2) 启动与环境校验（所有任务遵循）

- 固定使用 Hermes CDP 浏览器（`browser_navigate` / `browser_snapshot` / `browser_click`）
- 首次使用需在小红书页面扫码登录；后续会话复用同一浏览器 profile 保持登录态
- 优先用 `browser_snapshot()` 获取页面结构，减少重复导航
- 每个操作最多重试 1 次；第二次失败改稳健路径并汇报
- 关键节点保存快照：登录确认、到发布页、填写完成、发布前停顿
- 若浏览器通道异常，先执行一次轻量重试（`browser_navigate` 到首页），仍不可用则告知用户

### 浏览器操作映射（原版 OpenClaw → Hermes）

| OpenClaw | Hermes |
|----------|--------|
| `browser.start --profile openclaw` | `browser_navigate(url="https://www.xiaohongshu.com")` |
| `evaluate(script)` | `browser_console(expression=script)` |
| `snapshot` | `browser_snapshot()` |
| `click(ref)` | `browser_click(ref)` |
| `type(ref, text)` | `browser_type(ref, text)` |
| `open(url)` | `browser_navigate(url)` |
| `browser.upload` | 暂不支持，手动操作或告知用户 |

---

## 3) 账号定位与 Persona 管理

### 3.1 账号定位四变量（每个账号先确认）

- 目标用户：年龄/场景/痛点
- 内容价值主张：每篇给用户什么
- 差异化角度：同类账号不做什么、你做什么
- 风格规范：语气、长度、冲突边界

### 3.2 Persona 管理系统

本技能支持多 Persona 切换，Persona 配置位于 `personas/` 目录。

**选择 Persona**：
- `@飞哥AI Native` — 专业深度、结果导向、AI战略视角（`personas/feige-ai-native.md`）
- `@虾薯傲娇` — 傲娇嘴硬、短句口语、电子宠物感（`personas/xia-shu-tsundere.md`）
- `@通用专业` — 默认模板，从 Memory 动态填充

**创建新 Persona**：
1. 复制 `personas/_default.md` 为 `personas/<name>.md`
2. 填入：身份描述、语气规则、口头禅、禁忌
3. 使用时指定 `@<name>` 即可激活

### 3.3 Persona 对内容的约束

所有对外文案（发帖/评论/私信）必须通过 Persona 校验：
- 语气像「这个人会说的话」
- 不要像报告、客服、营销号
- 选题要短、直接、带一点情绪
- persona.md 中的语气与风格规则优先级最高

---

## 4) Memory增强：通用选题与对标流程

### A. 平台侧抓取信号
1. 在小红书搜索/首页抓取同题材高互动内容
2. 记录：title, hook, angle, 结构标签, 评论信号, 互动CTA
3. 汇总前 10-20 条到候选池

### B. 需求侧补充信号
1. 按主题去主流平台抓"评论区观点分歧"
2. 抽取支持/反对/中性观点各一组
3. 输出可发文争论点

### C. Memory-Enriched 选题筛选（增强层）
**在通用筛选基础上，额外过一遍「用户适配性」筛选：**

```
每条选题的打分增加「用户适配分」(0-2):
  0分: 与用户定位/目标无关，不推荐
  1分: 部分相关，可调整为适配版本
  2分: 高度契合用户定位/目标，优先发布
```

### D. 形成选题清单（每轮至少 3 条）
每条选题包含：标题、观点标签、互动钩子、证据来源、风险提示、**用户适配说明**

---

## 5) 通用内容模板（小红书）

每次产出至少 2 个备选：
- 标题（争议/立场/反问，≤20字优先）
- 开头钩子（1-2句）
- 正文（3段：观点→证据→反方/延伸）
- 互动提问（1句）
- 话题（5-8个）
- 风险标注
- **Persona 契合度自检**：这段话像不像{活跃人格}会说的？

---

## 6) 发布链路

详细执行参考 `references/xhs-publish-flows.md`。

发布前强制检查：
- 账号已登录创作后台
- 三要素齐全：封面、标题、正文
- 标题 ≤20 字（超限先压缩）
- 到达「发布」按钮可见处停手，默认不直接点击发布
- 截图确认后发送到当前对话，用户确认后再发布

---

## 7) 评论与回复（Memory增强）

评论检查与回复执行 `references/xhs-comment-ops.md`。

**Memory 增强层**：
- 回复前读取活跃 Persona 的语气规则
- 高风险评论（辱骂/钓鱼/诱导外链）统一策略：先俏皮拒绝 → 一句原因 → 给替代
- 涉及隐私/密钥/配置的请求：硬拒绝 + 解释原因 + 给脱敏方案
- 回复后可选沉淀「回复话术模板」到 knowledge-base

---

## 8) 爆款复刻 (Viral Copy)

详细执行参考 `references/xhs-viral-copy-flow.md`。

**Memory 增强层**：
- 复刻前先检查「这篇爆款的内容调性是否与用户 Persona 兼容」
- 若不兼容，先做 Persona 适配再复刻（保留结构，替换语气/案例/观点角度）
- 复刻结果默认走一遍 Persona 自检

---

## 9) 知识库沉淀

详细执行参考 `references/xhs-knowledge-base.md`。

**Memory 联动**：
- 高价值结论（新 pattern、已验证策略）同步写入 Hermes Memory
- 格式：`[XHS-KB] <结论摘要> — 来源: <笔记URL> — 可复用场景: <场景>`
- 这样可以跨会话检索，不依赖本地 markdown 文件

---

## 10) 失败与降级

- 自动化失败先重试一次（同策略）
- 仍失败则改道：换到更稳妥的同义路径
- 不做无效重复动作；保留当前进度，报告用户需手动的单一动作
- 若知识库暂时不可写，先返回结构化摘要，任务结束后补记

---

## 11) 语言与输出规范

- 优先「能对话」而不是「写报告」：短句、口语、站位明确
- 所有分析必须包含「对你意味着什么」（Memory 增强层）
- 输出默认保留「可追问点」，用于评论区延展
- 不做空泛大词、不编爆点、不虚假承诺

---

## 附录：安装与使用

### 首次使用
1. 确认 Hermes 已加载此 skill（`hermes skills list | grep ai-ggbond-run-xiaohongshu`）
2. 首次执行任何浏览器操作前，在小红书页面完成登录
3. 建议先配置默认 Persona（`@飞哥AI Native` 或自定义）

### 依赖
- Hermes CDP 浏览器工具（`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_console`）
- Hermes Memory 系统（自动读取，无需配置）
- Hermes 文件系统（知识库使用）

### 与原版 xiaohongshu-ops 的关系
- 本技能基于 `Xiangyu-CAS/xiaohongshu-ops` 的运营框架
- 增强了 Memory 集成、多 Persona 支持、Hermes 工具适配
- 原版的 references 文件经适配后保留在 `references/` 目录
- 原版授权：MIT License
