# 传播指数（Spread Index）调研与实现

> 2026-11-16 调研。目标：在 X 站内热度之外，加一层「全网传播热度」判断，低于基准的选题不写。

## 1｜全网有哪些可用的传播指数

### 第一梯队：预测型（最先进，付费）

**NewsWhip Prediction / Spike**
- 核心指标：`predicted_interactions`（预测未来 24 小时 Facebook + Twitter 互动量）、`nw_score`（当前传播速度）、`nw_max_score`（历史最高速度）。
- 特点：文章发布后几分钟内给出预测，按 30 分钟 / 1 小时 / 3 小时窗口排序；覆盖全球 web 文章和 Facebook 公开帖。
- 适合：判断「这条现在写，24 小时后会不会爆」。
- 限制：企业级付费 API，需要账号和额度。
- 参考：https://www.newswhip.com/prediction ｜ https://developer.newswhip.com/docs/data-dictionary

**BuzzSumo Trending Score**
- 核心指标：`trending_score`，基于社交分享随时间的变化速度；0 为最低，无固定上限。
- 特点：覆盖 Facebook、X、Reddit、YouTube、TikTok 等；有 8 亿+ 文章库。
- 适合：跨平台内容传播速度对比。
- 限制：付费订阅（约 $199/月起），API 另计。
- 参考：https://help.buzzsumo.com/en/articles/1633344-trending-now-what-is-the-trending-score

### 第二梯队：公开数据（免费，可落地）

**GDELT DOC 2.0**
- 核心指标：`timelinevolraw`（全球新闻文章数量）、`timelinelang`（语言分布）、`timelinetone`（平均语调）。
- 特点：全球新闻媒体覆盖，免费，无需 key；适合判断「主流媒体有没有跟进、跟进速度多快」。
- 限制：公共 API 限流严格（约 5 秒一次，超限直接返回提示文本），不适合批量并发；中文查询支持有限。
- 参考：https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

**Wikipedia Pageviews**
- 核心指标：某条目每日浏览量、近 2 日相对前 5 日的放大倍数。
- 特点：免费、稳定、可解释；适合判断「公众是否真的在查这件事」。
- 限制：只覆盖有维基条目的主体；对娱乐八卦、短视频热点不敏感。
- 参考：https://wikimedia.org/api/rest_v1/

**抖音热榜 / 百度热搜**
- 核心指标：热榜词条、排名、热度值。
- 特点：中文大众平台的第一手热度；免费（非官方接口，字段可能变化）。
- 限制：以社会、娱乐、政策为主；AI/科技题很少上榜，命中即代表破圈。
- 参考：`https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/` ｜ `https://top.baidu.com/board?tab=realtime`

**Hacker News Algolia**
- 核心指标：近 7 天相关 story 数量。
- 特点：免费、稳定；适合判断技术圈讨论度。
- 限制：只覆盖英文技术社区，中文/消费题会得 0 分。

### 第三梯队：中文舆情厂商（强，但闭源/付费）

**微热点（新浪）**
- 网络传播热度指数、事件热度/传播量榜单、传播路径分析；中文全网数据强。
- 参考：https://www.midu.com/more/bang

**清博智能**
- 微信 WCI、微博 BCI、抖音/小红书/快手等账号传播指数；公式公开，数据接口付费。
- 参考：https://www.gsdata.cn/site/usage-2

**知微数据**
- 知微事见：全网热点事件传播分析、舆论场变化、传播路径；企业级服务。
- 参考：https://www.weiboreach.com

**结论**：不存在一个免费指数覆盖所有平台。最先进的是 NewsWhip 的预测型指标；可落地的是「X + 中文热榜 + Wikipedia + HN」的复合指数，付费后再接 NewsWhip/BuzzSumo/微热点。

## 2｜本技能采用的复合指数（v1.1）

脚本：`scripts/spread_index.py`

### 平台权重

**微信公众号贴图（wechat）**
- X 热度 50%
- 中文热榜（抖音 + 百度，取最高）25%
- Wikipedia 关注度 15%
- Hacker News 讨论度 10%
- AIHOT 修正（可选，只有接入 AIHOT 时）：0 条 +3；≥5 条 -5

**X 贴图（x）**
- X 热度 65%
- 中文热榜 5%
- Wikipedia 关注度 15%
- Hacker News 讨论度 15%
- AIHOT 修正（可选，只有接入 AIHOT 时）：0 条 +3；≥5 条 -5

### 分项算法

**X 热度**
```
engagement = likes + 2*reposts + 0.5*replies
velocity = engagement / hours_since_post
x_score = 0.7 * log_norm(engagement, 20000) + 0.3 * log_norm(velocity, 1000)
```
`log_norm(v, p95) = 100 * log10(1+v) / log10(1+p95)`，上限 100。

**中文热榜**
- 在抖音/百度热榜词条中做关键词匹配；命中后按排名给分：`60 + 40 * (1 - rank/len)`。
- 两个平台取最高分；未命中 = 不加分、不扣分，按缺失处理，权重自动归一化。
- 命中代表「破圈」，不是「有讨论」；AI 题通常不命中，这是正常的。

**Wikipedia**
```
last2_avg = 最近 2 天日均浏览量
prev5_avg = 前 5 天日均浏览量
spike = last2_avg / max(prev5_avg, 1)
wiki_score = 0.6 * log_norm(last2_avg, 200000) + 0.4 * ratio_norm(spike, 5)
```

**Hacker News**
- 近 7 天相关 story 数量，`log_norm(hits, 100)`。
- 中文题可传 `hn_query` 指定英文查询词；没有英文查询词时不要硬算 0，脚本会跳过该分项并重新归一化权重。

### 基准与分层

默认基准：**80/100**（`--baseline` 可改）。**只有 S（≥80）进入发布池；A/B 只作备选，不写。**

- **S ≥ 80**：发布池，优先排期
- **A 65–79**：备选，不主推
- **B 55–64**：观察
- **C < 55**：不做

### 评分锚点（v1.1 校准）

- X 互动 **2 万**、速度 **1000/小时**接近满分；Wikipedia 单日 **20 万**浏览为绝对热度满分；HN 近 7 天 **100 条**为满分。
- 80 分是「真正的大爆款」线，不是日常好题线。2026-11-16 样本：黄仁勋夜市 83.7（微信）/ 90.5（X）、星舰 88.6 / 90.3、黄仁勋回归 86.0 / 87.1；Grok Bot 70.5 / 71.1、Claude 墓园 54.6 / 47.3。
- 中文热榜未命中按缺失处理，不按 0 分处理；旧事重提/常青故事不会因为当前没上热榜被误杀。

**传播指数过线 ≠ 可以发。** 还要过「得体性」检查：涉及未核实指控、私生活、地域/群体歧视、教人割韭菜的题，即使指数高也不做。

## 3｜使用方式

```bash
python3 scripts/spread_index.py \
  --input candidates.json \
  --platform wechat \
  --baseline 80 \
  --output scored.json
```

`candidates.json` 示例：

```json
[
  {
    "title": "黄仁勋夜市找水果阿姨",
    "keywords": ["黄仁勋", "夜市", "水果"],
    "x_engagement": 8665,
    "x_hours": 16,
    "wikipedia_title": "Jensen_Huang",
    "wikipedia_lang": "en",
    "hn_query": "Jensen Huang",
    "aihot_hits": 0
  }
]
```

输出包含：
- `spread_index`：0–100
- `tier`：S/A/B/C
- `components`：x / cn / wiki / hn 分项
- `details`：engagement、velocity、热榜命中词、Wikipedia 数据、HN 命中数
- `pass`：是否达到基准

## 4｜已知限制

- 中文热榜接口是非官方的，字段和可用性可能变化；失败时脚本会跳过该分项，不阻塞。
- GDELT 公共 API 限流严重，v1.1 默认不调用；需要时单独加 `--gdelt`（后续版本）。
- NewsWhip / BuzzSumo / 微热点 / 清博 / 知微 都是付费或闭源，v1.1 不直接接入；有 key 时可作为高权重分项替换。
- 指数衡量「当前传播热度」，不衡量内容质量、事实准确性、得体性。
- 旧事重提（如 2025 年的黄仁勋夜市）可能没有当前热榜命中，但 X 互动仍然很高；这类题需要人工判断是否属于「常青故事」。
