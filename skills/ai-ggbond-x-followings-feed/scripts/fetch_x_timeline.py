#!/usr/bin/env python3
"""
X/Twitter Home Timeline Fetcher (Python fallback for bird CLI)

bird CLI (Node.js) doesn't support HTTP_PROXY env vars.
This script uses requests library which respects proxy settings.

Usage:
    # With proxy (required in mainland China)
    export HTTPS_PROXY=http://127.0.0.1:7897
    python3 fetch_x_timeline.py [count]

    # Without proxy
    python3 fetch_x_timeline.py 20

Environment variables (from ~/.hermes/.env):
    AUTH_TOKEN - X auth_token cookie
    CT0        - X ct0 cookie (also used as csrf-token)

Output: JSON array of tweets to stdout
"""

import json
import os
import sys
import requests

# Auth tokens from env
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")
CT0 = os.environ.get("CT0", "")

if not AUTH_TOKEN or not CT0:
    print('{"error": "Missing AUTH_TOKEN or CT0 environment variables"}', file=sys.stderr)
    sys.exit(1)

# Tweet count from args
COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 20

# X GraphQL API endpoint
# Query ID for HomeTimeline - may change if X updates their API
QUERY_ID = "HJFjzBgCs16TqxewQOeLNg"
URL = f"https://x.com/i/api/graphql/{QUERY_ID}/HomeTimeline"

# Public bearer token (embedded in X's web client)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

headers = {
    "Cookie": f"auth_token={AUTH_TOKEN}; ct0={CT0}",
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "x-csrf-token": CT0,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-twitter-active-user": "yes",
    "x-twitter-client-language": "en",
}

variables = {
    "count": COUNT,
    "includePromotedContent": True,
    "latestControlAvailable": True,
    "requestContext": "launch",
    "withCommunity": True,
}

# Feature flags from X's web client (may change over time)
features = {
    "profile_label_improvements_pcf_label_in_post_enabled": False,
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}


def extract_tweets(data):
    """Extract tweets from X's instruction-based GraphQL response."""
    tweets = []
    instructions = (
        data.get("data", {})
        .get("home", {})
        .get("home_timeline_urt", {})
        .get("instructions", [])
    )

    for instruction in instructions:
        if instruction.get("type") != "TimelineAddEntries":
            continue

        for entry in instruction.get("entries", []):
            content = entry.get("content", {})
            if content.get("entryType") != "TimelineTimelineItem":
                continue

            item_content = content.get("itemContent", {})

            # Handle TweetWithVisibilityResults wrapper
            if item_content.get("__typename") == "TweetWithVisibilityResults":
                tweet_result = (
                    item_content.get("tweet", {})
                    .get("tweet_results", {})
                    .get("result", {})
                )
            else:
                tweet_result = (
                    item_content.get("tweet_results", {}).get("result", {})
                )

            if not tweet_result or tweet_result.get("__typename") != "Tweet":
                continue

            legacy = tweet_result.get("legacy", {})
            user_legacy = (
                tweet_result.get("core", {})
                .get("user_results", {})
                .get("result", {})
                .get("legacy", {})
            )

            username = user_legacy.get("screen_name", "")
            tweet_id = legacy.get("id_str", "")

            tweet = {
                "id": tweet_id,
                "text": legacy.get("full_text", ""),
                "createdAt": legacy.get("created_at", ""),
                "author": {
                    "username": username,
                    "name": user_legacy.get("name", ""),
                },
                "likeCount": legacy.get("favorite_count", 0),
                "retweetCount": legacy.get("retweet_count", 0),
                "replyCount": legacy.get("reply_count", 0),
                "url": f"https://x.com/{username}/status/{tweet_id}" if username and tweet_id else "",
            }
            tweets.append(tweet)

    return tweets


def main():
    try:
        response = requests.post(
            URL,
            headers=headers,
            json={"variables": variables, "features": features},
            timeout=30,
        )

        if response.status_code != 200:
            print(
                f'{{"error": "HTTP {response.status_code}", "body": "{response.text[:200]}"}}',
                file=sys.stderr,
            )
            sys.exit(1)

        data = response.json()

        # Check for API errors
        if "errors" in data:
            print(json.dumps({"error": data["errors"]}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)

        tweets = extract_tweets(data)
        print(json.dumps(tweets, ensure_ascii=False, indent=2))

    except requests.exceptions.ProxyError as e:
        print(f'{{"error": "Proxy error: {e}. Check HTTPS_PROXY env var."}}', file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f'{{"error": "Connection error: {e}. Check network/proxy."}}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'{{"error": "{e}"}}', file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
