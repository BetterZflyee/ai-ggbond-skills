# gpt-image-2 中文渲染与女性角色信息图经验（2026-06-08 实战）

## 核心发现：英文 prompt + 中文内容

**之前错误认知**：必须用中文 prompt 才能生成中文文字。
**实际情况**：英文 prompt + 明确要求 "all text must be in Simplified Chinese" 效果更好。

**正确提示词模式**：
```
Create a 16:9 tech infographic, dark background #0A1628...
Title: "中文标题" in large glowing text.
Card 1: "中文标签" with description "中文描述"...
All text MUST be in Simplified Chinese (简体中文), clear and legible. No English text except technical terms.
```

**错误提示词模式**（中文 prompt 容易让模型自由发挥）：
```
创建一张16:9科技风信息图，深色背景#0A1628...
标题：「本周 GitHub 最火的 5 个项目」...
```

**原因**：中文 prompt 结构松散，模型容易偏离。英文 prompt 结构清晰，模型更容易遵循，同时指定中文输出保证文字质量。

## 女性角色信息图模式

飞哥要求"女性化""有魅力""可爱且成熟"时的配图模式。

**设计公式**：
- 角色占画面 25-30%（不能太大抢信息图主体）
- 角色风格：动漫风成熟女性，精致五官，自信微笑，眼影光泽
- 服装：与项目调性匹配的优雅服饰
- 信息密度：6+ 功能模块，含数据对比、兼容列表、安装命令
- 文字：全部简体中文

**已确认角色设计**：
| 项目 | 角色 | 服装 | 特征 |
|------|------|------|------|
| Headroom | 断舍离女王 | 深梅子色长裙 | 玫瑰金长发，手握水晶 |
| MarkItDown | 万能翻译官 | 深蓝制服 | 金色波波头+圆框眼镜 |
| Hermes Agent | 知识女神 | 祖母绿长裙 | 发尾渐变绿，衔尾蛇手镯 |

**提示词关键词**：
- `anime-style illustration of a mature elegant woman`
- `small figure, occupying 25-30% of the frame`
- `detailed face with soft features, confident smile, eye shadow highlights`
- `6+ information modules with data, comparisons, commands`
- `all text in Simplified Chinese`

## 搞笑副标题铁律

飞哥偏好每个项目配一句搞笑副标题，用「」包裹：
- 「装完之后Agent突然变话少了但事办了」
- 「她比你对象还了解你」
- 语气：自嘲、反差、接地气

## 配图生成后去水印

生成所有配图后，必须调用 ai-ggbond-remove-ai-marks 清除 C2PA/EXIF 元数据。
命令：`python3 {skills}/ai-ggbond-remove-ai-marks/scripts/batch_clean.py 图片目录/`

## 用户纠正记录

1. **"生成的图都没人看"** → 简单卡片堆叠不行，需要高密度信息图 + 视觉吸引力
2. **"信息图里面还是英文"** → 必须用英文 prompt 但指定中文输出
3. **"人物要小一点，信息图内容要多一些"** → 角色 25-30%，信息密度 6+ 模块
4. **"要有女性特有的细腻与吸引力"** → 动漫风成熟女性，精致五官，自信微笑
5. **"内容要带有AI味，要搞笑一点"** → 搞笑副标题 + 自嘲语气
