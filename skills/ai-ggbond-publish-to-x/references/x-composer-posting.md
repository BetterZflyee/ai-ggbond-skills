# X 短帖（图 + 文）实操：CDP 接管已登录 Chrome

适用场景：把微信贴图/文章摘要同步发到 X，内容是「一段文字 + 1 张图」。
本流程在 2026-11-15 实测通过（账号 @Zflyee，Chrome 157，macOS）。

## 0. 通道选择

| 通道 | 结果 |
|---|---|
| Hermes 内置 browser → x.com | 403（请求被拒绝），不可用 |
| 本机已登录 Chrome + CDP | ✅ 稳定，本文以此为准 |

Chrome 的调试端口**不一定是 9222**。先探测：

```bash
pgrep -f "Google Chrome" | head
curl -s http://127.0.0.1:61485/json/version    # 换成实际端口
curl -s http://127.0.0.1:61485/json/list | python3 -m json.tool | grep -E '"url"|webSocketDebuggerUrl'
```

`/json/list` 里能直接看到已登录的 X 标签页，说明 cookies 在，不用重新注入。

## 1. 打开发帖框

浏览器级 WebSocket（`/json/version` 的 `webSocketDebuggerUrl`）→ `Target.createTarget` →
`Target.attachToTarget {flatten:true}` → `Runtime.enable` / `DOM.enable` / `Page.enable` / `Network.enable`。

## 2. 填文字：用合成 paste 事件，不要用 execCommand

```js
const ed = document.querySelector('[data-testid="tweetTextarea_0"]');
ed.focus();
const dt = new DataTransfer();
dt.setData('text/plain', TEXT);
ed.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
```

- `document.execCommand('insertText', ...)` 在 X 的 Draft.js 编辑器里会被话题联想劫持：
  正文末尾带 `#DeepSeek #AI开发 #API` 时，编辑器被塞进几十组重复的 hashtag 前缀，原文开头被顶掉。
- 本机 `pbcopy` 返回 exit 1（无 GUI 剪贴板权限），真实 Cmd+V 这条路走不通。
- 合成 paste 事件是一次原子输入，`innerText` 与源文本（去空白对比）完全一致。

## 3. 上传图片：file input + 小图

```js
// DOM.getDocument → DOM.querySelector 找到
input[data-testid="fileInput"]
// 然后
DOM.setFileInputFiles {files:[path], nodeId}
```

- 1.5MB PNG：**150 秒内没有任何 upload 请求**，进度条停在 0，附件位只有本地 `blob:` 预览。
- 同一张图 `sips -s format jpeg -Z 1400` 压到 268KB：2 秒内走完
  `upload.x.com/i/media/upload.json` 的 `INIT 202 → APPEND 204 → FINALIZE 201`。
- 结论：短帖配图先压成 ≤300KB 的 JPEG 再传。

## 4. 判断上传完成：别信 progressbar

`[role="progressbar"]` 上传成功后**仍留在 DOM**，`aria-valuenow` 一直是 `0`。
可靠的完成信号只有两个：

1. `Network.responseReceived` 里 `upload.x.com` 的 `FINALIZE` 返回 200/201；
2. `[data-testid="attachments"] img` 数量 > 0 且没有新的 upload 请求。

## 5. 不要向发帖框发 Escape

Escape 会触发关闭，弹出「保存帖子？」确认框，**只有「保存」和「放弃」两个选项，没有取消**：

- 「保存」→ 内容进草稿箱，发帖框关闭；
- 「放弃」→ 内容直接丢。

草稿恢复路径：`https://x.com/compose/post` → 点「草稿」→ 面板异步加载（等 3–4 秒）→
**点条目正文区域**（点缩略图只会预览）→ 编辑器恢复文字和图片。

## 6. 发布

- 发帖前把截图给用户确认，除非用户明确说「直接发」。
- 点「发帖」后以出现 `/status/<id>` 页面或列表刷新出新帖为准，按钮变灰不算成功。
