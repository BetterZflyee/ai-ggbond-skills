#!/usr/bin/env python3
"""
X Followings Feed — Tweet Scoring & Filtering Script
=====================================================
Filters raw tweet JSON from fetch_x_following_paginated.py:
1. Removes pure RTs and very short tweets
2. Scores by engagement (like + 2*retweet + reply) + signal keyword boost
3. Applies recency boost: today 2x, yesterday 1.5x, 2 days ago 1.2x, older 1x
4. Outputs top-N tweets with category hints and timestamps for digest generation

Usage:
    python3 curate_and_score.py /tmp/x_following_latest.json [--top 50]
"""

import json, re, sys
from datetime import datetime, timezone, timedelta
from collections import Counter

SIGNAL_KW = [
    r'\b(GPT|Claude|Gemini|Llama|Mistral|DeepSeek|Qwen|Gemma|Phi|Command)\b',
    r'\b(open.?source|OSS|github\.com|arxiv|paper)\b',
    r'\b(benchmark|MMLU|GSM8K|HumanEval|AIME|GPQA|SWE-bench)\b',
    r'\b(API|SDK|release|launch|announce|update|upgrade)\b',
    r'\b(free|discount|giveaway|beta|waitlist)\b',
    r'\b(agent|workflow|RAG|fine.?tun|LoRA|inference|token)\b',
    r'\b(\$\d+|pricing|price|fee|cost)\b',
    r'\b(v?\d+\.\d+(\.\d+)?)\b',  # version numbers
    r'\b(AGI|ASI|alignment|safety|reasoning)\b',
    r'\b(YC|ycombinator|fundraising|Series|valuation)\b',
    r'\b(image|video|audio|3D|multimodal|vision)\b',
    r'\b(MCP|context|protocol|memory)\b',
    r'\b(CN|China|Chinese|国产)\b',
]

CATEGORY_PATTERNS = {
    '🔥EVENT':    r'(launch|release|announce|new|updated)',
    '🚀PRODUCT':  r'(benchmark|vs|compar|beats|outperform)',
    '💡INSIGHT':  r'(paper|arxiv|research|study)',
    '🎁DEAL':     r'(free|discount|giveaway|beta|waitlist|deal)',
    '🔗RESOURCE': r'(github|repo|tool|library|OSS)',
    '📊SIGNAL':   r'(warning|concern|controvers|risk)',
}

# Date format used by X API: "Sun Jun 28 23:45:25 +0000 2026"
X_DATE_FMT = '%a %b %d %H:%M:%S %z %Y'


def signal_score(text: str) -> int:
    s = 0
    for kw in SIGNAL_KW:
        if re.search(kw, text, re.IGNORECASE):
            s += 2
    if 'http' in text:
        s += 3
    return s


def engagement_score(tweet: dict) -> int:
    return (tweet.get('likeCount', 0) or 0) + \
           2 * (tweet.get('retweetCount', 0) or 0) + \
           (tweet.get('replyCount', 0) or 0)


def recency_boost(created_at: str) -> float:
    """Time-decay multiplier: today 2.0x, yesterday 1.5x, 2 days ago 1.2x, older 1.0x"""
    if not created_at:
        return 1.0
    try:
        dt = datetime.strptime(created_at, X_DATE_FMT)
        # Convert to UTC+8
        dt_cn = dt + timedelta(hours=8)
        now_cn = datetime.now(timezone(timedelta(hours=8)))
        days_diff = (now_cn.date() - dt_cn.date()).days
        if days_diff <= 0:
            return 2.0   # today
        elif days_diff == 1:
            return 1.5   # yesterday
        elif days_diff == 2:
            return 1.2   # 2 days ago
        else:
            return 1.0
    except:
        return 1.0


def parse_timestamp(created_at: str) -> str:
    """Convert X API timestamp to readable 'MM-DD HH:MM' format (UTC+8)"""
    if not created_at:
        return '?'
    try:
        dt = datetime.strptime(created_at, X_DATE_FMT)
        dt_cn = dt + timedelta(hours=8)
        return dt_cn.strftime('%m-%d %H:%M')
    except:
        return '?'


def categorize(text: str) -> str:
    for cat, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return cat
    return '💡INSIGHT'


def is_pure_rt(text: str) -> bool:
    return text.strip().startswith('RT @')


def main(filepath: str, top_n: int = 50):
    with open(filepath) as f:
        raw = f.read()

    # Extract JSON array from possibly noisy stdout capture
    start = raw.find('[')
    end = raw.rfind(']') + 1
    data = json.loads(raw[start:end])

    scored = []
    for t in data:
        text = t.get('text', '') or ''
        if is_pure_rt(text) or len(text.strip()) < 20:
            continue
        eng = engagement_score(t)
        sig = signal_score(text)
        rb = recency_boost(t.get('createdAt', ''))
        author = (t.get('author', {}) or {}).get('username', 'unknown')
        name = (t.get('author', {}) or {}).get('name', '')
        url = t.get('url', '')
        ts_display = parse_timestamp(t.get('createdAt', ''))
        # Total = (engagement + signal*5) * recency_boost
        base = eng + sig * 5
        total = int(base * rb)
        scored.append({
            'author': author,
            'name': name,
            'text': text[:400],
            'url': url,
            'eng_score': eng,
            'sig_score': sig,
            'recency_boost': rb,
            'total': total,
            'category': categorize(text),
            'createdAt': t.get('createdAt', ''),
            'ts_display': ts_display,
            'likeCount': t.get('likeCount', 0) or 0,
            'retweetCount': t.get('retweetCount', 0) or 0,
        })

    scored.sort(key=lambda x: x['total'], reverse=True)
    top = scored[:top_n]

    print(f"Filtered from {len(data)} → {len(scored)} tweets (removed RTs/short)\n")

    for i, t in enumerate(top):
        rb_label = f" ×{t['recency_boost']}" if t['recency_boost'] > 1.0 else ""
        print(f"[{t['category']}] @{t['author']} ({t['ts_display']}) (E{t['eng_score']} S{t['sig_score']} R{rb_label} T{t['total']})")
        print(f"  {t['text'][:200]}")
        print(f"  🔗 {t['url']}")
        if i < len(top) - 1:
            print()

    print(f"\n--- Category Distribution ---")
    for k, v in Counter(t['category'] for t in top).most_common():
        print(f"  {k}: {v}")

    # Return structured data for programmatic use
    return top


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Score and filter X following tweets')
    parser.add_argument('file', help='Path to raw tweet JSON file')
    parser.add_argument('--top', type=int, default=50, help='Number of top tweets to return')
    args = parser.parse_args()
    main(args.file, args.top)
