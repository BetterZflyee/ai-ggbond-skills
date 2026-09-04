# API 配置与 OpenLux 迁移（2026-09 实测）

## 当前可用链路

- Base URL：`https://api.openlux.ai/v1`
- 文生图：`POST /v1/images/generations`（OpenAI Images API 格式）
- 图生图/编辑：`POST /v1/images/edits`（multipart）
- 模型：`gpt-image-2`、`gpt-image-2-c`
- 鉴权：`GET /v1/models`（返回 200 且含 468 个模型 = Key 有效）

## 迁移背景

原云雾 `yunwu.ai` 系列域名已于 2026 年迁移：

| 旧入口 | 现状 |
|--------|------|
| `https://yunwu.ai/v1/images/generations` | 403：账号已迁移至 api.openlux.ai，老站仅保留历史查询 |
| `https://api.apiplus.org` | 403：同上 |
| `https://api3.wlai.vip` | 403：同上 |
| `https://api.openlux.ai` 旧 Key | 401：迁移前 Key 不能直接用于新站 |

**结论：必须登录 api.openlux.ai 控制台重新创建 API Key，再把 base_url 改为 `https://api.openlux.ai/v1`。**

## Key 存放位置

| 位置 | 用途 |
|------|------|
| `~/.hermes/profiles/<profile>/config.yaml` → `image_gen.api_key` | Hermes 内置 image_generate 工具 + 本 skill 脚本自动扫描 |
| `~/.ai-ggbond-skills/.env` → `YUNWU_API_KEY` | ai-ggbond 品牌脚本（article-writer/sticker-writer 等） |

建议同步两份。模型统一为 `gpt-image-2`，不要写 `gpt-image-2-medium`。

## Key 安全（重要）

- Agent 的 write_file / execute_code / terminal 传长 Key 可能被截断（51 位 → 13 位）或掩码为 `***`
- **设置 Key 必须由用户在本机终端手动编辑 config.yaml / .env**
- 脚本读取不受影响（直接从文件读，不经过 Agent 输出）

## edits 接口注意

OpenLux 的 `/v1/images/edits` **不支持 `format` 参数**。传了会报：

```
Unknown parameter: 'format' (invalid_request_error)
```

正确 multipart 字段：`image`、`prompt`、`model`、`n`、`size`、`quality`。

## 尺寸支持范围（gpt-image-2）

实测 OpenLux 前端列出：

- `1024x1024`（默认方图）
- `1536x1024`（16:9 横）
- `1024x1536`（9:16 竖）
- `2048x2048`
- `3840x2160` / `2160x3840`（4K 竖/横）
- 更大会被拒：先小图生成，再本地放大

quality 支持 `auto/low/medium/high`。

## 验证命令

```bash
# 1) Key 有效
curl https://api.openlux.ai/v1/models -H "Authorization: Bearer $KEY"

# 2) 极小生图（低质量最省钱）
curl https://api.openlux.ai/v1/images/generations \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"blue circle, no text","n":1,"size":"1024x1024","quality":"low"}'
```
