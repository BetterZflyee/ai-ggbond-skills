# 批量图片生成预检

## 适用场景

一篇文章需要生成多张章节图、封面图或信息图时，在并行调用图片模型之前执行。

## 核心原则

**先验证一张，再批量生成。**

不要在未确认模型、密钥和输出链路可用时，同时发起多张图片请求。否则一个配置问题会被放大成多次失败、限流和额外成本。

## 预检流程

### 1. 检查当前 Profile 的图片配置

Hermes 多 Profile 环境中，图片工具应读取当前 Profile 的 `config.yaml`，不能默认使用 `~/.hermes/config.yaml`。

确认以下字段均存在：

```yaml
image_gen:
  provider: openai
  model: gpt-image-2
  base_url: https://api.openlux.ai/v1
  api_key: <有效密钥>
```

如果错误中出现 `Incorrect API key provided: dummy`，说明工具回退到了占位密钥。修复方法是让用户在终端对当前 Profile 执行：

```bash
hermes config set image_gen.provider openai
hermes config set image_gen.model gpt-image-2
hermes config set image_gen.base_url https://api.openlux.ai/v1
hermes config set image_gen.api_key 完整密钥
```

密钥必须由用户手动输入，Agent 不要通过聊天、`write_file` 或命令参数转存完整密钥。

### 2. 只生成一张样图

从批次中选文字最少、结构最简单的一张作为探针：

- 16:9 横版
- 1 个标题
- 3—5 个短标签
- 不先生成全部章节

样图成功后检查：

- 模型确实是 GPT-Image-2
- 返回了有效图片文件
- 中文可读
- 视觉风格符合要求
- 文件能写入目标目录

### 3. 中文文字质检

批量前先验证样图文字。优先使用短标签、结构化网格和大字号；避免长段落。若中文乱码：

1. 收缩为标题 + 3—5 个短标签；
2. 明确禁止英文、拼音、乱码和额外文字；
3. 重新生成并 OCR/视觉检查；
4. 连续 3 次仍乱码，停止批量生成并告知用户，不要继续烧额度。

### 4. 分批生成

样图通过后再按 2—3 张一组生成。每组完成后立即质检，避免最后才发现整批风格或文字错误。

推荐顺序：

```text
配置预检 → 1张样图 → 文字/风格质检 → 2—3张一组生成 → 逐组质检 → 插入文章
```

## 禁止事项

- 未做样图验证就并行生成整批图片；
- 图片接口失败后用 PIL 空壳图替代；
- 未经用户授权擅自更换模型；
- 把 Profile 配置缺失固化成“图片工具不可用”的结论；
- 跳过生成后中文文字检查。
