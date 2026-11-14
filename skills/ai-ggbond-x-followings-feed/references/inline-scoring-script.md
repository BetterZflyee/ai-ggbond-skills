# Inline Scoring Script Reference

**⚠️ 优先用 `scripts/curate_and_score.py`（CLI 文本输出，快速便捷）。** 只有当需要 JSON 输出或自定义打分权重时，才用下面的 inline 脚本。

When `scripts/curate_and_score.py` CLI output format doesn't fit (outputs human-readable text, not JSON), use this inline script pattern. Write to `/tmp/score_tweets.py` via `write_file`, then execute with `terminal` (pitfall #15 two-step pattern).

## Proven Scoring Script (2026-06-19 verified)

```python
#!/usr/bin/env python3
"""Score and curate tweets from X followings feed."""
import json, re, sys

with open('/tmp/x_following_latest.json') as f:
    tweets = json.load(f)

SIGNAL_KEYWORDS = {
    # Product/version signals
    r'v\d+\.\d+': 5, r'v\d+': 4, r'\d+\.\d+\.\d+': 5,
    r'release|launch|announce|introducing': 4,
    r'benchmark|eval|score|accuracy|latency': 4,
    r'GPT-?\d|Claude|Gemini|Llama|Mistral|Qwen|DeepSeek': 3,
    r'open.?source|open.?weight': 4,
    r'AGI|ASI|super.?intelligence': 4,
    # Tech signals
    r'agent|agentic|RAG|fine.?tun|LoRA|RLHF|DPO': 3,
    r'inference|quantiz|GGUF|vLLM|TensorRT': 3,
    r'tool.?use|function.?call|MCP|A2A': 3,
    r'training|pretrain|post.?train|distill': 3,
    r'reasoning|chain.?of.?thought|CoT|o\d': 3,
    r'multimodal|vision|image.?gen|video.?gen|text.?to': 3,
    r'embedding|vector|knowledge.?graph': 2,
    # Business/market signals
    r'\$\d+[MBK]|billion|million|funding|valuation': 4,
    r'acqui[rs]|merger|IPO|partnership': 4,
    r'API|endpoint|SDK|platform': 2,
    r'enterprise|production|deploy': 2,
    # Research signals
    r'arxiv|paper|research|study|findings': 3,
    r'github\.com|repo|repository': 3,
    r'tutorial|guide|how.?to|cookbook': 2,
    # Controversy/hot takes
    r'controversy|debate|scam|fraud|layoff': 4,
    r'regulation|ban|restrict|policy': 3,
    r'doom|safety|alignment|risk': 3,
}

def engagement_score(t):
    likes = t.get('likeCount', 0) or 0
    rts = t.get('retweetCount', 0) or 0
    replies = t.get('replyCount', 0) or 0
    total = likes + rts * 2 + replies * 1.5
    if total > 1000: return 10
    if total > 500: return 8
    if total > 100: return 6
    if total > 50: return 4
    if total > 10: return 2
    return 0

def signal_score(text):
    score = 0
    matched = []
    for pattern, weight in SIGNAL_KEYWORDS.items():
        if re.search(pattern, text, re.IGNORECASE):
            score += weight
            matched.append(pattern)
    return score, matched

def is_rt_only(text):
    """Pure RT with <100 chars and no added commentary."""
    if text.startswith('RT @') and len(text) < 100:
        return True
    return False

# Score all tweets
scored = []
for t in tweets:
    text = t.get('text', '')
    if is_rt_only(text):
        continue

    sig, matched = signal_score(text)
    eng = engagement_score(t)

    # Link evidence boost
    has_gh = bool(re.search(r'github\.com', text, re.IGNORECASE))
    has_arx = bool(re.search(r'arxiv', text, re.IGNORECASE))
    has_url = bool(re.search(r'https?://', text))
    link_boost = 2 if has_gh else (1.5 if has_arx else (1 if has_url else 0))

    # CRITICAL: engagement fields are often all 0 (pitfall #18).
    # When eng==0, boost signal weight to ×8 and link_boost to ×3.
    if eng == 0:
        total = sig * 8 + link_boost * 3
    else:
        total = sig * 5 + eng + link_boost * 3

    if total > 0:
        scored.append({
            'text': text[:500],
            'author': t.get('author', {}),  # NOT 'user' (pitfall #12)
            'id': t.get('id', ''),
            'url': t.get('url', ''),
            'createdAt': t.get('createdAt', ''),
            'signal_score': sig,
            'engagement_score': eng,
            'total_score': total,
            'matched_keywords': matched[:5],
        })

scored.sort(key=lambda x: x['total_score'], reverse=True)
top = scored[:60]

# Print summary
print(f"Total tweets: {len(tweets)}")
print(f"After RT filter: {len(scored)}")
print(f"Top 60 selected")
if top:
    print(f"Score range: {top[0]['total_score']:.1f} - {top[-1]['total_score']:.1f}")
print("===")

# Output formatted for analyst consumption
for i, t in enumerate(top):
    author = t['author']
    handle = author.get('username', '?')
    name = author.get('name', handle)
    print(f"[{i+1}] @{handle} ({name}) | Score: {t['total_score']:.1f} (sig:{t['signal_score']} eng:{t['engagement_score']})")
    print(f"    {t['text'][:300]}")
    print(f"    URL: {t['url']}")
    print()
```

## Key Design Decisions

- **engagement=0 → signal×8**: Verified 2026-06-19. The default ×5 was too low when engagement is zero (which is almost always). 8x produces good separation.
- **link_boost×3**: GitHub/arxiv links are strong evidence signals. Even a bare URL gets ×3 when engagement is zero.
- **RT filter at <100 chars**: Pure RTs with no commentary are noise. RTs with added text (>100 chars) may contain signal.
- **`author` not `user`**: The fetch scripts map user info to `author` field (pitfall #12). Using `t['user']` will KeyError.

## Execution Pattern (Cron-safe, pitfall #15)

```bash
# Step 1: Write script via write_file tool → /tmp/score_tweets.py
# Step 2: Execute
python3 /tmp/score_tweets.py 2>&1
```

Never use `python3 << 'PYEOF'` heredoc — it gets blocked in strict cron environments.
