# X (Twitter) GraphQL API Reference

## Home Timeline Endpoint

```
POST https://x.com/i/api/graphql/{queryId}/HomeTimeline
```

### Query ID
- Current: `HJFjzBgCs16TqxewQOeLNg`
- May change when X deploys updates. To find new queryId:
  1. Open x.com in browser
  2. DevTools → Network → filter "graphql"
  3. Look for HomeTimeline requests in the URL

### Required Headers

| Header | Value | Source |
|--------|-------|--------|
| Cookie | `auth_token=...; ct0=...` | Browser cookies |
| Authorization | `Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA` | Public, embedded in X web client |
| x-csrf-token | `{ct0_value}` | Same as ct0 cookie |
| Content-Type | `application/json` | - |
| x-twitter-active-user | `yes` | - |
| x-twitter-client-language | `en` | - |

### Request Body

```json
{
  "variables": {
    "count": 20,
    "includePromotedContent": true,
    "latestControlAvailable": true,
    "requestContext": "launch",
    "withCommunity": true
  },
  "features": {
    // Feature flags - see fetch_x_timeline.py for full list
    // These may change with X client updates
  }
}
```

### Response Structure

X uses an **instruction-based** response format (not a flat tweet list):

```json
{
  "data": {
    "home": {
      "home_timeline_urt": {
        "instructions": [
          {
            "type": "TimelineAddEntries",
            "entries": [
              {
                "entryId": "tweet-123456",
                "content": {
                  "entryType": "TimelineTimelineItem",
                  "itemContent": {
                    "__typename": "TweetWithVisibilityResults",
                    "tweet": {
                      "tweet_results": {
                        "result": {
                          "__typename": "Tweet",
                          "legacy": { /* tweet data */ },
                          "core": {
                            "user_results": {
                              "result": {
                                "legacy": { /* user data */ }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

### Tweet Fields (in `legacy`)

| Field | Type | Description |
|-------|------|-------------|
| id_str | string | Tweet ID |
| full_text | string | Full tweet text |
| created_at | string | Timestamp (e.g. "Fri May 15 02:29:00 +0000 2026") |
| favorite_count | int | Like count |
| retweet_count | int | Retweet count |
| reply_count | int | Reply count |
| extended_entities.media | array | Media attachments |

### User Fields (in `core.user_results.result.legacy`)

| Field | Type | Description |
|-------|------|-------------|
| screen_name | string | Handle (without @) |
| name | string | Display name |
| profile_image_url_https | string | Avatar URL |

### Pagination

Response includes cursor entries (`TimelineCursor`) with `cursorType: "Bottom"` for next page.
Pass cursor value in `variables.cursor` for subsequent requests.

## Pitfalls

1. **Bearer token is public**: The Authorization bearer token is the same for all users, embedded in X's web client JS. Don't treat it as a secret.
2. **Feature flags change**: The `features` object may need updates when X changes their client. Check network tab if requests start failing.
3. **QueryId changes**: X periodically rotates queryIds. If you get "queryId not found", extract new one from browser DevTools.
4. **Rate limits**: X enforces rate limits. If you get 429, wait and retry.
5. **Proxy required in China**: `bird` CLI doesn't support proxies. Use Python `requests` which respects `HTTPS_PROXY` env var.

## References

- [API Design of X Home Timeline (trekhleb.dev)](https://trekhleb.dev/blog/2024/api-design-x-home-timeline/)
