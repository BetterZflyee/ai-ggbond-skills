# 云雾图片 Key 发现与验证

## 适用场景

当 `image_generate` 返回 `Incorrect API key provided: dummy`，但用户明确记得技能原本通过云雾 API 生图时，按本文排查。重点是找出**图片专用 Key**，而不是随便取配置文件里出现的第一个 `api_key`。

## 核心教训

同一个 Hermes 配置或历史备份里可能同时存在：

- 主模型 API Key
- fallback provider Key
- `image_gen` 图片专用 Key
- 已过期但仍保留的旧 Key
- 被安全机制掩码成 `sk-xxx...xxxx` 的不可用显示值

因此：

1. **禁止用正则取配置文件中的第一个完整 `api_key`。**
2. 优先读取 `image_gen.api_key`；若配置使用 `key_env`，再读取对应环境变量。
3. 被显示为带 `...` 的 Key 是掩码值，不能拿来请求 API。
4. `/v1/models` 返回 200 只证明 Key 能访问模型列表，**不能证明它有图片生成权限**。
5. 最终验证必须真实调用一次 `/v1/images/generations`，模型指定 `gpt-image-2`，使用低成本测试提示词和单张图片。

## 推荐发现顺序

1. 当前 profile 的 `config.yaml` 中 `image_gen` 区块。
2. `image_gen.key_env` 指向的环境变量。
3. 技能自己的 `.env` 或用户明确维护的凭据文件。
4. 当前 profile 的配置备份。
5. 其他 profile 仅用于只读定位；未经用户明确要求，不写回其他 profile。

不要把普通模型 provider 的 Key 误当成图片 Key。

## 安全验证

验证时不要打印完整 Key，只打印哈希指纹：

```python
fingerprint = hashlib.sha256(key.encode()).hexdigest()[:10]
```

对每个候选 Key 依次测试：

```text
GET  /v1/models
POST /v1/images/generations
```

图片生成测试建议：

```json
{
  "model": "gpt-image-2",
  "prompt": "纯蓝色圆形，白色背景，不要文字",
  "n": 1,
  "size": "1024x1024",
  "quality": "low"
}
```

只有图片端点返回 200，才把该 Key 标记为可用于正式生图。

## 常见误判

### 模型列表 200，所以图片一定可用

错误。主模型 Key 可能只能访问文本模型或模型列表；图片端点仍会返回 401/403。

### 历史配置中找到完整 Key，就直接批量生成

错误。历史 Key 可能已过期。必须先做低成本单图探针。

### 找到多个完整 Key，取第一个

错误。配置文件中的排列顺序不代表用途。应按所属配置块和实际图片端点验证结果选择。

## 正式生成前门禁

- [ ] Key 不含 `...`，长度合理
- [ ] Base URL 规范为 `https://api.openlux.ai/v1`
- [ ] 模型明确为 `gpt-image-2`
- [ ] `/v1/images/generations` 单图探针返回 200
- [ ] 返回体包含 `b64_json` 或 `url`
- [ ] 首张正式图完成中文质检后，再批量生成

## 批量策略

先生成一张代表性强、中文标签数量适中的图片。检查中文准确性、乱码、内容关联与统一视觉。首张通过后再生成剩余图片，避免错误配置或文字质量问题连续消耗余额。
