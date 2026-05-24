#!/usr/bin/env python3
"""Fetch and format GitHub Trending repositories.

MVP design:
- Uses Python stdlib only.
- Parses GitHub Trending HTML with tolerant regex/string patterns.
- Outputs JSON or Markdown for Hermes secondary analysis.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional

BASE_URL = "https://github.com/trending"
VALID_SINCE = {"daily", "weekly", "monthly"}


@dataclass
class Repo:
    rank: int
    repo: str
    url: str
    description: str
    language: str
    stars: int
    forks: int
    growth: str
    built_by: List[str]


def build_url(language: str = "", since: str = "daily") -> str:
    language = (language or "").strip().strip("/")
    path = f"/{urllib.parse.quote(language)}" if language else ""
    return f"{BASE_URL}{path}?since={urllib.parse.quote(since)}"


def fetch_html(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 ai-ggbond-github-trending/1.0 (+Hermes Agent)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            if status != 200:
                raise RuntimeError(f"GitHub returned HTTP {status}")
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub returned HTTP {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error while fetching GitHub Trending: {e.reason}") from e


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_int(text: str) -> int:
    cleaned = re.sub(r"[^0-9]", "", text or "")
    return int(cleaned) if cleaned else 0


def parse_trending(page: str) -> List[Repo]:
    # GitHub Trending repo cards are article.Box-row blocks. Current GitHub HTML
    # sometimes omits explicit </article>; split by article starts instead of
    # requiring a closing tag.
    starts = [m.start() for m in re.finditer(r'<article\b[^>]*class="[^"]*Box-row[^"]*"', page, flags=re.I)]
    articles = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else page.find("</main>", start)
        if end == -1:
            end = min(len(page), start + 50000)
        articles.append(page[start:end])
    repos: List[Repo] = []

    for article in articles:
        href = ""
        for candidate in re.findall(r'<h2[\s\S]*?<a\b[^>]*href="([^"]+)"[\s\S]*?</a>', article, flags=re.I):
            candidate = html.unescape(candidate).strip()
            stripped = candidate.strip("/")
            if stripped.count("/") == 1:
                href = candidate
                break
        if not href:
            repo_match = re.search(r'href="/([^/"\s]+/[^/"\s]+)"', article, flags=re.I)
            if repo_match:
                href = "/" + html.unescape(repo_match.group(1)).strip()
        if not href:
            continue
        repo = href.strip("/")
        if repo.count("/") != 1:
            continue
        url = "https://github.com/" + repo

        desc = ""
        desc_match = re.search(r'<p\s+class="[^"]*col-9[^"]*"[^>]*>([\s\S]*?)</p>', article, flags=re.I)
        if desc_match:
            desc = strip_tags(desc_match.group(1))

        language = ""
        lang_match = re.search(r'<span\s+itemprop="programmingLanguage">([\s\S]*?)</span>', article, flags=re.I)
        if lang_match:
            language = strip_tags(lang_match.group(1))

        # Star and fork links appear as href="/owner/repo/stargazers" and /network/members.
        stars = 0
        forks = 0
        star_match = re.search(r'href="/' + re.escape(repo) + r'/stargazers"[^>]*>([\s\S]*?)</a>', article, flags=re.I)
        if star_match:
            stars = parse_int(strip_tags(star_match.group(1)))
        fork_match = re.search(r'href="/' + re.escape(repo) + r'/forks"[^>]*>([\s\S]*?)</a>', article, flags=re.I)
        if not fork_match:
            fork_match = re.search(r'href="/' + re.escape(repo) + r'/network/members"[^>]*>([\s\S]*?)</a>', article, flags=re.I)
        if fork_match:
            forks = parse_int(strip_tags(fork_match.group(1)))

        growth = ""
        growth_match = re.search(r'<span[^>]*class="[^"]*float-sm-right[^"]*"[^>]*>([\s\S]*?)</span>', article, flags=re.I)
        if growth_match:
            growth = strip_tags(growth_match.group(1))

        built_by = []
        for avatar_alt in re.findall(r'<img[^>]+alt="@([^"]+)"', article, flags=re.I):
            built_by.append(html.unescape(avatar_alt).strip())

        repos.append(
            Repo(
                rank=len(repos) + 1,
                repo=repo,
                url=url,
                description=desc,
                language=language,
                stars=stars,
                forks=forks,
                growth=growth,
                built_by=built_by[:8],
            )
        )

    return repos


def keyword_filter(repos: Iterable[Repo], keyword: str) -> List[Repo]:
    keys = [k.strip().lower() for k in (keyword or "").split(",") if k.strip()]
    if not keys:
        return list(repos)
    matched = []
    for repo in repos:
        haystack = " ".join([repo.repo, repo.description, repo.language, repo.growth]).lower()
        if any(k in haystack for k in keys):
            matched.append(repo)
    return matched


def fmt_num(n: int) -> str:
    return f"{n:,}"


def escape_md(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def to_markdown(repos: List[Repo], source_url: str, language: str, since: str, keyword: str) -> str:
    lines = []
    title_bits = ["GitHub Trending"]
    if language:
        title_bits.append(language)
    title_bits.append(since)
    if keyword:
        title_bits.append(f"keyword={keyword}")
    lines.append(f"## {' / '.join(title_bits)}")
    lines.append("")
    lines.append(f"Source: {source_url}")
    lines.append("")
    if not repos:
        lines.append("无匹配项目。建议放宽关键词，先全量抓取后再做语义判断。")
        return "\n".join(lines)
    lines.append("| Rank | Repo | Language | Stars | Forks | Growth | Description |")
    lines.append("|---:|---|---|---:|---:|---|---|")
    for r in repos:
        lines.append(
            f"| {r.rank} | [{escape_md(r.repo)}]({r.url}) | {escape_md(r.language)} | {fmt_num(r.stars)} | {fmt_num(r.forks)} | {escape_md(r.growth)} | {escape_md(r.description)} |"
        )
    return "\n".join(lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GitHub Trending repositories and output JSON or Markdown.")
    parser.add_argument("--language", default="", help="GitHub Trending language slug, e.g. python/typescript/go/rust/javascript")
    parser.add_argument("--since", default="daily", choices=sorted(VALID_SINCE), help="Trending window: daily, weekly, monthly")
    parser.add_argument("--limit", type=int, default=20, help="Maximum repositories to return")
    parser.add_argument("--keyword", default="", help="Comma-separated local filter over repo/name/description/language")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--markdown", action="store_true", help="Output Markdown table")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout seconds")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    url = build_url(args.language, args.since)
    try:
        page = fetch_html(url, timeout=args.timeout)
        repos = parse_trending(page)
        repos = keyword_filter(repos, args.keyword)
        repos = repos[: max(args.limit, 0)]
    except Exception as exc:  # noqa: BLE001 - CLI should produce clean errors.
        payload = {"ok": False, "error": str(exc), "source_url": url, "repos": []}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"ERROR: {exc}\nSource: {url}", file=sys.stderr)
        return 1

    if args.json:
        payload = {
            "ok": True,
            "source_url": url,
            "language": args.language,
            "since": args.since,
            "keyword": args.keyword,
            "count": len(repos),
            "repos": [asdict(r) for r in repos],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(repos, url, args.language, args.since, args.keyword))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
