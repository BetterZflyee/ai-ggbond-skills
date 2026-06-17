---
name: ai-ggbond-brain-setup
description: GBrain 记忆层在 Hermes 环境下的安装、配置与内容灌入。当用户提到"brain""gbrain""灌内容""记忆层""知识库搭建"时触发。桥接 gbrain 上游技能（RESOLVER/signal-detector/brain-ops）与飞哥的 Hermes agent 生态。
version: 1.2.0
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
curl -fsSL https://bun.sh/install | bash   # 需代理
export PATH="$HOME/.bun/bin:$PATH"
bun --version
```

### 2. 安装 GBrain

```bash
export HTTPS_PROXY=http://127.0.0.1:7897   # 必须大写
export HTTP_PROXY=http://127.0.0.1:7897
bun install -g github:garrytan/gbrain
gbrain --version
```

### 3. Patch DashScope Recipe（中国区 key 必须）

```bash
RECIPE=~/.bun/install/global/node_modules/gbrain/src/core/ai/recipes/dashscope.ts
sed -i '' 's|dashscope-intl.aliyuncs.com|dashscope.aliyuncs.com|g' "$RECIPE"
grep "base_url_default" "$RECIPE"   # 验证已改
```

> ⚠️ `bun install -g` 更新 gbrain 后会被覆盖，需重新 patch。

### 4. 初始化（带 embedding）

```bash
export DASHSCOPE_API_KEY=sk-xxx
export HTTPS_PROXY=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897

# ⚠️ 旧 config.json 可能有冲突维度，先清除
rm -f ~/.gbrain/config.json
rm -rf ~/.gbrain/brain.pglite

gbrain init --pglite --embedding-model dashscope:text-embedding-v4 --dimensions 1024
```

> v0.42.8.0 的 `--embedding-model` **已生效**（旧版本会被静默忽略）。但如果有旧 config.json 残留，维度冲突会报错。清除后重新 init 即可。

### 5. 设置搜索模式

```bash
gbrain config set search.mode balanced   # 推荐
```

### 6. 加载上游技能

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

### 向量嵌入（四选一，DeepSeek 不支持）

| 提供商 | 申请地址 | 环境变量 | 备注 |
|--------|----------|----------|------|
| OpenAI | https://platform.openai.com/api-keys | `OPENAI_API_KEY` | 最通用 |
| ZeroEntropy | https://dashboard.zeroentropy.dev | `ZEROENTROPY_API_KEY` | gbrain 默认 |
| Voyage | https://dash.voyageai.com | `VOYAGE_API_KEY` | |
| **DashScope** | **https://bailian.console.aliyun.com/** | **`DASHSCOPE_API_KEY`** | **中文最优，最便宜** |
| ~~DeepSeek~~ | ❌ 不支持 embedding API | - | 只能用于 chat/expansion |

**推荐**：OpenAI text-embedding-3-small — 最通用，$10 能用很久。

> ⚠️ `gbrain config set embedding_model` 对已有 brain 是 silent no-op。必须编辑 `~/.gbrain/config.json`，见上方"正确配置 embedding 的方法"。

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

## Related Workflows

- **[GitHub 仓库同步](references/github-repo-sync.md)** — 将本地全部 ai-ggbond-* 技能同步到 GitHub 仓库 `BetterZflyee/ai-ggbond-skills`。含完整复制脚本和技能分布一览表。
- **[GBrain Embedding 陷阱](references/gbrain-embedding-pitfalls.md)** — 实测发现的 9 个配置陷阱：维度冲突、config set no-op、DashScope 中国区 recipe patch、DeepSeek 不支持 embedding、schema 损坏、bun 符号链接、base_urls 不生效、fetch() 代理大小写、brew malloc bug。

## Embedding 提供商配置（关键流程）

GBrain 原生支持 OpenAI / ZeroEntropy / Voyage / **DashScope（阿里云百炼）** 四家 embedding。**DeepSeek 不支持 embedding API**（2026-06 实测，`/v1/embeddings` 返回 404）。

> DashScope recipe 在 gbrain v0.42+ 内置（`src/core/ai/recipes/dashscope.ts`），Qwen3-Embedding 系列对应 API 模型名 `text-embedding-v4`。

### 正确配置 embedding 的方法

**v0.42.8.0 已修复**：`gbrain init --embedding-model` 和 `gbrain config set embedding_model` 均已生效。

但如果有旧 brain 存在，维度冲突会报错。清除后重新 init：

```bash
rm -f ~/.gbrain/config.json
rm -rf ~/.gbrain/brain.pglite
gbrain init --pglite --embedding-model dashscope:text-embedding-v4 --dimensions 1024
```

### 提供商选择

| 提供商 | 模型 | 维度 | 成本 | 备注 |
|--------|------|------|------|------|
| OpenAI | text-embedding-3-small | 1536 | ~$10/年 | 最通用 |
| ZeroEntropy | zembed-1 | 1280 | 有免费额度 | gbrain 默认 |
| Voyage | voyage-3-large | 1024 | 按量付费 | |
| **DashScope** | **text-embedding-v4** | 64~2048（默认1024） | **$0.07/百万token** | **Qwen3-Embedding，中文最优，中国区key需patch recipe** |
| **DeepSeek** | ❌ 不支持 | - | - | `/v1/embeddings` 返回 404 |

**飞哥推荐**：DashScope `text-embedding-v4` — 中文场景最优，价格极低，维度可选。需 `DASHSCOPE_API_KEY`（[百炼控制台](https://bailian.console.aliyun.com/)）。

### DashScope（Qwen3-Embedding）配置

```bash
export DASHSCOPE_API_KEY=sk-xxx   # 百炼控制台获取
```

config.json 配置：
```json
{
  "embedding_disabled": false,
  "embedding_model": "dashscope:text-embedding-v4",
  "embedding_dimensions": 1024
}
```

**关键参数**：
- API base URL：`https://dashscope.aliyuncs.com/compatible-mode/v1`（国内）/ `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`（海外）
- 维度选项：64 / 128 / 256 / 512 / 768 / 1024（默认）/ 1536 / 2048
- 最大 batch 行数：10
- 单行最大 token：8192
- 价格：$0.07/百万 token（比 OpenAI 便宜 3x+）
- 100+ 语种支持，中文效果优于 OpenAI/Voyage

---

## 代理配置（Hermes VM 必须）

gbrain 的 `fetch()` **不读小写 `http_proxy`**，必须设大写环境变量：

```bash
export HTTPS_PROXY=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
```

写入 `~/.zshrc` 持久化：
```bash
echo 'export HTTPS_PROXY=http://127.0.0.1:7897' >> ~/.zshrc
echo 'export HTTP_PROXY=http://127.0.0.1:7897' >> ~/.zshrc
```

导入和 embed 操作都需要代理（DashScope API 在墙内）。如果 `gbrain import` 报 `Cannot connect to API`，先检查代理是否用大写。

---

## Pitfalls（详见 [references/gbrain-embedding-pitfalls.md](references/gbrain-embedding-pitfalls.md)，共 9 个陷阱）

- **`gbrain skillpack scaffold --all` 需要在 gbrain 仓库根目录运行**，否则报 `could not find gbrain repo root`。全局安装后根目录在 `~/.bun/install/global/node_modules/gbrain/`。
- **纯中文搜索不可靠**：无嵌入时，"AI工具 下半场" 可能无结果，但 "Harness" 能命中。要么用 slug 直接读取，要么配 API Key 做向量搜索。
- **`gbrain import` 不会自动 git commit**：brain 目录自带 git，导入后记得 `git add -A && git commit`。
- **Big brain (>10K pages)**：PGLite 适合个人使用。超过阈值用 `gbrain migrate --to supabase` 迁移到 Postgres。
- **⛔ DashScope 中国区 key 必须 patch recipe**：gbrain 的 dashscope recipe 默认用国际端点 `dashscope-intl.aliyuncs.com`，中国区 API key 只认 `dashscope.aliyuncs.com`。`config.json` 的 `base_urls` / `provider_base_urls` 对 embed pipeline 无效（gateway 代码读 `cfg.base_urls` 但 config 系统映射不通）。唯一解法：直接改 recipe 源文件 `~/.bun/install/global/node_modules/gbrain/src/core/ai/recipes/dashscope.ts`，把 `dashscope-intl` 改成 `dashscope`。⚠️ `bun install -g` 更新后会被覆盖，需重新 patch。详见 [references/gbrain-embedding-pitfalls.md](references/gbrain-embedding-pitfalls.md)。
- **⛔ gbrain fetch() 不读小写 http_proxy**：Bun 的 `fetch()` 只认大写 `HTTPS_PROXY` / `HTTP_PROXY`。小写 `http_proxy` / `https_proxy` 不生效，导致 `gbrain import` 报 `Cannot connect to API`。必须 export 大写代理变量。
- **⛔ 维度冲突需清除旧 brain**：如果有旧 brain 的 embedding_dimensions 与新模型不匹配（如旧 OpenAI 1536d vs 新 DashScope 1024d），`gbrain init` 会报 `rejects custom dimensions`。必须先 `rm -f ~/.gbrain/config.json && rm -rf ~/.gbrain/brain.pglite` 再重新 init。
- **⛔ DeepSeek 不支持 embedding API**：`/v1/embeddings` 返回 404。DeepSeek Key 只能用于 chat/expansion，不能用于向量嵌入。
- **npm 在 Hermes VM 需代理**：GitHub 直连被墙，npm registry 有时也超时。确保 `HTTPS_PROXY=http://127.0.0.1:7897`（Clash）已设置后再跑 `npm install -g`。
- **环境变量持久化**：`DASHSCOPE_API_KEY`、`HTTPS_PROXY`、`HTTP_PROXY` 必须写入 `~/.zshrc`（或对应 shell 配置），否则新 session 中 gbrain 无法读取。
