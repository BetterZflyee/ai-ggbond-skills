# execute_code API Key 审查问题

## 问题

`execute_code` 工具会对代码中的 API key 字符串进行审查/遮蔽，导致 Python 语法错误：
```
SyntaxError: unterminated string literal
```

具体表现：代码中 `line.startswith("YUNWU_API_KEY=***    api_key = line.split("=", 1)[1].strip()` 被截断。

## 解决方案

**不要在 execute_code 中读取含 API key 的 .env 文件。**

改用两步法：
1. `write_file` 将脚本写入 `/tmp/gen_xxx.py`（脚本中用 Path 读取 .env，不直接内联 key）
2. `terminal` 执行 `python3 /tmp/gen_xxx.py`

示例脚本结构：
```python
from pathlib import Path
api_key = ""
for line in Path("/Users/admin/.ai-ggbond-skills/.env").read_text().splitlines():
    parts = line.split("=", 1)
    if len(parts) == 2 and parts[0].strip() == "YUNWU_API_KEY":
        api_key = parts[1].strip()
        break
# ... 用 api_key 发请求
```

## 适用场景

所有需要在代码中调用外部 API（云雾、OpenAI 等）的图片生成/文本生成任务。
