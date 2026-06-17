# Feishu 发送目标格式（2026-06-07 实战）

## 问题
`send_message` 使用 user_id（`ou_xxx`）作为 target 会报错：
```
Feishu media send failed: [230001] invalid receive_id
```

## 解决
使用 chat_id（`oc_xxx`）作为 target：

```
# 错误
target: feishu:ou_714d50c888dc32829dc4719d31c82fdc

# 正确
target: feishu:oc_99929d11c9332515fc59cfb22e1de2e0
```

## 获取正确的 target
运行 `send_message(action='list')` 获取可用目标列表，格式为：
```
feishu:oc_xxxxx (dm)
```

## MEDIA 发送
```bash
send_message(
  action='send',
  message='MEDIA:/path/to/file.png',
  target='feishu:oc_xxxxx'
)
```
