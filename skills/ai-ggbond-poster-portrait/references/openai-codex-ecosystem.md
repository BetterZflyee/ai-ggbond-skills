# OpenAI Codex 工具生态调研 (2026-06-10)

## Codex Desktop vs Codex CLI vs OpenAI API

| 工具 | 安装方式 | 用途 | 图片生成 |
|------|---------|------|----------|
| **Codex Desktop** | `/Applications/Codex.app` (macOS) | 代码生成、执行、沙盒 | ❌ 不支持 |
| **Codex CLI** | `npm install -g @openai/codex` | 命令行代码生成、执行 | ❌ 不支持 |
| **OpenAI Images API** | 需要 API key + 充值 | GPT Image 2 图片生成 | ✅ 支持 |
| **ChatGPT Plus** | 网页/应用订阅 | 对话、代码、图片（界面操作） | ⚠️ 仅界面，无 API |

## 关键结论

1. **Codex Desktop/CLI 是代码工具，不是图片生成工具**
   - Codex = 代码沙盒 + 执行环境
   - 无法通过 Codex 调用 GPT Image 2

2. **ChatGPT Plus ≠ OpenAI API**
   - Plus 订阅是网页/应用层的消费级产品
   - API 是独立的开发者服务，需要单独注册和充值
   - 两者账户体系独立，Plus 订阅不提供 API 额度

3. **GPT Image 2 图片生成需要的条件**
   - OpenAI API key（在 platform.openai.com 注册）
   - 账户余额（按量计费，约 $0.04-0.08/张）
   - 调用 `/v1/images/generations` 端点

## 用户环境调研结果

```bash
# Codex Desktop (已安装)
/Applications/Codex.app
~/Library/Logs/com.openai.codex/  # 日志目录

# Codex CLI (未安装)
which codex  # not found
npm list -g | grep codex  # not found

# OpenAI API Key (未配置)
echo $OPENAI_API_KEY  # empty
cat ~/.openai/api_key  # not found
```

## 替代方案（已验证）

- **云雾 API (yunwu.ai)**：OpenAI 代理服务，已配置 API key，但余额不足时需充值
- **ComfyUI**：本地生成，需要 GPU 环境配置
