---
name: ai-ggbond-brain-setup
description: GBrain 记忆层在 Hermes 环境下的安装、配置与内容灌入。当用户提到"brain""gbrain""灌内容""记忆层""知识库搭建"时触发。桥接 gbrain 上游技能（RESOLVER/signal-detector/brain-ops）与飞哥的 Hermes agent 生态。
version: 1.0.0
metadata:
  openclaw:
    homepage: https://github.com/BetterZflyee/ai-ggbond-skills#ai-ggbond-brain-setup
    requires:
      anyBins:
        - bun
        - npm
---

# AI朱朱侠 — GBrain 记忆层集成

将 GBrain（Garry Tan 的 opinionated agent brain）作为飞哥 Hermes 智能体的持久记忆层。

**设计原则**：GBrain 不是笔记软件，是实时上下文膜层。每次对话中 signal-detector 自动从对话提取人物/观点/概念写入 brain，brain-ops 保证脑优先查找（先搜脑，再调外部 API）。

---

## 快速安装（Hermes 终端 VM 专用）

Hermes 终端 VM 的 GitHub 直连被墙，但 npm registry 可用。绕行路径：

### 1. 安装 Bun

```bash
npm install -g @oven/bun-darwin-aarch64   # npm 拉取，不走 GitHub
BUN_BIN=$(npm root -g)/@oven/bun-darwin-aarch64/bin/bun
export PATH="$HOME/.bun/bin:$PATH"
"$BUN_BIN" --version   # 验证
```

### 2. 安装 GBrain

```bash
bun install -g github:garrytan/gbrain   # bun 内部网络路径可通
gbrain --version   # 验证
```

### 3. 初始化

```bash
gbrain init --pglite --no-embedding
```

`--no-embedding` 允许先建脑后配 Key。后续配 Key 后跑 `gbrain embed --stale` 补向量。

### 4. 加载上游技能

```bash
cd ~/.bun/install/global/node_modules/gbrain
gbrain skillpack scaffold --all
```

三个永远在线技能（必须读）：
- `skills/signal-detector/SKILL.md` — 每条消息触发，提取观点和实体
- `skills/brain-ops/SKILL.md` — 脑优先查找协议
- `skills/conventions/quality.md` — 引用格式、反向链接铁律

完整技能路由表：`skills/RESOLVER.md`

---

## API Key 配置

### 向量嵌入（三选一）

| 提供商 | 申请地址 | 配置命令 |
|--------|----------|----------|
| OpenAI | https://platform.openai.com/api-keys | `export OPENAI_API_KEY=sk-...` + `gbrain config set embedding_model openai:text-embedding-3-large` |
| ZeroEntropy | https://dashboard.zeroentropy.dev | `export ZEROENTROPY_API_KEY=ze-...`（默认） |
| Voyage | https://dash.voyageai.com | `export VOYAGE_API_KEY=...` + `gbrain config set embedding_model voyage:voyage-3-large` |

**推荐**：OpenAI — 最通用，$10 能用很久。

### 查询扩展（可选）

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

不配也能用，只是搜索时不会自动扩充查询角度。

---

## 搜索模式选择

`gbrain init` 自动设置模式。需向用户展示成本矩阵并确认：

```
                  Haiku 4.5     Sonnet 4.6    Opus 4.7
  conservative    $40/月        $120/月       $200/月
  balanced        $100/月       $300/月       $500/月
  tokenmax        $200/月       $600/月       $1,000/月
```

- **conservative**：4K / 10 chunks / 无扩展（无 Key 时唯一选项）
- **balanced**：12K / 25 chunks / 无扩展
- **tokenmax**：无限 / 50 chunks / LLM 扩展

---

## 脑目录结构

```
~/brain/
├── .gbrain.yml          → 脑注册文件
├── README.md
├── people/              → 人物（面试官、客户、联系人）
├── companies/           → 公司（目标公司、客户公司）
├── concepts/            → 概念（AI Native、熵减、超级个体...）
├── ideas/               → 想法（产品点子、商业想法）
├── originals/           → 原创观点（飞哥的判断、框架、文章）
├── meetings/            → 会议记录
├── deals/               → 商机/项目
├── career/              → 求职（面试复盘、案例库）
├── content/             → 内容资产
└── research/            → 行业研究
```

---

## 内容灌入模式

### 复制 → 重命名 → 导入

```bash
# 1. 把源文件复制到 brain 对应目录，用清理后的文件名
cp "源文章路径/长文件名-版本号.md" ~/brain/originals/clean-name.md

# 2. 导入（无嵌入模式，先灌后补向量）
gbrain import ~/brain/ --no-embed

# 3. 有 API Key 后补向量
gbrain embed --stale
```

### Slug 约定（重要）

gbrain 自动生成的 slug **包含目录前缀**：

| 文件路径 | gbrain slug |
|----------|------------|
| `~/brain/originals/harness-awakening.md` | `originals/harness-awakening` |
| `~/brain/people/wu-songyao.md` | `people/wu-songyao` |

搜索/读取时**必须带前缀**：
```bash
gbrain get originals/harness-awakening    # ✅
gbrain get harness-awakening              # ❌ page_not_found
```

---

## 搜索能力矩阵

| 搜索方式 | 需要什么 | 能搜什么 |
|----------|----------|----------|
| `gbrain search "keyword"` | 无 | 精确关键词匹配（英/中英混合好，纯中文差） |
| `gbrain query "自然语言问题"` | API Key + 向量嵌入 | 语义相似检索 |
| `gbrain get <slug>` | 无 | 精确路径读取 |

**纯中文关键词搜索受限**：FTS 分词器对中英文混合友好（"Harness 觉醒"能命中），但纯中文（"下半场"）可能漏。需要向量嵌入才能解决。

---

## 日常维护

```bash
gbrain autopilot --install --repo ~/brain   # 一次性安装自维护守护进程
gbrain dream                                 # 手动触发夜间 8 阶段维护
gbrain doctor --json                         # 健康检查
gbrain stats                                 # 统计
```

---

## Pitfalls

- **`gbrain skillpack scaffold --all` 需要在 gbrain 仓库根目录运行**，否则报 `could not find gbrain repo root`。全局安装后根目录在 `~/.bun/install/global/node_modules/gbrain/`。
- **纯中文搜索不可靠**：无嵌入时，"AI工具 下半场" 可能无结果，但 "Harness" 能命中。要么用 slug 直接读取，要么配 API Key 做向量搜索。
- **`gbrain import` 不会自动 git commit**：brain 目录自带 git，导入后记得 `git add -A && git commit`。
- **Big brain (>10K pages)**：PGLite 适合个人使用。超过阈值用 `gbrain migrate --to supabase` 迁移到 Postgres。
