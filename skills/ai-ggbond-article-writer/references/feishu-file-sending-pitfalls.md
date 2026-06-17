# Feishu File Sending Pitfalls

## Target Format for `send_message`

When sending files/images to Feishu via `send_message`, the `target` parameter must use the **chat_id** format, NOT the user_id format.

### ❌ Wrong (user_id)
```
target: feishu:ou_714d50c888dc32829dc4719d31c82fdc
```
Error: `invalid receive_id`

### ✅ Correct (chat_id)
```
target: feishu:oc_99929d11c9332515fc59cfb22e1de2e0
```

### How to Find the Correct Target

Run `send_message` with `action=list` to see available targets:
```
Available messaging targets:
  feishu:oc_99929d11c9332515fc59cfb22e1de2e0 (dm)
```

The `oc_` prefix is the chat_id. The `ou_` prefix is the user_id — do NOT use this.

### Sending Images

```
send_message(
    action="send",
    message="MEDIA:/absolute/path/to/image.png",
    target="feishu:oc_XXXXXXXX"
)
```

- Use absolute file paths
- MEDIA: prefix triggers file upload
- Works for .png, .jpg, .webp (inline), .md (attachment), audio (voice message)

### Common Failure Sequence

1. Try `target=feishu` → Error: "No home channel set"
2. Try `target=feishu:ou_XXXX` → Error: "invalid receive_id"  
3. Try `target=feishu:oc_XXXX` → ✅ Success

Always use `send_message(action="list")` first to get the correct target.
