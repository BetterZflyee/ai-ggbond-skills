# YouTube logged-in Chrome subtitle diagnostic

Use this when direct InnerTube and `yt-dlp` are blocked by YouTube's bot check, and the user authorizes access to their already logged-in Chrome.

## What worked in this session

1. Ask the user to log in to YouTube in Chrome and enable remote debugging at `chrome://inspect/#remote-debugging`; they must accept Chrome's first CDP authorization dialog.
2. Establish the first CDP connection with browser-harness:
   ```bash
   browser-harness -c 'ensure_real_tab(); print(page_info())'
   ```
3. Open the video in the authenticated Chrome and inspect YouTube's player state:
   ```bash
   browser-harness -c 'new_tab("https://www.youtube.com/watch?v=VIDEO_ID"); wait_for_load(); print(js("JSON.stringify({loggedIn:!!document.querySelector(\"ytd-topbar-menu-button-renderer, ytd-notification-topbar-button-renderer\"), cap:window.ytInitialPlayerResponse?.captions?.playerCaptionsTracklistRenderer?.captionTracks?.map(t=>({lang:t.languageCode,name:t.name?.simpleText||t.name?.runs?.map(r=>r.text).join(\"\"),kind:t.kind||\"manual\",url:t.baseUrl}))||null})"))'
   ```
4. If `loggedIn: true` and caption tracks appear, use `yt-dlp --cookies-from-browser chrome` as a separate download attempt.

## Important interpretation

- Caption-track metadata proves YouTube exposed tracks to the authenticated player; it does **not** prove that a subtitle payload can be downloaded.
- If timedtext requests return HTTP 200 with a zero-byte body, report this precisely as **caption payload unavailable in the current session/region or not yet published**, rather than claiming the video definitely has no subtitles.
- Have the user manually enable CC and play 10–20 seconds once, then retry inspection/download. This can prompt real subtitle loading in their browser session.
- If payload still remains empty, pivot to audio transcription (user-provided file or an otherwise permitted audio acquisition path) or clearly label a metadata/third-party-summary result as non-verbatim.

## Useful evidence to capture

- Auth state (`loggedIn`)
- Available language, display name, and `kind` for each caption track
- Whether timedtext content was non-empty
- Whether `yt-dlp` successfully extracted browser cookies and listed subtitle languages
