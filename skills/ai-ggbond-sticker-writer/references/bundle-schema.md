# 贴图计划与交付格式

`scripts/sticker_pack.py` 使用 Python 3.10+ 标准库，图片尺寸读取复用同级公众号精排模块。不会联网或生成图片。

```json
{
  "schema_version": 1,
  "scene": "newspic",
  "meta": {"title": "已选标题", "author": "AI朱朱侠", "caption_budget": 500},
  "caption": "可直接粘贴的第一段。\n\n第二段。",
  "tags": ["公众号", "内容创作", "图文"],
  "expected_image_count": 1,
  "style": {"description": "深蓝底色、明亮正文、少量技术蓝，清晰网格"},
  "sources": [{"id": "source1", "title": "用户提供材料", "status": "provided"}],
  "images": [{
    "id": "cover", "role": "cover", "heading": "精确上图标题",
    "text": ["第一条准确文字", "第二条准确文字"],
    "ratio": "16:9", "layout": "标题在上，核心信息按阅读顺序排列",
    "asset": "images/01-cover.png", "alt": "图片辅助描述",
    "source_ids": ["source1"]
  }]
}
```

`scene` 可为 `newspic`、`article-cards`、`long-image`。`images` 数组顺序就是阅读和上传顺序；ID 唯一。原生贴图封面页排第一，明确张数必须和数组长度一致，不自动截取。`role` 支持 cover/overview/steps/comparison/timeline/data/person/concept/quote/summary/case。

`caption` 为纯文本，`tags` 不含 `#`。`source_ids` 必须能对应来源表；来源表记录可追溯性，不代表脚本核实了事实。`prompt` 可选，提供时原样保存；否则按布局、视觉描述和精确文字生成中文 prompt。正文标签不能放入图片文字。

`asset` 省略时保留待生成状态；存在时必须指向本地 PNG/JPEG/GIF/WebP，原文件按字节复制。可以填写真实 `source_min_text_px`，未知时省略。已实际核对图片时填：

```json
{"review":{"status":"passed","method":"visual","sha256":"当前图片的64位SHA-256","notes":"实际核对的内容与范围"}}
```

method 为 `visual` 或 `ocr+visual`，哈希不同则检查失效。不能为消除提示填造结果。没有高优先级问题且全部图片已核对才标记 `ready_for_handoff`；它仍不等于平台验收或发布授权。

## 长文复用

可增加 `article_reuse`：

```json
{
  "article_reuse": {
    "meta": {"title": "长文标题", "summary": "摘要"},
    "cover_image_id": "cover",
    "blocks": [
      {"type": "paragraph", "text": "用户确认的完整正文。"},
      {"type": "steps", "items": [{"title":"第一步","text":"保留准确说明。"}]},
      {"type": "image", "image_id": "detail", "role": "diagram"}
    ]
  }
}
```

`detail` 应对应真实图片 ID。除图像引用外，blocks 原样交精排模块处理，支持原有表格、时间线、问答等组件；不自动缩短长文。封面不可隐式重复进正文。素材齐备时生成 `layout-input.json`，缺图则只生成待完成计划。

## 产物

- `caption.txt`：纯文本正文，和交接包 content 完全一致。
- `content.md`、`source.json`、`plan.json`、`sources.json`：编辑及来源记录。
- `prompts/`：每张图独立 prompt；`assets/`：顺序明确的图片副本。
- `preview.html` / `post-preview.html`：真实宽度、顺序翻图的本地模拟，不上传。
- `design-review.json`：字符统计、尺寸、比例、图内字号、核对状态。
- `newspic-bundle.json`：原生贴图的纯文本＋图片列表，只在 newspic 场景输出。
- `layout-input.json`：可选长文输入；`manifest.json`：交付文件哈希。

不覆盖已有目录；使用新版本目录构建，方便对照和恢复。手改产物会被 `audit` 检出，建议修改计划后重新构建。
