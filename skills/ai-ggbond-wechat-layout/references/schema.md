# 输入与输出契约

## Markdown

支持首行 `# 标题`、开头的 `副标题：...`（可被粗体包裹）、平铺 YAML 元信息、二三级标题、自然段、粗体、强调、行内代码/链接、独立行图片、非嵌套列表、引用、围栏代码、标准管道表格。软换行合并为段内空格，段落边界保留。导入动作写入 `checks.json.transformations`。

复杂 YAML、原始 HTML、多层列表、引用式链接、混在文字中的图片需先转换为 JSON。不要为让解析器通过而删除内容。导入器是有边界的 Markdown 子集，不是完整 CommonMark 实现。

## JSON

```json
{
  "schema_version": 1,
  "meta": {"title": "标题", "summary": "摘要", "author": "AI朱朱侠", "cover": "images/cover.png"},
  "blocks": [
    {"id": "opening", "type": "paragraph", "text": "第一段，**保留已有强调**。"},
    {"id": "topic", "type": "heading", "level": 2, "text": "章节标题"},
    {"id": "photo", "type": "image", "src": "images/photo.jpg", "alt": "辅助描述"}
  ]
}
```

`cover`、`summary`、`author` 可省略，推送前按实际需要补全。标题必填。组件 ID 可省略；指定时仅字母、数字、下划线或短横线且唯一。

| type | 字段 | 行为 |
|---|---|---|
| paragraph | text；align:left/justify 可选 | 保留段落，混排可局部左对齐 |
| heading | text；level:2/3 | 无正文 h1 |
| quote | text；attribution 可选 | 引文与出处分开 |
| list | items:文字数组；ordered、start 可选 | 无嵌套列表 |
| steps | items:[{title,text}] | 有序步骤 |
| table | headers:文字数组、rows:二维文字数组 | 列数一致；按密度和比较任务选择布局，详见下文 |
| image | src；alt、role 可选 | 有 caption 必须明确 show_caption:true；详见下文 |
| code | text；language 可选 | 转义后保留代码，不强制显示语言标签 |
| timeline | items:[{label,text}] | 保留顺序 |
| callout | text | 文字强调，不加装饰卡片 |
| faq | items:[{question,answer}] | 完整展开答案 |
| comparison | items:[{title,text}] | 手机纵向对比 |
| metrics | items:[{label,value}] | value 为字符串，可含单位 |
| chart | title、items:[{label,value}] | 2–12 项非负有限数；unit/source/max_value 可选 |
| reveal | prompt、answer | 静态版完整显示问答 |

文字支持上述行内 Markdown，原始 HTML 会被转义。表格单元格使用字符串保留小数位/货币/百分比/单位，如 `"12.00%"`。柱形图使用数值，需保留原始数值格式时用表格。数据不会联网更新。

本地图片相对输入文件解析，复制到交付包 `assets/`。支持 PNG/JPEG/WebP/GIF；缺图直接报错。HTTPS 图片不自动下载，记录可达性与许可待核验；代码许可证不能替代图片许可。

## 表格的阅读任务

- `layout`：`auto`（默认）、`table`（完整矩阵）、`split`（分组比较）、`records`（逐条字段）。短小四列表可以保留矩阵，宽比较表自动分组，每组重复关键列，保持对象关联。
- `intent`：`comparison`（默认）或 `records`，说明读者需要比较还是逐条查询。显式 `layout` 优先。
- `key_column`：关键列的零基索引，默认 `0`。分组表每组最多三个字段列，其中一个为重复的关键列；输入字段仅登记一次，重复呈现另作标记。
- `column_widths`：与列数相同的正数权重，非像素。分组后在各组内重新归一化。
- `column_align`：与列数相同的 `left` / `right` / `center` 数组。省略时识别纯数值列并右对齐，关键列默认左对齐；复杂单位可以显式指定。
- `title` / `source`：可选表题与来源，保留在表格旁。

自动宽度计算是以 320px 视口为参考的启发式，不保证所有字体、放大比例都可读。较长的三列表也可能需要 `split`、调列宽或保留一列关键指标。检查换行和比较关系，不仅检查横向溢出。

可识别的数值单元格保持整组数字、单位不拆行，避免小数点与小数位分离。文字放大后表格确实放不下时，表格容器可横向滚动，整篇正文不横向溢出；记录该情况，不以“没有溢出”代替可读性判断。目标编辑器可能改写滚动样式，推送后仍需核验。

## 图片角色与可读性

`role` 可用 `auto`（默认）、`photo`、`screenshot`、`diagram`、`illustration`、`decorative`。只有明确为照片时使用 profile 圆角；截图和图解保留边缘。小图默认不超过可读取的原始宽度。`width_percent` 可设置 20–100，图片仍保比例。

图中文字已知时填写 `source_min_text_px`（原图最小字号），设计报告估算缩小后的字号。未填写就不能声称核实了图内文字可读性；没有 OCR。未知尺寸、远程图、EXIF 方向及图片压缩影响仍需浏览器与人工复核。非装饰图片应提供 `alt`；alt 不会自动变成可见图注。

## 可选互动

`reveal` 或 `chart` 增加 `"interactive":true` 后额外生成 `interactive.html`，`article.html` 仍保留完整静态信息。

- 揭秘固定 600×360 画布，上游换行规则允许提示 3 行、答案 5 行；放不下报错，不截断。
- 互动柱形图 2–5 项、短标题/标签、非负数；与静态版 2–12 项不同，超界需换组件。
- 原生名片、视频、真实高度展开、复杂横滑需到目标平台实际操作，不能伪造原生能力。

## 检查范围

生成器逐一精确比较解析后输入的文字/数据字段与静态 HTML 对应字段，包括代码中的缩进、空格与换行；Markdown 导入时的软换行合并与元信息提取单独记录。验证图片存在、列数、标签与文件哈希。不证明人工整理 JSON 前后原稿完全一致，不检验文章事实，不代表平台保留样式。人工调整结构仍须核对原稿数字、引文、章节、图片及顺序。

`design-review.json` / `review.html` 记录可计算的设计指标与需人工复核项；`preview.html` 使用 `reading-preview.html` 进行真实宽度、文字放大和额外间距检查。两个预览文件及审查页均不用于发布；发布使用无测试脚本的 `article.html` 或 `body.html`。

生成后手改 HTML 会导致 `audit` 报哈希变更。推荐改 JSON/profile 再生成；手改时保留差异并重新验收，不能沿用旧报告。
