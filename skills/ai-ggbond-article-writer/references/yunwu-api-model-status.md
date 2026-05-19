# 云雾 API 模型状态检查与故障排查

## gpt-image-2 模型可用性模式（2026-05 验证）

云雾 API 的 gpt-image-2 模型存在**间歇性不可用**，表现为：
- HTTP 429 + `model_not_found` — 分组/套餐不支持或渠道暂时下线
- HTTP 429 + `负载已饱和` — 临时限流，15-60秒后可恢复
- HTTP 401 + `无效的令牌` — API Key 过期或无效
- 连续超时（>60s 无响应） — 端点不可达

## 推送前必检流程

```bash
source ~/.ai-ggbond-skills/.env
python3 -c "
import requests, os
r = requests.post('https://yunwu.ai/v1/images/generations',
    headers={'Authorization': f'Bearer {os.environ[\"YUNWU_API_KEY\"]}', 'Content-Type': 'application/json'},
    json={'model': 'gpt-image-2', 'prompt': 'test', 'n': 1, 'size': '1024x1024'},
    timeout=30)
print(f'{r.status_code}: {r.text[:100]}')
"
```

## 状态判断表

| 响应 | 含义 | 操作 |
|------|------|------|
| 200 | 正常 | 直接跑 gen_images.py |
| 429 + model_not_found | 模型不可用 | 通知用户检查套餐/分组 |
| 429 + 负载已饱和 | 临时限流 | 等 15-60 秒重试 |
| 401 + 无效令牌 | Key 问题 | 检查 .env 配置 |
| 超时 | 端点不可达 | 尝试 api.apiplus.org |

## 备用端点优先级

1. `https://yunwu.ai` — 主站
2. `https://api.apiplus.org` — CF 站
3. `https://api3.wai.vip` — 国内服务器（DNS 可能不稳定）

## 降级方案

gpt-image-1 可作为降级备选，但**质量明显低于 gpt-image-2**，用户可能拒绝（实测：用户明确要求"必须用 gpt-image-2"）。

## gen_images.py 脚本注意事项

- Python 输出在后台运行时被缓冲，看不到实时进度
- 改用 `ls -la images/` 检查文件时间戳来判断进度
- 每张图约 60-120 秒生成，间隔 45 秒，6 张图总计约 10-12 分钟
- 脚本路径：`~/SuperIp/Article/<文件夹>/gen_images.py`
