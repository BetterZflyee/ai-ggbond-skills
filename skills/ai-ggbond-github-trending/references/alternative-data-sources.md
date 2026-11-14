# GitHub Trending 替代数据源

当 GitHub Trending 页面数据不足（页面上限约 25 个项目）或脚本失败时，使用以下替代来源。

## 1. Trendshift.io

**URL**: `https://trendshift.io/github-trending-repositories?since=weekly`

- 第三方 GitHub Trending 聚合站
- 有历史趋势数据（可查看某项目何时上过 Trending）
- 支持按语言/话题筛选
- 数据更稳定，反爬限制低

**抓取方式**:
```bash
web_extract(["https://trendshift.io/github-trending-repositories?since=weekly"])
```

**注意事项**: 页面内容可能被截断，需配合 browser 工具获取完整数据。

## 2. OSSInsight AI Trending

**URL**: `https://ossinsight.io/trending/ai`

- AI 专项排名，按 star 增长排序
- 包含 AI Agents、Coding Agents、LLM Tools 等分类
- 数据含 star 数和近期增长量
- 适合 AI/Agent/MCP 方向的专项筛选

**抓取方式**:
```bash
web_extract(["https://ossinsight.io/trending/ai"])
```

**特点**: 数据结构化程度高，适合对比分析。

## 3. GitHub Search API

**命令格式**:
```bash
gh search repos --created=">YYYY-MM-DD" --sort=stars --order=desc --limit=50 \
  --json fullName,stargazersCount,description,primaryLanguage,url
```

**示例**（获取本周新建高增长仓库）:
```bash
gh search repos --created=">2026-06-15" --sort=stars --order=desc --limit=50 \
  --json fullName,stargazersCount,description,primaryLanguage,url
```

**注意事项**:
- 非 Trending 等价数据，是按 star 数排序的新建仓库
- 需要 gh CLI 已认证
- 可能超时，建议设 30s timeout
- 返回的是新建仓库，不含老牌项目的突然增长

## 4. 数据源选择策略

| 场景 | 推荐数据源 |
|------|-----------|
| 快速查看今日/本周热榜 | GitHub Trending 脚本 |
| 需要更长榜单（>25项） | Trendshift.io |
| AI/Agent 专项分析 | OSSInsight AI Trending |
| 查找特定时间段新建高增长项目 | GitHub Search API |
| 项目历史趋势分析 | Trendshift.io（有历史数据） |

## 5. 已知限制

- **GitHub Trending 页面**: 最多约 25 个项目，无官方 API
- **Trendshift.io**: web_extract 可能截断，需 browser 辅助
- **OSSInsight**: 仅 AI 方向，非全品类
- **GitHub Search**: 新建仓库为主，不反映老牌项目增长
