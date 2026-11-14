# 多日 GitHub Trending 聚合方法

用于“最近两周 / 过去 N 天 Trending Top 50”这类 GitHub 官方页面无法直接提供的历史汇总任务。

## 统计口径

GitHub Trending 没有官方历史 API，也没有原生“两周榜”。必须先说明口径：

- 从可信的每日 Trending 历史快照读取指定日期范围；
- 合并全部日期并按 `owner/repo` 去重；
- 用**上榜天数**衡量持续热度，降序选取 Top N；
- 当前 Star、Fork、Language 等字段再通过 GitHub Repository API 补充；
- “上榜天数榜”不等于“Star 增长榜”，不能混写。

默认以当前日期往前取完整结束的 N 天。例如当前为 8 月 17 日，“近两周”可取 8 月 3 日至 8 月 16 日，共 14 个完整自然日。

## 推荐数据源顺序

1. GitHub 当前 `daily / weekly / monthly` 页面：适合当前窗口，不适合回溯两周。
2. `hanishrao/trending-collection`：按日期保存 Markdown 快照，适合跨日聚合。
3. `larsbijl/trending_archive` 或其他持续更新的公开归档：作为交叉验证或回退。
4. GitHub Search API：只能做近似补充，不能冒充 Trending 历史数据。

使用第三方归档前检查：目标日期是否连续、是否覆盖 all-languages、快照包含哪些语言。若归档按语言分组，应明确汇总的是“归档覆盖语言的 Trending”，不要声称绝对全站 Top 50。

## 聚合步骤

1. 用系统日期确定起止日，优先使用完整自然日。
2. 拉取或读取每天的快照。
3. 解析 `repo`、`url`、`description`、当天语言分区。
4. 以标准化后的 `owner/repo` 去重，累计 `appearance_days`、`appearance_dates`、出现过的语言分区、最新非空描述。
5. 排序优先级：上榜天数降序；若有每日排名，用平均排名升序；若仍并列，可按最近一次上榜日期或窗口 Star 增长排序。不要用仓库名字母序制造虚假的精确名次。
6. 对候选 Top N 调 GitHub Repository API 补充当前 Star、Fork、主语言、创建时间、Topics。
7. API 限流或仓库不可访问时，将字段标为“暂缺”，不要把缺失值写成 0。
8. 输出时先讲统计口径，再给榜单和趋势判断。

## 分析框架

不要把 50 个项目逐个扩写成新闻摘要。先聚类，再找因果链：

1. 哪一类项目占比最高？
2. 它们共同在补哪一层基础设施？
3. 为什么这一层现在集中爆发？
4. 下一层稀缺能力是什么？
5. 对目标用户的业务、内容或商业机会意味着什么？

推荐聚类：Agent/LLM/RAG/Context；Skill/Memory/Harness/Orchestration；Computer Use/Browser/CLI/Execution；Local/Edge AI；Developer Infrastructure；Security/Observability；阶段性语言或平台生态热点。

关键词只做初筛，最终必须语义复核。同一项目可能跨类别。

## 输出要求

- 标题明确日期范围和“按上榜天数”口径。
- 一句话结论必须有判断，不做“AI 项目很多”的弱总结。
- 完整榜单保持紧凑；深挖项目控制在 5—8 个。
- Star 是抓取时点的当前总量，不是两周新增量，必须注明。
- 趋势分析应串成递进关系，例如：
  `模型能力成熟 → Agent 开始执行长任务 → 状态与上下文成为瓶颈 → Skill/Memory/Harness 爆发 → 行业 Know-how 成为下一层壁垒`。

## 常见误区

1. 把当前 Weekly 和 Monthly 榜单简单拼接，当成两周历史榜。
2. 把“上榜天数”写成“增长排名”。
3. 归档只覆盖部分语言，却声称是 GitHub 全站绝对 Top 50。
4. 并列项目用仓库名字母序强行给出精确排名，却不解释并列规则。
5. 当前 Star 数与窗口内新增 Star 混淆。
6. API 限流后把 Star 缺失写成 0。
7. 50 个项目逐项长篇介绍，导致真正趋势被淹没。
