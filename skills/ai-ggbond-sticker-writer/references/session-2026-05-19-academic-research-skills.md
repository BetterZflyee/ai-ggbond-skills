# 2026-05-19：academic-research-skills 贴图工作流复盘

## 触发信号
用户明确纠正：“你要调用 AI-GGBOND-STICKER-WRITER 这个技能来做 academic-research-skills 贴图呢”。

## 学到的规则
- 当用户点名要求使用本技能时，不能只加载 skill、手写 Markdown 或口头说“已按技能做”。
- 必须实际调用本技能脚本/类：`scripts/sticker_manager.py` 或 `StickerManager.generate_sticker()`，生成标准目录结构：
  - `[年月日时分]-[标题]/`
  - `[年月日时分]-[标题].md`
  - `images/prompt.md`
- 执行后要读取生成文件做验证，再回复用户路径。

## 本次暴露的脚本坑
旧版 `sanitize_filename()` 的 emoji 正则包含 `\U000024C2-\U0001F251`，范围过宽，会误删 CJK 中文字符，导致标题“⚠️AI不是论文代写员，是你的学术安全带”被清洗成 `AI`，目录名异常为：

```text
202605191050-AI
```

已修复：移除超宽范围，改用更窄 emoji 区段 + variation selector 清理。

## 未来验证清单
1. 运行 `StickerManager.generate_sticker()`。
2. 检查终端输出路径。
3. `read_file` 读取生成 `.md`，确认正文完整。
4. `read_file` 读取 `images/prompt.md`，确认提示词存在。
5. 检查文件夹标题是否保留中文；若只剩英文片段，说明文件名清洗仍有问题。
