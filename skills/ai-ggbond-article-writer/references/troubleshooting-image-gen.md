# 图片生成故障处理规范

> 版本：v1.2 | 更新日期：2026-05-15

---

## 🔴 核心铁律

### 铁律一：模型不可擅改

- 用户指定的模型（如 gpt-image-2）**必须严格使用**
- **禁止**因限流、报错、超时等原因自行切换到其他模型
- 不同模型差异巨大：
  - gpt-image-2：中文渲染最佳、1792x1024 支持、质量最高
  - gpt-image-1：不支持 1792x1024、中文渲染略逊
  - dall-e-3：中文支持一般、风格不同
  - 擅自换模型 = 出图风格不统一 = 全部作废

### 铁律二：API 问题找用户

- API Key 无效、额度耗尽、账户异常 → **立即暂停，通知用户**
- **禁止**自行尝试：
  - 其他 API 端点（api3.wai.vip / api.apiplus.org）
  - 其他 API Key
  - 其他模型
  - 其他生图服务（FAL / ComfyUI 等）
- 用户会自行解决，Agent 只需等待

### 铁律三：重试策略

| 场景 | 处理方式 |
|------|---------|
| 临时限流（429，无 code）| 等 15s → 30s → 60s 重试，最多 3 次 |
| 3 次仍失败 | **立即暂停，通知用户** |
| 模型不可用（503）| **立即暂停，通知用户** |
| API Key 无效（401）| **立即暂停，通知用户** |
| 上游负载饱和 | **立即暂停，通知用户** |
| **model_not_found（429 + code: "model_not_found"）** | **不是限流！是套餐/分组不支持该模型。立即通知用户检查套餐** |

> ⚠️ **关键区分**：429 有两种含义——"临时限流"和"model_not_found"。必须检查响应 JSON 中的 `code` 字段。如果 `code` 是 `"model_not_found"`，说明用户的 API 套餐/分组根本不包含该模型，重试多少次都没用。正确做法是通知用户去云雾后台（https://cx.tpkcur.click/）检查套餐，或切换分组。

### 铁律四：不要用 V4 脚本直接调用 gpt-image-2

- `generate_images_v4.py` 会传 `response_format` 参数
- 云雾 API 的 gpt-image-2 不支持该参数，报错：`Unknown parameter: 'response_format'`
- **正确做法**：用自定义 Python 脚本直接调 API
  ```python
  payload = {
      'model': 'gpt-image-2',
      'prompt': prompt,
      'n': 1,
      'size': '1792x1024'
  }
  # 不要传 response_format
  ```
- V4 脚本仍可用于 gpt-image-1 等其他模型

### 铁律五：批量生图必须分批，防超时

- gpt-image-2 每张图约 60-90 秒生成时间
- 600 秒超时只能跑 3-4 张，**必须分批处理**
- 推荐：每批 3 张，间隔 12 秒
- 超时后已生成的图片不会丢失，继续生成剩余部分即可

---

### Shell 环境变量传递陷阱

运行生图脚本时，`source ~/.env` 只在当前 shell 生效，**不会 export 到子进程**。Python 通过 `os.environ` 读不到变量。

**错误写法**：
```bash
source ~/.ai-ggbond-skills/.env && python3 gen_images.py
# Python 里 os.environ['YUNWU_API_KEY'] → KeyError
```

**正确写法**：
```bash
export $(grep -v '^#' ~/.ai-ggbond-skills/.env | grep -v '^$' | xargs) && python3 gen_images.py
```

或者在 Python 脚本内部自行读取 .env 文件：
```python
for p in [os.path.expanduser("~/.ai-ggbond-skills/.env")]:
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                if line.startswith("YUNWU_API_KEY="):
                    API_KEY = line.strip().split("=", 1)[1].strip()
```

## Python 后台脚本无输出问题

用 `background=true` 跑 Python 脚本时，输出会被缓冲，`process(log)` 看不到任何内容。

**解决**：加 `PYTHONUNBUFFERED=1` 环境变量或用 `python3 -u`：
```bash
export $(grep -v '^#' ~/.env | grep -v '^$' | xargs) && PYTHONUNBUFFERED=1 python3 gen_images.py
```

## article_manager.py 跨平台兼容问题

`article_manager.py` 脚本硬编码了 Windows 路径（`F:\\AI Workstation\\...`），在 macOS 上会报 `FileNotFoundError`。

**绕过**：不用脚本，手动创建文件夹：
```bash
mkdir -p ~/SuperIp/Article/YYYYMMDD-文章标题/{_briefs,_knowledge_base,images}
```

---

## 故障通知模板

### 模型不可用

```
⚠️ 生图模型 {model} 当前不可用（错误码：{status_code}，详情：{error_msg}）。

已暂停配图生成。请确认：
1. 等待一段时间后重试（我可以 15s/30s/60s 递增重试 3 次）
2. 更换模型（请指定模型名称）
3. 您去检查 API 账户状态后告诉我继续
```

### API Key / 账户问题

```
⚠️ 云雾 API 遇到认证/额度问题（错误码：{status_code}，详情：{error_msg}）。

已暂停配图生成。请检查：
- API Key 是否有效
- 账户额度是否充足
- 是否需要切换分组

确认后告诉我继续。
```

---

## 正确的生图脚本模板（gpt-image-2 专用）

```python
import os, requests, base64, time
from config_loader import load_all_env, apply_env_to_os
apply_env_to_os()

api_key = os.environ.get('YUNWU_API_KEY')
url = 'https://yunwu.ai/v1/images/generations'
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

def gen(prompt, filename, output_dir, size='1792x1024'):
    """用 gpt-image-2 生成图片，不传 response_format"""
    payload = {
        'model': 'gpt-image-2',
        'prompt': prompt,
        'n': 1,
        'size': size
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=300)
    if resp.status_code == 200:
        data = resp.json()
        img_data = data.get('data', [{}])[0]
        img_url = img_data.get('url', '')
        b64_data = img_data.get('b64_json', '')
        if img_url:
            r = requests.get(img_url, timeout=120)
            with open(f'{output_dir}/{filename}', 'wb') as f:
                f.write(r.content)
            return True, len(r.content)
        elif b64_data:
            b = base64.b64decode(b64_data)
            with open(f'{output_dir}/{filename}', 'wb') as f:
                f.write(b)
            return True, len(b)
    return False, f"HTTP {resp.status_code}: {resp.text[:200]}"

# 分批生成（每批3张，间隔12秒）
items = [("file.png", "prompt text"), ...]
for i, (fname, prompt) in enumerate(items):
    ok, info = gen(prompt, fname, output_dir)
    if i < len(items) - 1:
        time.sleep(12)
```

---

## format_article.py 配色修复

`format_article.py` 脚本默认使用绿色 `#07c160` 作为 h2 边框色。对于科技/商务主题文章，需要手动替换：

```bash
sed -i '' 's/#07c160/#1E88E5/g' output.html
```

---

## HTML 本地预览（图片显示问题）

相对路径图片在本地 `file://` 协议下无法显示。解决方案：

1. **HTTP 服务器预览**：`python3 -m http.server 8765` 在文章目录下
2. **base64 内嵌版**：将图片转为 data URI 嵌入 HTML（文件会很大，约 30MB）

---

## 更新日志

### 2026-05-15 v1.2
- 新增铁律三补充：429 + model_not_found 错误码区分（不是限流，是套餐不支持）
- 新增 Shell 环境变量传递陷阱（source vs export）
- 新增 Python 后台脚本无输出问题（PYTHONUNBUFFERED）
- 新增 article_manager.py 跨平台兼容问题及绕过方案

### 2026-05-11 v1.1
- 新增铁律四：V4 脚本 response_format bug 绕过
- 新增铁律五：批量生图分批策略
- 新增正确的生图脚本模板
- 新增 format_article.py 配色修复方法
- 新增 HTML 本地预览解决方案

### 2026-05-11 v1.0
- 初始版本：基于飞哥反馈，建立模型不可擅改 + API 问题找用户的铁律
