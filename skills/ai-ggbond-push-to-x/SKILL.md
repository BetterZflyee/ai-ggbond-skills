---
name: ai-ggbond-push-to-x
description: Posts content and articles to X (Twitter). Supports regular posts with images/videos and X Articles (long-form Markdown). Use when user asks to "post to X", "tweet", "publish to Twitter", or "share on X".
version: 1.57.2
metadata:
  openclaw:
    homepage: https://github.com/BetterZflyee/ai-ggbond-skills#ai-ggbond-push-to-x
    requires:
      anyBins:
        - bun
        - npx
---

# Post to X (Twitter)

Posts text, images, videos, and long-form articles to X via a real Chrome browser.

## Script Directory

**Important**: All scripts are located in the `scripts/` subdirectory of this skill.

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `{baseDir}`
2. Script path = `{baseDir}/scripts/<script-name>.ts`
3. Replace all `{baseDir}` in this document with the actual path
4. Resolve `${BUN_X}` runtime: if `bun` installed → `bun`; if `npx` available → `npx -y bun`; else suggest installing bun

**Script Reference**:
| Script | Purpose |
|--------|---------|
| `scripts/x-browser.ts` | Regular posts (text + images), CDP fallback |
| `scripts/x-video.ts` | Video posts (text + video), CDP fallback |
| `scripts/x-quote.ts` | Quote tweet with comment, CDP fallback |
| `scripts/x-article.ts` | Long-form article publishing (Markdown), CDP fallback |
| `scripts/md-to-html.ts` | Markdown → HTML conversion |
| `scripts/copy-to-clipboard.ts` | Copy content to clipboard |
| `scripts/paste-from-clipboard.ts` | Send real paste keystroke |
| `scripts/check-paste-permissions.ts` | Verify environment & permissions |

## Execution Mode Selection (Required)

Choose exactly one mode before interacting with X:

1. If the user explicitly asks for Chrome Computer Use, use **Chrome Computer Use Mode**.
2. If the user explicitly asks for CDP/script mode, use **CDP Script Mode**.
3. Otherwise, prefer **Chrome Computer Use Mode**. For Markdown **X Articles with local content images**, use the tested X editor flow. Use CDP Script Mode only when the selected browser-control mode is unavailable or the UI upload/selection flow is unreliable.

Never use the in-app Browser for X publishing workflows.

## Preferences (EXTEND.md)

Check EXTEND.md in priority order — the first one found wins:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.ai-ggbond-skills/ai-ggbond-push-to-x/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/ai-ggbond-skills/ai-ggbond-push-to-x/EXTEND.md` | XDG |
| 3 | `$HOME/.ai-ggbond-skills/ai-ggbond-push-to-x/EXTEND.md` | User home |

If none found, use defaults.

**EXTEND.md supports**: Default Chrome profile

## Prerequisites

- Google Chrome or Chromium
- `bun` runtime
- First run: log in to X manually (session saved)

## Pre-flight Check (Optional)

Before first use, suggest running the environment check. User can skip if they prefer.

```bash
${BUN_X} {baseDir}/scripts/check-paste-permissions.ts
```

Checks: Chrome, profile isolation, Bun, Accessibility, clipboard, paste keystroke, Chrome conflicts.

**If any check fails**, provide fix guidance per item:

| Check | Fix |
|-------|-----|
| Chrome | Install Chrome or set `X_BROWSER_CHROME_PATH` env var |
| Profile dir | Shared profile at `ai-ggbond-skills/chrome-profile` |
| Bun runtime | `brew install oven-sh/bun/bun` (macOS) or `npm install -g bun` |
| Accessibility (macOS) | System Settings → Privacy & Security → Accessibility → enable terminal app |
| Clipboard copy | Ensure Swift/AppKit available (macOS Xcode CLI tools: `xcode-select --install`) |
| Paste keystroke (macOS) | Same as Accessibility fix above |
| Paste keystroke (Linux) | Install `xdotool` (X11) or `ydotool` (Wayland) |

## References

- **Regular Posts**: See `references/regular-posts.md` for manual workflow, troubleshooting, and technical details
- **X Articles**: See `references/articles.md` for long-form article publishing guide

---

## Chrome Computer Use Mode

Use this mode when the user explicitly asks for Chrome Computer Use, or when no Chrome-plugin preference is stated and Computer Use is available. This uses the user's existing Chrome window, cookies, login, extensions, and X session.

**General rules**:
- Start each assistant turn that controls Chrome by calling `get_app_state` for `Google Chrome`.
- Prefer element-index actions when available; use coordinates only for editor text selection or drag selection.
- Do not use the in-app Browser, Playwright, or CDP for X UI actions in this mode unless the user approves a mode change.
- Never click `Publish`, `Post`, or any externally visible submit action without an explicit final confirmation from the user in the current conversation.

**Regular posts**:
1. Open or navigate Chrome to `https://x.com/compose/post`.
2. Type the post text into the composer using Computer Use.
3. For each image, run:
   ```bash
   ${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts image /absolute/path/to/image.png
   ```
4. Paste with Computer Use (`super+v` on macOS, `control+v` on Windows/Linux), then wait until X finishes uploading media.
5. Ask for confirmation before clicking `Post`.

**Video posts**:
1. Open or navigate Chrome to `https://x.com/compose/post`.
2. Type the post text into the composer.
3. Use the visible media upload/file picker UI to attach the video.
4. Wait for upload and processing to complete.
5. Ask for confirmation before clicking `Post`.

**Quote tweets**:
1. Open the tweet URL in Chrome.
2. Use the visible quote/repost UI to choose Quote.
3. Type the comment.
4. Ask for confirmation before clicking `Post`.

**X Articles**:
1. Convert Markdown and keep the image map:
   ```bash
   ${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/x-article-body.html > /tmp/x-article.json
   ```
2. Read the JSON output for `title`, `coverImage`, and `contentImages` (`placeholder` → `localPath`).
3. In Chrome, open `https://x.com/compose/articles`, create or open the draft, upload the cover if present, and fill the title.
4. Copy rich HTML to the clipboard:
   ```bash
   ${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts html --file /tmp/x-article-body.html
   ```
5. Paste into the article body with Computer Use.
6. For each `contentImages` entry in placeholder order:
   - Locate the exact visible placeholder text such as `XIMGPH_3` and click it to set the insertion point.
   - Open the toolbar `Insert` dropdown, choose `Media`, then click the modal's icon button labeled `Add photos or video`.
   - Use the native file picker to choose the image's `localPath`.
   - Wait until the image block appears and any upload activity is finished.
   - If the placeholder remains above the inserted image, reselect exactly that placeholder text and press `Delete` first. Use `Backspace` only if `Delete` fails and the selected text is confirmed to be exactly the placeholder.
7. Verify no `XIMGPH_` placeholders remain and the expected images appear.
8. Open Preview and verify title, cover, body, links, and images.
9. Ask for explicit confirmation before clicking `Publish`.

---

## CDP Script Mode (Fallback)

Use the script sections below only when the selected browser-control mode is unavailable, unreliable, or explicitly not requested. These scripts launch or reuse a real Chrome instance via CDP and keep the browser open for review.

---

## Post Type Selection

Unless the user explicitly specifies the post type:
- **Plain text** + within 10,000 characters → **Regular Post**
- **Markdown file** (.md) → **X Article**

## Regular Posts

```bash
${BUN_X} {baseDir}/scripts/x-browser.ts "Hello!" --image ./photo.png
```

**Parameters**:
| Parameter | Description |
|-----------|-------------|
| `<text>` | Post content (positional) |
| `--image <path>` | Image file (repeatable, max 4) |
| `--profile <dir>` | Custom Chrome profile |

**Note**: Script opens browser with content filled in. User reviews and publishes manually.

---

## Video Posts

```bash
${BUN_X} {baseDir}/scripts/x-video.ts "Check this out!" --video ./clip.mp4
```

**Parameters**:
| Parameter | Description |
|-----------|-------------|
| `<text>` | Post content (positional) |
| `--video <path>` | Video file (MP4, MOV, WebM) |
| `--profile <dir>` | Custom Chrome profile |

**Limits**: Regular 140s max, Premium 60min. Processing: 30-60s.

---

## Quote Tweets

```bash
${BUN_X} {baseDir}/scripts/x-quote.ts https://x.com/user/status/123 "Great insight!"
```

**Parameters**:
| Parameter | Description |
|-----------|-------------|
| `<tweet-url>` | URL to quote (positional) |
| `<comment>` | Comment text (positional, optional) |
| `--profile <dir>` | Custom Chrome profile |

---

## X Articles

Long-form Markdown articles (requires X Premium).

```bash
${BUN_X} {baseDir}/scripts/x-article.ts article.md
${BUN_X} {baseDir}/scripts/x-article.ts article.md --cover ./cover.jpg
```

**Parameters**:
| Parameter | Description |
|-----------|-------------|
| `<markdown>` | Markdown file (positional) |
| `--cover <path>` | Cover image |
| `--title <text>` | Override title |

**Frontmatter**: `title`, `cover_image` supported in YAML front matter.

**Publish safety**: Do not use `--submit` or click `Publish` unless the user explicitly confirms the final public publish action.

---

## Troubleshooting

### Chrome debug port not ready

CDP fallback only: if a script fails with `Chrome debug port not ready` or `Unable to connect`, kill existing Chrome CDP instances first, then retry:

```bash
pkill -f "Chrome.*remote-debugging-port" 2>/dev/null; pkill -f "Chromium.*remote-debugging-port" 2>/dev/null; sleep 2
```

**Important**: This should be done automatically — when encountering this error, kill Chrome CDP instances and retry the command without asking the user.

## Notes

- First run: manual login required (session persists)
- CDP scripts only fill content into the browser by default; user must review and publish manually unless `--submit` is explicitly used
- Cross-platform: macOS, Linux, Windows

## Extension Support

Custom configurations via EXTEND.md. See **Preferences** section for paths and supported options.
