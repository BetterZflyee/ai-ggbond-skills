---
name: ai-ggbond-skill-matrix
description: 飞哥的全量Skill元路由表。181个Skill按7大场景分类，含触发词→Skill映射、常用链式工作流、选题→研究→写作→发布全链路编排。当用户说"我该用哪个skill""帮我选skill""全链路""从选题到发布""skill矩阵""skill总览"时触发。每次新任务进来，先扫此表再决定调用哪些Skill。
---

# AI GGBond Skill Matrix — 元路由表

> **181 Skills × 7 大场景 × 22 分类**
> 原则：先匹配场景，再匹配触发词，最后选Skill链。

---

## 一、内容全链路（选题→研究→写作→配图→发布→分发）

这是飞哥最核心的工作流，覆盖公众号/X/小红书三大平台。

### 1.1 选题发现

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `ai-ggbond-github-trending` | GitHub趋势、开源项目、选题灵感、AI项目发现 | AI Native视角的趋势解读+选题建议 |
| `aihot` | AI资讯、AI日报、行业动态、热点 | AI行业聚合资讯 |
| `follow-builders` | AI大佬动态、builder更新、行业insight | X/YouTube大佬内容摘要 |
| `ai-ggbond-x-followings-feed` | X日报、关注列表摘要、推文总结 | 关注列表结构化AI摘要 |
| `blogwatcher` | 博客监控、RSS订阅、feed追踪 | 博客/Feed更新监控 |

**选题链路**：
```
ai-ggbond-github-trending → aihot → ai-ggbond-x-followings-feed
→ 汇总3源信息 → 输出"本周5个选题"清单
```

### 1.2 深度研究

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `deep-research` | 深度研究、文献综述、系统性回顾、fact-check | 13-agent学术级研究报告 |
| `web-access` | 搜索、抓取网页、联网、爬取 | 三层联网通道（search→curl→CDP） |
| `tavily-search` | 搜索、找资料、查信息 | LLM优化的搜索结果 |
| `arxiv` | 论文搜索、arxiv、学术文献 | arXiv论文检索 |
| `llm-wiki` | 知识库、wiki、知识图谱 | Karpathy式互联知识库 |
| `cdp-browser-harness` | 浏览器自动化、登录后操作、网页交互 | 自愈式CDP浏览器（95站点预置） |

**研究链路**：
```
tavily-search（快速搜索）→ web-access（深度抓取）→ deep-research（学术级综合）
→ 输出：研究结论 + 数据支撑 + 可引用素材
```

### 1.3 内容写作

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `ai-ggbond-article-writer` | 写文章、分析产品、聊聊XXX、品牌故事 | 公众号成稿（递进论证链） |
| `humanizer` | 去AI味、人性化、自然表达 | 去除AI腔调 |
| `web-video-presentation` | 口播稿、视频演示、网页演示 | 16:9交互式网页演示 |
| `guizang-ppt` / `guizang-ppt-skill` | PPT、演示、分享、发布会 | 横向翻页网页PPT |
| `ai-ggbond-sticker-writer` | 贴图、小红书风格、微信贴图 | 500字内短句贴图 |

**写作铁律**（记忆）：
- 多案例文章用递进论证链（现象→框架→机制→资产→权力→行动→冷思考→升华）
- 禁止"平行案例陷阱"
- 行动建议在冷思考之前
- 金句收束而非总结

### 1.4 配图生成

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `image_generate` | 生成图片、配图、封面 | gpt-image-2生成 |
| `comfyui` | ComfyUI、工作流图片、视频生成 | 本地ComfyUI图片/视频/音频 |
| `stable-diffusion-image-generation` | SD图片、diffusion、图生图 | Stable Diffusion图片 |
| `baoyu-infographic` | 信息图、infographic、可视化 | 21布局×21风格信息图 |
| `baoyu-comic` | 知识漫画、教育漫画 | 知识漫画 |
| `excalidraw` | 手绘图、架构图、流程图 | 手绘风格JSON图 |
| `architecture-diagram` | 架构图、系统图、云架构 | 暗色主题SVG架构图 |
| `ascii-art` | ASCII艺术、字符画 | pyfiglet/cowsay/image-to-ascii |
| `pixel-art` | 像素风、复古游戏风格 | 时代调色板像素画 |
| `ai-ggbond-remove-ai-marks` | 去水印、清除AI标记、洗图 | 清除可见/不可见水印 |

**配图铁律**（记忆）：
- 长叙述prompt会偏离内容→用结构化网格布局
- 生成后PaddleOCR核对文字
- 学术风高密度信息图，非概念化PPT
- 图文必须严格对应

### 1.5 发布分发

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `ai-ggbond-post-to-wechat` | 发公众号、推送到草稿箱 | 公众号草稿（含封面+正文图片） |
| `ai-ggbond-publish-to-x` | 发X、发推、tweet | X短帖/长文/Thread |
| `ai-ggbond-run-xiaohongshu` | 小红书、发小红书、红书运营 | 小红书全链路（定位→选题→发布→复盘） |
| `xitter` / `xurl` | X API操作、推文管理 | X/Twitter CLI操作 |

**全链路模板**：
```
选题：ai-ggbond-github-trending + aihot
  ↓
研究：deep-research 或 tavily-search + web-access
  ↓
写作：ai-ggbond-article-writer（递进论证链）
  ↓
配图：image_generate（gpt-image-2，结构化网格prompt）
  ↓
去水印：ai-ggbond-remove-ai-marks
  ↓
发布：ai-ggbond-post-to-wechat（公众号）
     ai-ggbond-publish-to-x（X）
     ai-ggbond-run-xiaohongshu（小红书）
```

---

## 二、投资交易全链路（选股→分析→评审→交易→监控）

### 2.1 选股与量化

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `a-stock-tools` | A股量化、选股、因子分析、Qlib | 量化因子选股+券商API实盘 |
| `lhb-analyzer` | 龙虎榜、游资、机构博弈、辨识度龙头 | 龙虎榜深度分析 |
| `polymarket` / `polymarket-public-data` | Polymarket、预测市场、赔率 | 预测市场数据 |
| `market-intel` | 市场资讯、金融事件、市场情报 | AI-Trader金融事件快照 |

### 2.2 深度分析

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `deep-analysis` | 深度分析、全面分析、值不值得买、DCF | 22维数据+51位大佬评审+6种估值+7种研究产物 |
| `investor-panel` | 评审团、50大佬怎么看、某某会买吗 | 50位投资大佬量化投票 |
| `trap-detector` | 杀猪盘、朋友推荐、群里说、内幕消息 | 8信号风险评级🟢🟡🟠🔴 |

### 2.3 交易执行与监控

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `ai-trader` | 交易信号、跟单、trading signal | AI交易信号平台 |
| `ai-trader-copytrade` | 跟单、复制持仓、copy trade | 跟随顶级交易者 |
| `ai-trader-tradesync` | 同步持仓、交易记录同步 | 持仓同步到AI-Trader |
| `ai-trader-heartbeat` | 心跳检测、交易通知 | AI-Trader心跳轮询 |

**投资分析模板**：
```
用户："深度分析XXX"
→ deep-analysis（22维+估值建模）
→ investor-panel（50大佬评审）
→ trap-detector（杀猪盘扫描）
→ 输出：HTML报告 + 决策建议
```

---

## 三、知识管理与研究（笔记→记忆→文档→学术）

### 3.1 知识捕获

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `obsidian` | 笔记、Obsidian、知识库 | Obsidian笔记读写搜索 |
| `hindsight-local` | 记住、偏好、学习、经验 | 持久化用户偏好与经验 |
| `memory` | 记忆、记住这个、不要忘记 | Hermes跨会话记忆 |
| `meeting-minutes-to-memory` | 会议纪要、会议记录、提取要点 | 会议内容提取→记忆/研究 |

### 3.2 文档处理

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `paddleocr-doc-parsing` | PDF解析、版面还原、表格提取 | 结构化Markdown/JSON（表格+公式+图表） |
| `paddleocr-text-recognition` | OCR、文字识别、截图识字 | 精确文字提取 |
| `paddleocr-curl-ocr` | OCR失败、SSL错误、PaddleOCR备用 | curl方式OCR（绕过SSL问题） |
| `ocr-and-documents` | PDF提取、扫描件、DOCX | 多格式文档提取 |
| `nano-pdf` | 编辑PDF、修改PDF文字 | 自然语言PDF编辑 |

### 3.3 学术研究

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `academic-paper` | 写论文、学术论文、guide my paper | 12-agent论文写作（10种模式） |
| `academic-paper-reviewer` | 审论文、peer review、模拟审稿 | 5位审稿人模拟评审 |
| `academic-pipeline` | 完整论文流程、research-to-publication | 10阶段学术流水线 |
| `deep-research` | 深度研究、文献综述、系统性回顾 | 13-agent研究报告 |

---

## 四、生产力工具（飞书→Google→Notion→邮件→日程）

### 4.1 飞书/Lark

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `lark-unified` | 飞书、Lark、消息、文档、表格 | 200+命令覆盖11个业务域 |
| `lark-cli-setup` | 飞书CLI安装、配置、认证 | lark-cli安装配置 |
| `lark-cli-bitable-docs-automation` | 飞书多维表格、Bitable、自动化 | 多维表格创建与管理 |

### 4.2 Google Workspace

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `google-workspace` | Gmail、Google日历、Drive、Sheets | Google全套办公 |

### 4.3 其他生产力

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `notion` | Notion、页面、数据库 | Notion API操作 |
| `airtable` | Airtable、记录、筛选 | Airtable REST API |
| `himalaya` | 邮件、IMAP、SMTP、发邮件 | 终端邮件收发 |
| `powerpoint` | PPT、幻灯片、.pptx | PowerPoint创建编辑 |
| `tencent-meeting-mcp` | 腾讯会议、预约会议、会议录制 | 腾讯会议全功能 |
| `maps` | 地图、导航、POI、路线 | OpenStreetMap地理服务 |
| `find-nearby` | 附近餐厅、找地方、周边 | OpenStreetMap周边搜索 |

---

## 五、开发与运维（编码→测试→部署→调试）

### 5.1 AI代理编码

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `claude-code` | Claude Code、委派编码、写功能 | Claude Code CLI代理 |
| `codex` | Codex、OpenAI编码 | Codex CLI代理 |
| `opencode` | OpenCode、编码审查 | OpenCode CLI |
| `hermes-agent` | Hermes配置、agent设置、工具管理 | Hermes Agent配置扩展 |

### 5.2 GitHub操作

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `github-repo-management` | 克隆仓库、创建repo、管理remote | GitHub仓库管理 |
| `github-pr-workflow` | PR、分支、合并、CI | PR全生命周期 |
| `github-code-review` | 代码审查、review、diff | PR审查+行内评论 |
| `github-issues` | Issue、标签、分配 | Issue管理 |
| `github-auth` | GitHub认证、token、SSH | GitHub认证设置 |
| `codebase-inspection` | 代码量、语言占比、LOC | pygount代码库检查 |

### 5.3 软件开发

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `plan` | 规划、plan、方案设计 | Markdown实现方案 |
| `writing-plans` | 写计划、任务拆分、bite-sized | 详细实现计划 |
| `to-issues` | 拆issue、转tickets、任务分解 | 方案→独立issue |
| `to-prd` | 写PRD、产品需求文档 | 对话→PRD |
| `tdd` | 测试驱动、TDD、red-green-refactor | TDD开发循环 |
| `test-driven-development` | 测试优先、写测试 | TDD强制执行 |
| `prototype` | 原型、prototype、试试设计 | 快速原型验证 |
| `spike` | 实验、spike、验证想法 | 抛弃式实验 |
| `requesting-code-review` | 提交前审查、质量门禁 | 代码审查+安全扫描 |

### 5.4 调试与运维

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `diagnose` | 诊断、debug、排查、性能回归 | 系统化诊断循环 |
| `systematic-debugging` | 调试、根因分析、4阶段调试 | 理解→最小化→假设→修复 |
| `debugging-hermes-tui-commands` | Hermes TUI调试、slash命令 | Hermes TUI调试 |
| `node-inspect-debugger` | Node调试、Chrome DevTools | Node.js调试 |
| `python-debugpy` | Python调试、pdb、debugpy | Python远程调试 |
| `skill-health-audit` | Skill健康检查、审计skill | Skill库健康扫描 |
| `safe-tavily-cli-setup` | Tavily安装、搜索配置 | Tavily CLI安全安装 |

### 5.5 知识库理解

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `understand` | 分析代码库、理解架构 | 交互式知识图谱 |
| `understand-explain` | 解释代码、这个函数做什么 | 深度代码解释 |
| `understand-diff` | 分析diff、PR变更、影响范围 | Git diff分析 |
| `understand-domain` | 领域知识、业务逻辑 | 领域流程图 |
| `understand-onboard` | 新人指南、onboarding | 入职指南生成 |
| `understand-dashboard` | 知识图谱可视化、dashboard | 交互式Web看板 |
| `improve-codebase-architecture` | 重构、架构改进、解耦 | 代码库深化机会 |

---

## 六、媒体与创意（音频→视频→动画→设计→游戏）

### 6.1 音频

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `heartmula` | 歌曲生成、Suno、歌词+标签 | Suno风格歌曲 |
| `songwriting-and-ai-music` | 作曲、写歌、音乐制作 | 歌曲创作+Suno提示词 |
| `audiocraft-audio-generation` | MusicGen、文字转音乐、音效 | AI音乐/音效生成 |
| `whisper` | 语音转文字、转录、ASR | 99语言语音识别 |
| `songsee` | 音频频谱、mel、MFCC | 音频特征分析 |
| `spotify` | Spotify、播放、歌单 | Spotify控制 |

### 6.2 视频与动画

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `web-video-presentation` | 网页演示、口播视频、交互演示 | 16:9交互网页演示 |
| `manim-video` | 3Blue1Brown、数学动画、算法可视化 | Manim数学动画 |
| `ascii-video` | ASCII视频、字符动画 | ASCII彩色视频/GIF |
| `youtube-content` | YouTube摘要、视频转文字 | YouTube转录→摘要/博客 |
| `x-media-download` | 下载X视频、推文媒体 | X/Twitter媒体下载 |

### 6.3 设计与可视化

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `claude-design` | Landing page、deck、prototype | 一次性HTML设计 |
| `popular-web-designs` | 54种设计系统、Stripe风格、Linear风格 | 真实设计系统HTML/CSS |
| `sketch` | 草图、2-3种设计对比 | 快速HTML草图 |
| `design-md` | DESIGN.md、token规范 | Google DESIGN.md规范 |
| `p5js` | p5.js、生成艺术、shader、交互 | p5.js创意编程 |
| `touchdesigner-mcp` | TouchDesigner、实时视觉 | TouchDesigner MCP控制 |
| `pretext` | 文字排版、ASCII布局、文字几何 | DOM-free文字布局 |

### 6.4 代码可视化

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `excalidraw` | 手绘图、白板图 | Excalidraw JSON图 |
| `architecture-diagram` | 架构图、系统架构、云架构 | 暗色SVG架构图 |
| `ascii-art` | ASCII艺术、字符画 | pyfiglet/cowsay |

---

## 七、业务运营（工业照明→求职→平台管理）

### 7.1 工业照明业务

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `industrial-lighting-bid` | 招标信息、工业照明、投标筛选 | chinabidding.cn爬取+筛选+Excel |
| `industrial-lighting-bid-demo` | 演示招投标、快速展示 | 20关键词快速演示版 |

### 7.2 求职系统

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `offer-sprint-interview-job-search` | 求职、面试、Offer冲刺、简历 | 求职执行+面试模拟+简历定位 |
| `expression-training-for-interviews` | 面试表达、言简意赅、表达训练 | 三阶段表达训练 |
| `高压场景心态调节方案` | 高压、面试紧张、心态调节 | 即时调节+泄压替代+行为拦截 |

### 7.3 平台与工具管理

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `ai-ggbond-brain-setup` | GBrain、记忆层、知识库搭建 | GBrain安装配置+内容灌入 |
| `find-skills` | 找skill、搜索技能、发现新skill | OpenClaw技能搜索 |
| `clawhub-skills-install-to-hermes` | 安装skill、导入技能 | 外部skill安装+安全审查 |
| `write-a-skill` | 写skill、创建技能 | 新skill编写 |
| `skill-orchestrator` | 多技能编排、复杂任务、链式调用 | Skill编排执行 |
| `hindsight-local` | 记住偏好、经验存储 | 持久化用户经验 |
| `webhook-subscriptions` | Webhook、事件驱动、自动触发 | Webhook订阅管理 |

### 7.4 通用工具

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `web-access` | 联网、搜索、抓取 | 三层联网通道 |
| `tavily-search` | 搜索、找资料 | LLM优化搜索 |
| `caveman` | 精简模式、省token、简短 | 压缩75%token |
| `grill-me` | 追问、压力测试、挑战方案 | 苏格拉底式追问 |
| `grill-with-docs` | 对照文档挑战、验证方案 | 文档对齐追问 |
| `zoom-out` | 全局视角、跳出细节、大局观 | 更高层面视角 |
| `handoff` | 交接、切换agent、上下文传递 | 对话压缩为交接文档 |
| `triage` | 分类issue、bug分类、工作流 | 状态机驱动的issue分流 |
| `diagnose` | 诊断、排查、debug | 系统化诊断 |
| `ideation` | 头脑风暴、创意生成、项目点子 | 约束驱动创意 |
| `yuanbao` | 元宝群、@用户、群信息 | 元宝群操作 |

---

## 八、ML/AI 工程（训练→推理→评估→部署）

> 这些Skill偏底层ML工程，飞哥日常较少直接用，但在需要技术深度时可调用。

### 8.1 模型训练

| Skill | 触发词 |
|-------|--------|
| `axolotl` | LoRA、DPO、GRPO、YAML微调 |
| `fine-tuning-with-trl` | SFT、DPO、PPO、GRPO、RLHF |
| `grpo-rl-training` | GRPO、强化学习微调 |
| `peft-fine-tuning` | LoRA、QLoRA、参数高效微调 |
| `unsloth` | 2-5x加速微调、少显存 |
| `pytorch-fsdp` | FSDP、分布式训练、参数分片 |
| `weights-and-biases` | 实验记录、W&B、sweeps |

### 8.2 模型推理

| Skill | 触发词 |
|-------|--------|
| `llama-cpp` | 本地推理、GGUF、CPU推理 |
| `gguf-quantization` | 量化、GGUF、消费级硬件部署 |
| `serving-llms-vllm` | vLLM、高吞吐推理、API服务 |
| `guidance` | 约束生成、正则控制、结构化输出 |
| `outlines` | JSON/regex/Pydantic结构化生成 |
| `obliteratus` | 去除LLM限制、ablation |

### 8.3 计算机视觉

| Skill | 触发词 |
|-------|--------|
| `clip` | 图文匹配、零样本分类 |
| `segment-anything-model` | SAM、图像分割 |
| `stable-diffusion-image-generation` | SD图片生成 |

### 8.4 评估与平台

| Skill | 触发词 |
|-------|--------|
| `evaluating-llms-harness` | MMLU、GSM8K、基准测试 |
| `dspy` | 声明式LM程序、自动优化prompt |
| `huggingface-hub` | HuggingFace模型/数据集 |
| `modal-serverless-gpu` | 无服务器GPU、按需计算 |

---

## 九、Apple 生态（仅 macOS）

| Skill | 触发词 | 产出 |
|-------|--------|------|
| `apple-notes` | Apple Notes、备忘录 | memo CLI管理笔记 |
| `apple-reminders` | 提醒事项、reminders | remindctl管理提醒 |
| `findmy` | 查找设备、AirTag | FindMy设备追踪 |
| `imessage` | iMessage、短信 | imsg收发消息 |

---

## 十、特殊模式

| 模式 | 触发词 | 说明 |
|------|--------|------|
| **精简模式** | "caveman"、"省token" | 压缩75%token，保持技术准确 |
| **追问模式** | "grill me"、"挑战我" | 苏格拉底式深度追问 |
| **全局模式** | "zoom out"、"大局观" | 跳出细节看全局 |
| **交接模式** | "handoff"、"交接" | 压缩对话为交接文档 |
| **编排模式** | "全链路"、"多技能" | skill-orchestrator链式调用 |

---

## 附录：飞哥常用全链路工作流

### A. 公众号日更流
```
1. 选题：ai-ggbond-github-trending + aihot + follow-builders
2. 研究：tavily-search → web-access → deep-research（按深度选）
3. 写作：ai-ggbond-article-writer（递进论证链）
4. 配图：image_generate（gpt-image-2，结构化网格）
5. 质检：paddleocr-text-recognition（OCR核对）
6. 去水印：ai-ggbond-remove-ai-marks
7. 发布：ai-ggbond-post-to-wechat
8. 分发：ai-ggbond-publish-to-x + ai-ggbond-run-xiaohongshu
```

### B. 股票深度分析流
```
1. 数据：a-stock-tools（量化因子）+ lhb-analyzer（龙虎榜）
2. 分析：deep-analysis（22维+估值建模）
3. 评审：investor-panel（50大佬投票）
4. 风控：trap-detector（杀猪盘扫描）
5. 输出：HTML报告 + 社交战报
```

### C. 求职执行流
```
1. 定位：offer-sprint-interview-job-search
2. 表达：expression-training-for-interviews
3. 心态：高压场景心态调节方案
4. 跟进：lark-cli-bitable-docs-automation（飞书表格管理）
```

### D. 技术项目开发流
```
1. 规划：plan → writing-plans
2. 拆分：to-issues → to-prd
3. 编码：claude-code / codex / opencode
4. 测试：tdd / test-driven-development
5. 审查：requesting-code-review → github-code-review
6. 部署：github-pr-workflow
7. 理解：understand → improve-codebase-architecture
```

### E. 学术论文流
```
1. 研究：deep-research
2. 写作：academic-paper
3. 审查：academic-paper-reviewer
4. 修订：academic-paper（revision模式）
5. 完整流水线：academic-pipeline（一键10阶段）
```
