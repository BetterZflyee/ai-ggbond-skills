# GitHub Trending / Agent 文章配图工作流案例（2026-05-25）

## 场景
用户确认 GitHub Trending / AI Agent 趋势长文后，要求“确认风格和配图”，随后指定：

- 风格：方案一，暖米白手绘高密度信息图风格
- 数量：每个章节最好 1 到 2 张配图
- 模型：严格 `gpt-image-2`，不可擅自切换

## 推荐配图清单
对 6 章节趋势长文，建议 10 张图：

1. `cover.png`：公众号封面，标题图，不放正文
2. `infographic.png`：全文核心信息图，正文开头
3. `01-github-trending-intro.png`：GitHub Trending 科普图
4. `02-code-understanding.png`：代码理解课（codegraph / Understand-Anything）
5. `03-long-term-memory.png`：长期记忆课（agentmemory）
6. `04-engineering-discipline.png`：工程纪律课（superpowers）
7. `05-professional-workflow.png`：专业工作流课（academic-research-skills）
8. `06-software-calling.png`：软件调用课（CLI-Anything）
9. `07-ecosystem-plugins.png`：生态扩展课（cursor/plugins）
10. `08-call-to-action.png`：结尾号召图

## 风格提示词底座

```text
创建一张微信公众号文章配图。整体风格：暖米白手绘高密度信息图，手账风格，暖米白背景 #FAF7EF，深炭黑文字，陶土橙、鼠尾草绿、暖灰、少量技术蓝点缀。线条有自然手绘抖动感，不等粗细，虚线连接模块，便签卡片、课程表、课堂黑板、箭头、图标组合。画面信息密度高但清晰，模块之间有足够留白。所有文字必须是简体中文，文字清晰、标准、无乱码、无变形、无重影。禁止英文大段文字。禁止生成任何水印、署名、Logo、角标、作者名、“AI朱朱侠”文字。
```

## 生图耗时与续跑策略（2026-05-25 实战）

### 真实耗时基准

gpt-image-2 批量生成 10 张图，实际耗时约 30-40 分钟。

- 单张生成 2-5 分钟
- 每张间隔 15-20 秒防限流
- 如遇 429 触发重试（最多 3 次 × 300s），单张可膨胀到 10 分钟以上
- 10 张全量正常跑完 ≈ 35 分钟

### 会话重启砍进程（重要坑）

如果 Hermes 会话中重启、模型切换或上下文压缩，后台 Python 进程可能被杀死，已生成的图片不会丢失。

症状：
- 进程 status 变为 `exited`，`exit_code` 为 null 或非零
- `images/` 下文件数量 < 目标数量

标准续跑策略：
1. 检查 `images/` 下已有哪些文件
2. 写续跑脚本，用 `if path.exists() and path.stat().st_size > 10000: continue` 跳过已生成项
3. 只对缺失图片调用 generate
4. 间隔可缩短到 15 秒（续跑图片少，限流风险低）

续跑脚本模板见本次生成脚本 `images/prompts/resume_remaining_5.py`。

### 进度汇报规范

长耗时生图任务（>3 张），不能只回复"正在跑"。
每次用户询问进度时，必须汇报：
- 已完成 / 总数
- 每张文件名、大小、尺寸
- 预计剩余时间
- 进程状态（running/exited/error）

1. 生图前必须确认：风格、数量、封面标题、模型。
2. 用户确认后，先写入 `images/prompts/image-plan.md` 和生成脚本，再调用 API。
3. 使用 `gpt-image-2`。如果 API 或模型不可用，暂停并汇报，不得切换模型。
4. 批量生成多张图时建议每张间隔约 20 秒，避免限流。
5. 生成后检查文件存在、大小、尺寸；发布前用 PaddleOCR/OCR 检查中文标题和核心标签。
6. 如果 Feishu/对话澄清工具不可用，不要误判为生图失败；直接文字确认并继续执行。

## 本次落地路径示例

- 文章目录：`/Users/admin/SuperIp/article/202605250930-github-trending-agent补课/`
- 配图计划：`images/prompts/image-plan.md`
- 生成脚本：`images/prompts/generate_warm_handdrawn_images.py`
