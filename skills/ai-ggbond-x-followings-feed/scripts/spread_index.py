#!/usr/bin/env python3
"""传播指数 v1.1：把 X 热度、中文平台热榜、维基关注度、HN 讨论度合成 0-100。

这不是某个厂商的官方指数，而是一个可解释的复合代理指标。
付费增强（NewsWhip predicted_interactions / BuzzSumo trending score）见 references/spread-index.md。
"""
from __future__ import annotations

import argparse
import json
import math
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 research-spread-index/1.0"
CST = timezone(timedelta(hours=8))


def http_json(url: str, timeout: int = 25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def http_text(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def log_norm(value: float, p95: float) -> float:
    if value <= 0:
        return 0.0
    return min(100.0, 100.0 * math.log10(1 + value) / math.log10(1 + p95))


def ratio_norm(value: float, p95: float) -> float:
    if value <= 0:
        return 0.0
    return min(100.0, 100.0 * math.log10(1 + value) / math.log10(1 + p95))


def fetch_wikipedia(title: str, lang: str = "en") -> dict | None:
    if not title:
        return None
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=7)
    t = urllib.parse.quote(title, safe="")
    url = (
        f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"{lang}.wikipedia/all-access/user/{t}/daily/{start:%Y%m%d}/{end:%Y%m%d}"
    )
    try:
        data = http_json(url)
        vals = [int(x["views"]) for x in data.get("items", [])]
        if not vals:
            return None
        last2 = sum(vals[-2:]) / min(2, len(vals))
        prev = vals[-7:-2]
        prev_avg = sum(prev) / len(prev) if prev else last2
        spike = last2 / max(prev_avg, 1)
        abs_score = log_norm(last2, 200_000)
        spike_score = ratio_norm(spike, 5)
        score = 0.6 * abs_score + 0.4 * spike_score
        return {
            "score": round(score, 1),
            "last2_avg": round(last2),
            "prev5_avg": round(prev_avg),
            "spike": round(spike, 2),
            "url": f"https://{lang}.wikipedia.org/wiki/{t}",
        }
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}", "score": None}


def fetch_douyin() -> list[dict]:
    try:
        data = http_json("https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/")
        return data.get("word_list", []) or []
    except Exception:
        return []


def fetch_baidu() -> list[dict]:
    try:
        html = http_text("https://top.baidu.com/board?tab=realtime")
        m = re.search(r"<!--s-data:(.*?)-->", html, re.S)
        if not m:
            return []
        data = json.loads(m.group(1))
        cards = data.get("data", {}).get("cards", [])
        if not cards:
            return []
        return cards[0].get("content", []) or []
    except Exception:
        return []


def match_hot(words: list[dict], keywords: list[str], word_key: str, value_key: str) -> dict:
    if not words or not keywords:
        return {"score": None, "matched": None, "rank": None}
    lowered = [(str(w.get(word_key, "")), w) for w in words]
    for idx, (text, item) in enumerate(lowered):
        low = text.lower()
        if any(k.lower() in low for k in keywords if k):
            score = 60 + 40 * (1 - idx / max(len(words) - 1, 1))
            return {
                "score": round(score, 1),
                "matched": text,
                "rank": idx + 1,
                "hot_value": item.get(value_key),
            }
    return {"score": None, "matched": None, "rank": None}


def fetch_hn(keywords: list[str], query_override: str | None = None) -> dict | None:
    query = (query_override or "").strip() or " ".join(keywords[:3])
    if not query:
        return None
    since = int(time.time()) - 7 * 86400
    params = urllib.parse.urlencode(
        {
            "query": query,
            "tags": "story",
            "numericFilters": f"created_at_i>{since}",
            "hitsPerPage": 1,
        }
    )
    try:
        data = http_json(f"https://hn.algolia.com/api/v1/search?{params}")
        hits = int(data.get("nbHits") or 0)
        return {"hits": hits, "score": round(log_norm(hits, 100), 1), "query": query}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}", "score": None}


def score_candidate(item: dict, platform: str, douyin: list[dict], baidu: list[dict]) -> dict:
    engagement = float(item.get("x_engagement") or 0)
    hours = max(float(item.get("x_hours") or 1), 1)
    velocity = engagement / hours
    eng_score = log_norm(engagement, 20_000)
    vel_score = log_norm(velocity, 1_000)
    x_score = 0.7 * eng_score + 0.3 * vel_score

    keywords = item.get("keywords") or []
    dy = match_hot(douyin, keywords, "word", "hot_value")
    bd = match_hot(baidu, keywords, "word", "hotScore")
    cn_scores = [x["score"] for x in (dy, bd) if x.get("score") is not None]
    cn_score = max(cn_scores) if cn_scores else None
    cn_detail = {"douyin": dy, "baidu": bd}

    wiki = fetch_wikipedia(item.get("wikipedia_title", ""), item.get("wikipedia_lang", "en"))
    wiki_score = wiki.get("score") if wiki and wiki.get("score") is not None else None

    hn = fetch_hn(keywords, item.get("hn_query"))
    hn_score = hn.get("score") if hn and hn.get("score") is not None else None

    if platform == "wechat":
        weights = {"x": 0.50, "cn": 0.25, "wiki": 0.15, "hn": 0.10}
    else:
        weights = {"x": 0.65, "cn": 0.05, "wiki": 0.15, "hn": 0.15}

    components = {"x": x_score, "cn": cn_score, "wiki": wiki_score, "hn": hn_score}
    available = {k: v for k, v in components.items() if v is not None}
    if not available:
        return {"error": "no components available"}
    weight_sum = sum(weights[k] for k in available)
    index = sum(weights[k] * available[k] for k in available) / weight_sum

    aihot_hits = item.get("aihot_hits")
    if aihot_hits == 0:
        index += 3
    elif isinstance(aihot_hits, int) and aihot_hits >= 5:
        index -= 5
    index = max(0.0, min(100.0, index))

    return {
        "title": item.get("title") or "",
        "platform": platform,
        "spread_index": round(index, 1),
        "tier": tier(index),
        "components": {k: (round(v, 1) if v is not None else None) for k, v in components.items()},
        "details": {
            "engagement": engagement,
            "hours": hours,
            "velocity_per_hour": round(velocity, 1),
            "x_eng_score": round(eng_score, 1),
            "x_velocity_score": round(vel_score, 1),
            "cn": cn_detail,
            "wikipedia": wiki,
            "hacker_news": hn,
            "aihot_hits": aihot_hits,
        },
    }


def tier(index: float) -> str:
    if index >= 80:
        return "S"
    if index >= 65:
        return "A"
    if index >= 55:
        return "B"
    return "C"


def main() -> None:
    parser = argparse.ArgumentParser(description="传播指数 v1：X + 中文热榜 + 维基 + HN 的复合评分")
    parser.add_argument("--input", required=True, help="候选 JSON 文件")
    parser.add_argument("--platform", choices=["wechat", "x"], default="wechat")
    parser.add_argument("--baseline", type=float, default=None, help="基准分，默认 80")
    parser.add_argument("--output", help="输出 JSON 路径")
    args = parser.parse_args()

    baseline = args.baseline if args.baseline is not None else 80
    items = json.loads(Path(args.input).read_text())
    if isinstance(items, dict):
        items = items.get("items", [])
    douyin = fetch_douyin()
    baidu = fetch_baidu()

    results = []
    for item in items:
        r = score_candidate(item, args.platform, douyin, baidu)
        if "error" not in r:
            r["baseline"] = baseline
            r["pass"] = r["spread_index"] >= baseline
        results.append(r)

    results.sort(key=lambda x: x.get("spread_index", -1), reverse=True)
    if args.output:
        Path(args.output).write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps({"platform": args.platform, "baseline": baseline, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
