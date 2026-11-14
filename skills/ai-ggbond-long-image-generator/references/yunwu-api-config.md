# 云雾 API 配置详解

## 配置位置（Profile-aware）

Hermes 使用 Profile 时，凭证可能位于当前 Profile，而不是全局路径。**严禁把 `gongcheng` 或任何固定 Profile 写死为唯一来源。**

先定位当前 Profile 的配置：

```bash
hermes -p <当前profile> config path
hermes -p <当前profile> config env-path
```

### 1. 当前 Profile `.env`（优先检查）

常见的云雾 OpenAI 兼容配置：

```bash
OPENAI_API_KEY="sk-xxx...xxx"
OPENAI_BASE_URL="https://api.openlux.ai/v1"
```

AI朱朱侠旧版脚本可能只读取：

```bash
YUNWU_API_KEY="sk-xxx...xxx"
YUNWU_BASE_URL="https://api.openlux.ai"
```

如果当前 Profile 已有有效的 `OPENAI_API_KEY`，但脚本只识别 `YUNWU_API_KEY`，可在**同一 Profile `.env`**增加同值兼容变量。不要复制到其他 Profile。

### 2. 当前 Profile `config.yaml`

```yaml
image_gen:
  provider: openai
  model: gpt-image-2
  base_url: https://api.openlux.ai/v1
  api_key: sk-xxx...xxx
```

### 3. 全局或旧版位置（仅作回退）

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.ai-ggbond-skills/.env`
- Skill 本地 `.env`

**排查铁律：不要只检查当前进程环境或 `config.yaml`。** 当前 Gateway 进程未导出变量，并不代表 Profile `.env` 没有 Key。

## API Key 获取

1. 访问 https://api.openlux.ai
2. 注册/登录账号
3. 进入 API Keys 页面
4. 生成新的 API Key
5. 复制完整 Key（通常 50+ 字符）

## 配置方法

### 方法 1：hermes config set（可能截断）
```bash
hermes config set image_gen.api_key "sk-xxx...xxx"
hermes config set image_gen.base_url "https://api.openlux.ai/v1"
hermes config set image_gen.model "gpt-image-2"
```

⚠️ **注意**：`hermes config set` 可能会截断长 Key。如果设置后仍报错，请用方法 2。

### 方法 2：手动编辑配置文件（推荐）
```bash
# 打开配置文件
nano ~/.hermes/profiles/gongcheng/config.yaml

# 找到 image_gen 部分，修改 api_key
image_gen:
  base_url: https://api.openlux.ai/v1
  api_key: sk-完整的API-Key
  model: gpt-image-2

# 保存退出
```

### 方法 3：Python 脚本读取
```python
import yaml

config_path = '~/.hermes/profiles/gongcheng/config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

api_key = config.get('image_gen', {}).get('api_key', '')
# yaml 库读取不会截断
```

## 错误排查

### 401 - 无效令牌
**原因**：API Key 过期、无效、或被截断
**解决**：
1. 检查 Key 长度（应为 50+ 字符）
2. 到云雾 API 后台重新生成 Key
3. 手动编辑 config.yaml 填入完整 Key

### 403 - 无权限访问模型
**原因**：该 Key 没有目标模型的使用权限
**解决**：
1. 尝试其他模型（gpt-image-2、gpt-image-1、flux-1.1-pro）
2. 联系云雾 API 客服开通模型权限
3. 使用其他有权限的 API Key

### 429 - 频率限制
**原因**：短时间内请求过多
**解决**：
1. 等待 120 秒后重试
2. 减少并发请求
3. 使用分段渲染时增加间隔

### SSL 错误
**原因**：网络代理或证书问题
**解决**：
1. 设置代理：`export https_proxy=http://127.0.0.1:7897`
2. 或使用备用链路：
   - https://api.openlux.ai/v1
   - https://api.openlux.ai/v1

## 多链路配置

云雾 API 支持多链路自动切换：

```bash
# 环境变量方式
export YUNWU_BASE_URLS="https://api.openlux.ai,https://api.openlux.ai,https://api.openlux.ai"
```

脚本会按顺序尝试，直到成功。

## 验证配置

```bash
# 运行测试脚本
python3 ~/.hermes/skills/ai-ggbond-long-image-generator/scripts/test_yunwu_api.py

# 期望输出：
# 📏 Key 长度: 56 字符
# ✅ API 连接成功!
# ✅ 测试图片已保存: /tmp/api_test_success.png
```

## 安全注意事项

1. **不要提交 API Key 到 Git**
2. **不要在脚本中硬编码 Key**
3. **使用环境变量或配置文件**
4. **定期轮换 API Key**
5. **监控 API 使用量**

## 相关资源

- 云雾 API 官网：https://api.openlux.ai
- API 文档：https://api.openlux.ai/docs
- 状态页：https://status.yunwu.ai
