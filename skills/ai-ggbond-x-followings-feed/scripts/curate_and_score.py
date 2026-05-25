#!/usr/bin/env python3
"""
X Followings Feed — Tweet Scoring & Filtering Script
=====================================================
Filters raw tweet JSON from fetch_x_following_paginated.py:
1. Removes pure RTs and very short tweets
2. Scores by engagement (like + 2*retweet + reply) + signal keyword boost
3. Outputs top-N tweets with category hints for digest generation

Usage:
    python3 curate_and_score.py /tmp/x_following_latest.json [--top 50]
"""

import json, re, sys
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
        author = (t.get('author', {}) or {}).get('username', 'unknown')
        name = (t.get('author', {}) or {}).get('name', '')
        url = t.get('url', '')
        scored.append({
            'author': author,
            'name': name,
            'text': text[:400],
            'url': url,
            'eng_score': eng,
            'sig_score': sig,
            'total': eng + sig * 5,
            'category': categorize(text),
            'createdAt': t.get('createdAt', ''),
            'likeCount': t.get('likeCount', 0) or 0,
            'retweetCount': t.get('retweetCount', 0) or 0,
        })

    scored.sort(key=lambda x: x['total'], reverse=True)
    top = scored[:top_n]

    print(f"Filtered from {len(data)} → {len(scored)} tweets (removed RTs/short)\n")

    for i, t in enumerate(top):
        print(f"[{t['category']}] @{t['author']} (E{t['eng_score']} S{t['sig_score']} T{t['total']})")
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
