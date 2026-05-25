# Antigravity CLI 迁移文章案例（2026-05-21）

## 触发场景
用户已经在上一轮确认了公众号选题：Google Antigravity CLI / Gemini CLI 迁移，并明确要求“按照这个标题的内容调用这个技能，完整写出公众号文章内容”。

## 关键处理方式
当用户已经明确选题、标题方向和“完整写出”时，不要机械执行“内容类型确认→3-5个选题→等待选择→框架确认”的慢流程；应进入写作快车道：

1. 仍需先核实事实来源，避免写错热点。
2. 保存 brief 和 knowledge base 到文章目录。
3. 创建标准化文章目录：`/Users/admin/SuperIp/article/YYYYMMDDHHMM-标题/`。
4. 直接产出完整 Markdown 正文。
5. 做基础自检：禁用阅读时长/图注/figcaption/明显 AI 味词。
6. 最终只给文件路径、核心标题建议和一句传播金句，不要重复贴全文。

## 本次核实信息
- Google 正在将 Gemini CLI sunset，迁移到 Antigravity CLI。
- Antigravity CLI 被定义为 agent-first terminal experience，构建在 Google Antigravity 2.0 平台。
- 保留/迁移 Agent Skills、Hooks、Subagents、Extensions（转为 plugins），新增统一后端上的 multi-agent workflows。
- 从 2026-06-18 起，Gemini CLI 和 Gemini Code Assist IDE extensions 停止为 free / Google AI Pro / Ultra 消费级用户服务请求；Enterprise / Standard license 保留访问。
- 开发者争议点：旧 CLI 停止服务、计费/配额不透明、程序化调用和开放协议支持不明、平台锁定风险。

## 陌生化角度
不要写成“Google 发布/关闭了什么工具”的新闻稿，而要写成：

> AI 编程正在从 Copilot 时代进入 Agent 接管时代，真正变化的是开发者工作流的入口和权力边界。

## 可复用文章骨架
- 事件切入：Gemini CLI 迁移到 Antigravity CLI。
- 第一层升番：这不是工具改名，而是入口收编。
- 第二层升番：从 Copilot 到 Agent，本质是从代码生成到反馈闭环。
- 第三层升番：竞争从模型战转向 Agent Runtime / 工作流战争。
- 第四层升番：个人和企业都要从“工具消费者”升级为“工作流所有者”。

## 推荐传播标题
- 《AI编程正在从Copilot进入Agent接管时代：Google关闭Gemini CLI，真正改写的是开发者的权力边界》
- 《Google关掉Gemini CLI：AI编程的下一个时代，不是副驾驶，是接管方向盘》

## 推荐传播金句
> 工具是船，工作流是航海术。船会换，航海术才跟着你走。

## 质量自检项
写完后检查正文不得包含：
- `建议阅读`
- `点击右上角`
- `全文核心信息图`
- `配图：`
- `图片说明`
- `figcaption`
- `深入探讨`
- `赋能`
- `总而言之`
- `综上所述`
