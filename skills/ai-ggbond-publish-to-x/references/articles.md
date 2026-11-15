# X Articles - Detailed Guide

Publish Markdown articles to X Articles editor with rich text formatting and images.

## Mode Selection

In Codex, choose the browser-control mode from the user's wording:

1. If the user says "Codex Chrome plugin", "Codex 自带的 Chrome 插件", `@chrome`, or Chrome Extension, use **Codex Chrome Plugin Workflow**. Do not try Computer Use first.
2. If the user explicitly asks for Chrome Computer Use, use **Computer Use Workflow**.
3. If the user explicitly asks for CDP/script mode, use **CDP Script Workflow**.
4. Otherwise, use Computer Use when available; if unavailable or blocked, use CDP Script Workflow.

Never use the in-app Browser for X Article publishing. Never switch away from an explicitly requested mode without explaining the blocker and getting approval.

## Prerequisites

- X Premium subscription (required for Articles)
- Google Chrome installed
- `bun` installed

## Usage

### Codex Chrome Plugin (When Requested)

Use the `chrome:Chrome` skill and its Node REPL browser client. Verify the connection with a lightweight call such as `browser.user.openTabs()`. If it fails, wait 2 seconds and retry once, then follow the Chrome skill's health checks.

Prepare the article HTML and image map:

```bash
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/x-article-body.html > /tmp/x-article.json
```

Copy generated HTML as rich text:

```bash
${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts html --file /tmp/x-article-body.html
```

Use the Chrome plugin's tab, Playwright-wrapper, CUA, clipboard, and file chooser APIs for all X UI operations. If upload fails with `Not allowed`, stop and tell the user to enable file URL access for the Codex Chrome Extension in `chrome://extensions` → Details.

### Chrome Computer Use

Prepare the article HTML and image map:

```bash
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/x-article-body.html > /tmp/x-article.json
```

Copy the generated HTML as rich text:

```bash
${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts html --file /tmp/x-article-body.html
```

Then use Codex Computer Use against `Google Chrome` for all X UI operations.

### CDP Script Fallback

```bash
# Publish markdown article (preview mode)
${BUN_X} {baseDir}/scripts/x-article.ts article.md

# With custom cover image
${BUN_X} {baseDir}/scripts/x-article.ts article.md --cover ./cover.jpg

# Actually publish
${BUN_X} {baseDir}/scripts/x-article.ts article.md --submit
```

Do not use `--submit` unless the user has explicitly confirmed the final public publish action.

## Markdown Format

```markdown
---
title: My Article Title
cover_image: /path/to/cover.jpg
---

# Title (becomes article title)

Regular paragraph text with **bold** and *italic*.

## Section Header

More content here.

![Image alt text](./image.png)

- List item 1
- List item 2

1. Numbered item
2. Another item

> Blockquote text

[Link text](https://example.com)

\`\`\`
Code blocks become blockquotes (X doesn't support code)
\`\`\`
```

## Frontmatter Fields

| Field | Description |
|-------|-------------|
| `title` | Article title (or uses first H1) |
| `cover_image` | Cover image path or URL |
| `cover` | Alias for cover_image |
| `image` | Alias for cover_image |

## Image & Video Handling

1. **Cover Image**: First image or `cover_image` from frontmatter. Must be an image — a video cannot be used as cover.
2. **Remote Images**: Automatically downloaded to temp directory.
3. **Placeholders**: Content media use `XIMGPH_N` placeholders. Any markdown image whose path ends in `.mp4/.mov/.m4v/.webm` is treated as a video (`kind: "video"`), everything else as an image.
4. **Insertion**: `x-article.ts` selects the placeholder, deletes it with a real Backspace key, then uses X's **Insert → Media** picker:
   - click `插入` → `媒体`
   - click the drop zone with a real mouse event
   - intercept the native file chooser (`Page.setInterceptFileChooserDialog`)
   - inject the file with `DOM.setFileInputFiles`
   - wait for `upload.x.com` INIT/APPEND/FINALIZE (images) or `upload2.json` + STATUS (videos)
5. **Cleanup**: after all media, `cleanupPlaceholders` removes any `XIMGPH_N` that Draft.js restored on re-render.

Do **not** use clipboard/Swift/AppleScript for article media. In automation or headless sessions NSPasteboard is unavailable and `copy-to-clipboard.ts image` fails with `Failed to write image to clipboard`.

### Video notes

```markdown
![捕获视频](video/catch.mp4)
```

- Supported containers: `.mp4`, `.mov`, `.m4v`, `.webm`
- Upload goes through `upload2.json` and asynchronous processing; allow up to 120s per video (`insertMediaViaPicker` uses that default)
- Keep clips short (≤ 2 minutes recommended) and ≤ 1080p to avoid long processing
- A video block cannot be the article cover; always set `cover_image` to an image

## Markdown to HTML Script

Convert markdown and inspect structure:

```bash
# Get JSON with all metadata
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md

# Output HTML only
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --html-only

# Save HTML to file
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/article.html
```

JSON output:
```json
{
  "title": "Article Title",
  "coverImage": "/path/to/cover.jpg",
  "contentImages": [
    {
      "placeholder": "XIMGPH_1",
      "localPath": "/tmp/x-article-i