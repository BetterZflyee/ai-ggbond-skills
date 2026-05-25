# 2026-05-21 Antigravity 文章标题与配图工作流复盘

## 背景
用户让基于 X 关注流中的 Google Gemini CLI → Antigravity CLI 迁移事件写公众号文章，并要求后续生成配图；生成配图前明确要求先确认配图信息。

## 标题经验
用户给出的主标题：
《我越来越确定：AI 工具的下一站，不是更聪明，而是接管工作流》

副标题：
从 Gemini CLI 迁移到 Antigravity CLI，看懂 AI 编程工具真正的转折点

关键偏好：标题要突出“我”的判断，而不是写成新闻标题或第三方行业报告。对 AI朱朱侠公众号而言，热点事件只是药引子，标题要传达“我观察到 / 我越来越确定 / 我的判断是”的个人 IP 视角。

可复用标题公式：
- 《我越来越确定：[趋势判断]》
- 《我越来越确定：[对象]的下一站，不是[A]，而是[B]》
- 副标题用“从[事件]，看懂[本质转折]”承接事实锚点

## 配图确认经验
用户确认前，不得直接生图。确认项至少包括：
1. 风格方案（如专业科技蓝信息图 / 手绘信息图 / 混合风格）
2. 图片数量与清单
3. 封面标题文字
4. 使用模型（默认严格 gpt-image-2，不擅自切换）

本次用户确认：
- 风格：A，专业科技蓝信息图风格
- 数量：7 张
- 封面标题：AI 工具的下一站，不是更聪明，而是接管工作流

## 已采用图片清单模板
1. cover.png：封面图
2. infographic.png：全文核心信息图
3. 02-tool-vs-platform.png：工具 vs 平台
4. 03-copilot-vs-agent.png：Copilot vs Agent
5. 04-agent-runtime-architecture.png：Agent Runtime 三层架构
6. 05-control-and-quota.png：开发者焦虑：API Key 可控 → 平台配额黑箱
7. 06-workflow-assets.png：工具依赖和工作流资产分开

## 生图执行注意
- 先在文章目录 images/prompts/ 下保存 image plan 与生成脚本，避免提示词散落。
- 通过 `YunwuImageGenerator.generate(prompt, model='gpt-image-2', size='1792x1024')` 逐张生成。
- 批量 7 张建议后台执行，每张间隔约 20 秒。
- 生成后必须验证文件存在、大小合理，并再把 Markdown 图片引用插入正文；不要只说“后台跑完后再看”。
