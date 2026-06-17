# Tweet Categorization Keywords / 推文分类关键词

When generating the structured digest, scored tweets must be assigned to one of the 6 categories. Use keyword matching on tweet text (case-insensitive).

## Category → Keyword Mapping

```python
CATEGORIES = {
    '🔥重大事件': ['breaking', 'just in', 'announced', 'confirmed', 'major', '重大', '爆炸', '熔断', '暴跌', '危机', 'supersonic', 'first ever', '历史性'],
    '🚀产品发布': ['release', 'launch', 'v2', 'v3', 'v4', 'new model', 'api', 'update', '发布', '上线', '新版本', 'open source', 'introducing', 'now available', 'coding plan'],
    '💡技术洞察': ['how to', 'tutorial', 'tip', 'trick', 'architecture', 'performance', 'optimization', '技术', '方案', '优化', '实现', 'leverage', 'valuation', 'p/s', 'price/sales'],
    '🔗资源汇总': ['paper', 'research', 'study', 'github', 'repo', 'tool', 'resource', '论文', '开源', '资源', '工具', 'blog', 'guide'],
    '📊舆情信号': ['prediction', 'warning', 'controversy', 'debate', 'bullish', 'bearish', '预测', '警告', '争议', '观点', 'underestimate', 'miss', 'sigh'],
    '🎯个人视角': []  # Generated separately from Memory, not keyword-matched
}
```

## Fallback Logic

1. Count keyword matches per category
2. Assign to category with highest match count
3. If no matches → default to `💡技术洞察` (broadest bucket)
4. `🎯个人视角` is NEVER keyword-assigned — it's generated from Memory user state

## Notes

- A tweet can match multiple categories; pick the one with most keyword hits
- RT content is categorized by the RT text, not original tweet
- Short promotional tweets (<50 chars) often land in wrong category — apply human review for top items
- Chinese keywords help catch Chinese-language tweets that English-only matching would miss
