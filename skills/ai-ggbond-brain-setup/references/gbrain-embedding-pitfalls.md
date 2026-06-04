# GBrain Embedding 配置陷阱（实测记录 2026-06-02 ~ 06-04）

## 陷阱 1：`gbrain init --embedding-model` 维度冲突（2026-06-04 更新）

**现象**：`gbrain init --pglite --embedding-model dashscope:text-embedding-v4 --dimensions 1024` 报 `Refusing to init: Provider "dashscope" model "text-embedding-v4" rejects custom dimensions 1536`

**根因**：旧 brain 的 config.json 残留了 `embedding_dimensions: 1536`（来自 OpenAI），新模型只允许 64-1024。gbrain 读到旧配置后报维度冲突。

**修复**：
```bash
rm -f ~/.gbrain/config.json
rm -rf ~/.gbrain/brain.pglite
gbrain init --pglite --embedding-model dashscope:text-embedding-v4 --dimensions 1024
```

**v0.42.8.0 已修复**：`--embedding-model` 参数已生效（旧版本会被静默忽略）。但维度冲突仍需清除旧 brain。

---

## 陷阱 2：`gbrain config set embedding_model` 是 silent no-op

**现象**：`gbrain config set embedding_model dashscope:text-embedding-v4` 看似成功，但 embed 仍用旧模型。

**根因**：`gbrain config set` 写 DB plane，embed pipeline 读 file plane（config.json）。两者不互通。

**修复**：直接编辑 `~/.gbrain/config.json`，或用 `rm -f ~/.gbrain/config.json && gbrain init --pglite --embedding-model <model>` 重建。

---

## 陷阱 3：DashScope 中国区 key 必须 patch recipe

**现象**：`gbrain import` 报 `Incorrect API key provided`，但 curl 调 API 完全正常。

**根因**：GBrain 的 dashscope recipe 硬编码默认端点为国际版：
```typescript
// ~/.bun/install/global/node_modules/gbrain/src/core/ai/recipes/dashscope.ts
base_url_default: 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1',
```
中国区百炼 API key **只认** `dashscope.aliyuncs.com`，国际端点返回 `invalid_api_key`。

**为什么 config.json 的 base_urls 不管用**：

Gateway 代码读 `cfg.base_urls?.[recipe.id]`：
```typescript
// src/core/ai/gateway.ts
const baseURL = cfg.base_urls?.[recipe.id] ?? recipe.base_url_default;
```
但 config.json 的 `base_urls` 字段在 loadConfig() 到 gateway 的映射链中**断裂**——`gbrain config set` 写 DB plane，`config.json` 的 `base_urls` 也不被 gateway 正确读取。实测设置 `provider_base_urls.dashscope` 和 `base_urls.dashscope` 均无效。

**唯一解法**：直接改 recipe 源文件：
```bash
RECIPE_FILE="$HOME/.bun/install/global/node_modules/gbrain/src/core/ai/recipes/dashscope.ts"
sed -i '' 's|dashscope-intl.aliyuncs.com|dashscope.aliyuncs.com|g' "$RECIPE_FILE"
```

**⚠️ 风险**：`bun install -g github:garrytan/gbrain` 更新后会被覆盖，需重新 patch。

---

## 陷阱 4：DeepSeek 不支持 Embedding API

**现象**：`curl https://api.deepseek.com/v1/embeddings` 返回 HTTP 404。

**验证**（2026-06-02）：
```bash
curl -v https://api.deepseek.com/v1/embeddings \
  -H "Authorization: Bearer $DEEPSEEK_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "test", "model": "deepseek-embedding"}'
# HTTP/2 404, content-length: 0
```

**结论**：DeepSeek API Key 只能用于 GBrain 的 chat/expansion 模型，不能用于 embedding。

---

## 陷阱 5：维度不匹配导致 schema 损坏

**现象**：`gbrain doctor` 报 `embedding_column_registry: declared dims=1280 but actual is vector(1536)`。

**根因**：GBrain init 默认用 `zeroentropyai:zembed-1`（1280 维）创建 schema，但如果你后续改 config 指向 OpenAI（1536 维），schema 列类型不匹配。

**修复**：删除 brain 重建：
```bash
rm -rf ~/.gbrain/brain.pglite
# 编辑 config.json 设置正确的 embedding_model
gbrain init --pglite
```

---

## 陷阱 6：bun 符号链接缺失

**现象**：`gbrain --version` 报 `env: bun: No such file or directory`

**根因**：npm 安装的 `@oven/bun-darwin-aarch64` 不会自动创建 `~/.bun/bin/bun` 符号链接，但 gbrain 的 shebang 指向 `#!/usr/bin/env bun`。

**修复**：
```bash
ln -sf "$(npm root -g)/@oven/bun-darwin-aarch64/bin/bun" ~/.bun/bin/bun
```

---

## 陷阱 7：`gbrain config set base_urls.xxx` 是 unknown key

**现象**：`gbrain config set base_urls.dashscope "https://..."` 报 `Unknown config key`。

**根因**：GBrain 的 config 白名单里没有 `base_urls`，只有 `provider_base_urls`。但即使用 `provider_base_urls.dashscope`（被接受），gateway 代码也不会读它。

**结论**：base URL 覆盖只能通过改 recipe 源文件实现。

---

## 陷阱 8：⛔ gbrain fetch() 不读小写 http_proxy（2026-06-04 新增）

**现象**：`gbrain import` 报 `Cannot connect to API: Unable to connect`，但同环境 `curl` 调 API 完全正常。

**根因**：Bun/Node.js 的 `fetch()` 实现不自动读取小写 `http_proxy` / `https_proxy` 环境变量。只有大写 `HTTPS_PROXY` / `HTTP_PROXY` 被识别。

**验证**：
```bash
# 小写 — gbrain import 失败
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
gbrain import /tmp/test  # ❌ Cannot connect to API

# 大写 — gbrain import 成功
export HTTPS_PROXY=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
gbrain import /tmp/test  # ✅ imported=2, errors=0
```

**修复**：import/embed 操作前确保设大写代理：
```bash
export HTTPS_PROXY=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
```

写入 `~/.zshrc` 持久化：
```bash
echo 'export HTTPS_PROXY=http://127.0.0.1:7897' >> ~/.zshrc
echo 'export HTTP_PROXY=http://127.0.0.1:7897' >> ~/.zshrc
```

---

## 陷阱 9：brew malloc integer overflow（Homebrew 5.1.15）

**现象**：`brew install` 报 `malloc: possible integer overflow (18446744073709551615*4)`，所有 bottle 下载失败。

**根因**：Homebrew 5.1.15 的内置下载模块有整数溢出 bug。`brew fetch`（使用系统 curl）正常，但 `brew install` 的验证阶段报错。

**修复**：
```bash
# 方案 A：设系统 curl（fetch 有效，install 仍可能失败）
export HOMEBREW_CURL_PATH=/usr/bin/curl
brew fetch <formula>  # ✅ 下载成功

# 方案 B：手动解压 bottle（install 的替代方案）
# 1. 先 fetch
brew fetch <formula>
# 2. 找到缓存的 bottle
find ~/Library/Caches/Homebrew/downloads -name "<formula>*.bottle.tar.gz"
# 3. 手动解压到 /opt/homebrew/bin/
cd /tmp && mkdir extract && tar xzf <bottle.tar.gz> -C extract
cp extract/*/bin/<binary> /opt/homebrew/bin/
```

**已验证可装**：himalaya (v1.2.0), fzf (0.73.1), mmx-cli (npm), mcporter (npx)

**受影响**：remindctl, memo（依赖 python@3.13，brew 无法安装其依赖）

---

## 正确的完整安装流程（Hermes VM + DashScope）

```bash
# 1. 安装 bun
export HTTPS_PROXY=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.bun/bin:$PATH"

# 2. 安装 gbrain
bun install -g github:garrytan/gbrain

# 3. Patch DashScope recipe（中国区 key 必须）
RECIPE_FILE="$HOME/.bun/install/global/node_modules/gbrain/src/core/ai/recipes/dashscope.ts"
sed -i '' 's|dashscope-intl.aliyuncs.com|dashscope.aliyuncs.com|g' "$RECIPE_FILE"

# 4. 删除旧 brain（如有）+ 清 config
rm -rf ~/.gbrain/brain.pglite ~/.gbrain/config.json

# 5. 初始化（自动用 recipe 里的新 base URL）
export DASHSCOPE_API_KEY=sk-xxx
gbrain init --pglite --embedding-model dashscope:text-embedding-v4 --dimensions 1024

# 6. 设置 chat/expansion 模型
gbrain config set expansion_model dashscope:qwen-plus
gbrain config set chat_model dashscope:qwen-plus

# 7. 设置搜索模式（向用户展示成本矩阵后确认）
gbrain config set search.mode balanced

# 8. 导入 + embed（必须带大写代理）
gbrain import ~/brain/ --no-embed
gbrain embed --stale

# 9. 验证
gbrain doctor
gbrain stats
gbrain query "test query"
```
