# 《AI工具的下半场》文章配图与引流实战记录

## 场景
用户要求为公众号文章《AI工具的下半场：不是谁更会聊天，而是谁能真正下场干活》补充个人工作流引流，并生成尽可能多的配图。

## 文章引流方式
自然插入在“Skill 生态的扩散，说明 AI 能力正在被资产化”章节，而不是结尾硬广。

引流逻辑：
- `ai-ggbond-x-followings-feed`：抓 X/Twitter 关注流，生成 AI 日报，作为选题来源。
- `ai-ggbond-article-writer`：把选题、资料搜索、结构设计、初稿、去 AI 味、配图规划沉淀成公众号工作流。
- `ai-ggbond-post-to-wechat`：将 Markdown/HTML 推送到微信公众号草稿箱。
- `ai-ggbond-push-to-x`：把长文观点拆成 X/Twitter 传播内容。

推荐表达：
> 这不是宏大的平台，更像我给自己打造的几把“工作扳手”。
> 从“使用 AI 工具”，走向“拥有 AI 资产”。

仓库地址：`https://github.com/BetterZflyee/ai-ggbond-skills`

## 配图偏好修正
飞哥明确纠正：他没有拒绝手绘图。公众号文章配图一般按内容在手绘图、信息图、科技结构图之间选择。

执行规则：
- 概念/方法论/个人工作流：手绘信息图、手账式结构图。
- 技术架构/流程/企业方案：科技蓝结构图、专业流程图。
- 长文可采用“手绘信息图 + 科技蓝结构图”混合。
- 不要默认写“拒绝手绘莫兰迪”或“只用科技蓝扁平矢量”。

## 批量配图方案
本次规划 12 张 16:9 图：
1. 全文核心信息图
2. 聊天框到工作流迁移图
3. Claude 沙箱与 MCP 隧道图
4. Open Design + Codex 交付链路图
5. 企业 AI 成本分层图
6. Prompt vs Skill 对比图
7. AI朱朱侠工作流飞轮图
8. 企业 AI 小闭环图
9. 普通人工作流四步法图
10. X 新闻到公众号选题闭环图
11. 未来 AI 工具三层结构图
12. 结尾金句海报

## 工具故障与回退
内置 `image_generate` 工具失败：`FAL_KEY environment variable not set`。

正确回退：
1. 使用文章技能自带 `scripts/generate_images_v4.py`。
2. 确认 `~/.ai-ggbond-skills/.env` 或技能目录 `.env` 存在 `YUNWU_API_KEY`。
3. 写临时批量脚本导入：
   ```python
   from generate_images_v4 import YunwuImageGenerator, add_watermark
   g = YunwuImageGenerator()
   res = g.generate(prompt, model='gpt-image-2', size='1792x1024', quality='standard', max_retries=1, timeout=300)
   g.download_image(res.url, path)
   add_watermark(path, 'AI朱朱侠')
   ```
4. 每张图之间 `time.sleep(20)`，降低限流风险。
5. 后台执行并记录 `session_id`，完成后检查 `images/*.png`、文件大小、正文引用。

## 注意
生图时不要擅自换模型。若 `gpt-image-2` 或 API 报额度/权限/模型不可用，应暂停并告知用户，而不是切换到其他模型。