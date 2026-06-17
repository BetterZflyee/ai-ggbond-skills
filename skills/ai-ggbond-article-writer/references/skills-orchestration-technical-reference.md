# Skills 编排技术参考

> 来源：2026-06-05 飞哥关于 Skills 编排的深度讨论
> 用途：写 AI Agent / Skills 相关文章时的技术参考

## Claude Code 自动触发机制

**核心原理**：LLM 推理驱动，不是算法匹配。

- Skill 是 tools 数组中的**元工具**（叫 `Skill`，大写 S）
- description 是 Claude 判断是否调用的**唯一信号**
- 没有正则、没有嵌入向量、没有关键词匹配
- Claude 用自己的语义理解来判断是否需要调用某个 Skill

## 描述写法与激活率

650 次实验结果（Ivan Seleznov, 2026-02）：

| 描述风格 | 激活率 |
|----------|--------|
| 被动描述（"Use when..."） | 37% |
| 扩展关键词（"...or any X-related task"） | ~50% |
| 指令式描述（"ALWAYS invoke...Do not X directly"） | 100% |

**公式**：`正面路由（ALWAYS invoke）+ 负面约束（Do not X directly）`

示例：
```
❌ 失败：Docker expert for containerization. Use when creating Dockerfiles...

✅ 成功：Docker and containerization expert. ALWAYS invoke this skill when 
the user asks about Docker, Dockerfiles, containers. Do not attempt to write 
Dockerfiles directly — use this skill first.
```

## 渐进式加载（三层）

| 层级 | 内容 | 加载时机 | Token 成本 |
|------|------|----------|-----------|
| Level 1 | name + description | 始终在 tools 数组中 | ~100 tokens |
| Level 2 | SKILL.md body | Skill 被触发时 | <5000 tokens |
| Level 3 | scripts/、references/、assets/ | 被引用时才加载 | 按需 |

## 链式触发

**机制**：隐式 LLM 推理，不是显式 DAG 编排。

- Skill A 执行完毕后，Claude 根据上下文判断是否需要调用 Skill B
- 没有显式的"下一步"字段，靠 LLM 推理
- 可以在 SKILL.md 里写提示增强判断（如"完成后如果需要翻译，建议调用 translation skill"）

**概率问题**：链式触发是概率相乘。如果每步激活率 90%，5 步下来只有 59%。

## 编排方案对比

| 方案 | 复杂度 | 可靠性 | 适用场景 |
|------|--------|--------|----------|
| Orchestration Skill + 用户确认 | 低 | 高 | 最推荐，先跑通再扩展 |
| 2 个 Skills 链式触发 | 低 | 中高 | 最简单的链式场景 |
| 外部脚本编排（Cron/Webhook） | 中 | 高 | 需要确定性的场景 |
| LangGraph/CrewAI DAG 编排 | 高 | 高 | 复杂多步骤工作流 |

## 开源项目参考

| 项目 | 地址 | 定位 |
|------|------|------|
| skill-creator | Anthropic 官方 | 元技能，编排其他 Skills |
| ai-maestro | github.com/23blocks-OS/ai-maestro | AI Agent Orchestrator with Skills System |
| Multi-AI-Workflow | github.com/haoyu-haoyu/Multi-AI-Workflow | Multi-AI orchestration for Claude Code |
| CAS | github.com/codingagentsystem/cas | Multi-agent orchestration for Claude Code |
| multi-agent-ralph-loop | github.com/alfredolopez80/multi-agent-ralph-loop | Autonomous orchestration framework |
| amux | github.com/andyrewlee/amux | TUI for parallel coding agents |
| AgenticX | github.com/DemonDamon/AgenticX | Unified multi-agent platform（支持飞书/微信） |

## Hermes Agent 状态

- 当前：不支持原生链式触发，Skills 在系统提示中（~4000 tokens）
- 开发中：Issue #37227 三层智能索引 + search_skills() 工具
- 自动触发：Issue #3879 keywords/triggers 字段

## 核心洞察

> "完整的自动编排确实很难，甚至可以说目前没有人真正做好了。"
> 
> "与其追求'完美的自动编排'，不如接受'半自动'模式。"
> 
> "先别想'完整的调度系统'，先想'最常做的 3 件事'。"
