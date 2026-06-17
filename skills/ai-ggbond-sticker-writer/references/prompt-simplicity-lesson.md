# 提示词简洁性经验（2026-06-09）

## 核心教训

用户多次偏爱**简洁直接的提示词**（3-4句视觉描述），而非我过度工程化的多段落长提示词。

### 用户偏好的提示词风格（3-4句）

```
A confident mature woman in a fitted dark navy dress with gold jewelry,
sitting at a sleek desk with a holographic floating screen showing code.
She has a slight smirk, one hand on keyboard. Magazine luxury style,
deep navy background #0a1628 with rose gold #b76e79 accents and gold
data particles floating. Tech-luxury aesthetic. No text in image.
```

```
High-density infographic style. A mature woman in white fitted blazer
holding a tablet, standing on the right side (30% of frame). Left side
shows 6 organized information modules in rose gold and champagne gold
cards on deep navy background. Clean data visualization with icons.
Magazine editorial luxury tech style. No text in image.
```

### 我的错误：过度工程化

我写的版本包含：
- 15+ 个参数段（Photography style / Scene / Clothing / Temperament / Body type / Camera angle / Pose / Lighting / Filter / Background...）
- 英文参数标签 + 中文解释混合
- 安全词清单内嵌
- 多个风格参考词叠加

**结果**：用户两次把自己的短提示词换回来，说明我的版本反而不如简洁版好用。

### 规则

1. **用户给的提示词 → 直接用**，不要"优化"或"扩展"
2. **自己写提示词时**：3-5句视觉描述即可，不要堆参数段
3. **poster-portrait技能的参数模板**适用于用户主动要求"按poster-portrait格式写"的场景，不要默认使用
4. **gpt-image-2的提示词理解力很强**：简洁自然语言 > 结构化参数堆叠
