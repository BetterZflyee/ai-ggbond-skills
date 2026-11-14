# 云雾 API Key 定位与批量生图预检

## 适用场景

- 用户明确要求使用云雾 API / GPT-Image-2 生图
- 通用图片工具返回 `Incorrect API key provided: dummy`
- 配置文件中的 Key 显示为 `sk-xxx...xxxx`
- 准备一次生成多张公众号章节信息图

## 核心判断

`dummy` 只说明当前通用 OpenAI 链路没有配置真实凭证，不代表云雾 API 不可用。

包含 `...` 的 Key 是脱敏展示或占位文本，不能直接请求 API。判断 Key 时只输出状态和长度，永远不要打印完整值。

## 安全定位顺序

1. 当前 profile 的 `config.yaml`：检查 `image_gen.provider/model/base_url/key_env/api_key`。
2. 当前 profile 的 `.env`：检查 `YUNWU_API_KEY`、`OPENAI_BASE_URL`、`YUNWU_BASE_URL`。
3. 技能自己的 `.env` 或历史迁移目录：只在用户明确要继续使用该技能链路时查找。
4. 其他 profile 或配置备份：只能作为定位线索。若内容已被脱敏，不能复制使用；跨 profile 持久化修改仍需用户明确授权。

## Key 有效形态检查

```python
state = (
    "missing" if not key else
    "dummy" if key == "dummy" else
    "masked" if "..." in key else
    "too_short" if len(key) < 20 else
    "candidate"
)
print(state, len(key))
```

不要输出 `key` 本身。

## 云雾请求规范

- Base URL：`https://api.openlux.ai/v1`
- Endpoint：`/images/generations`
- Model：`gpt-image-2`
- 公众号横图：`1536x1024`
- 中文信息图必须使用全中文提示词、短标签和结构化网格

请求体示例：

```json
{
  "model": "gpt-image-2",
  "prompt": "全中文的信息图提示词",
  "n": 1,
  "size": "1536x1024",
  "quality": "high"
}
```

## 批量生成前置门禁

先只生成 1 张测试图。必须同时满足：

- HTTP 200
- 返回 `b64_json` 或可下载 URL
- 文件非空且能打开
- 中文文字基本可读
- 内容与章节对应

通过后再批量生成。首图失败时停止，不要连续请求导致限流或浪费余额。

## 错误处理

- 401：Key 无效或过期。要求用户更新云雾 Key。
- 403：Key 有效但无 GPT-Image-2 权限。让用户检查模型权限或套餐；未经授权不换模型。
- 429：限流。停止连续重试，等待后再做单图测试。
- 余额不足：停止批量生成，直接报告余额问题。
- 中文乱码：缩短标签、减少文字、强化“只允许指定中文”；连续 3 次乱码后停止，让用户改用 ChatGPT 端生成。

## 禁止事项

- 不把掩码 Key 当真实 Key。
- 不在日志、聊天或脚本输出中暴露完整 Key。
- 不因通用工具的 dummy Key 直接宣布云雾不可用。
- 不在首图未验证时并行生成多张。
- 不用 PIL 空壳图冒充 GPT-Image-2 成果。
