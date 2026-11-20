# 公众号贴图与精排工作流

贴图 v3 与精排 v2.1 使用同一份事实、文字和图片记录，按阅读场景分别交付。当前默认视觉为商业杂志编辑风；用户指定的品牌、参考图与模型优先。

| 场景 | 技能与产物 |
|---|---|
| 原生公众号贴图 | `ai-ggbond-sticker-writer` → 纯文本、图片页序、`newspic-bundle.json` |
| 公众号长文章 | `ai-ggbond-article-writer` → `ai-ggbond-wechat-layout` → `article.html` 与 `handoff.json` |
| 贴图复用于长文 | 贴图计划中的 `article_reuse` → `layout-input.json` → 精排 HTML |
| 完整长图 | `ai-ggbond-long-image-generator` 的预设、分段与接缝方法；实际生成及最终图片另行验收 |

## 本地开始

在仓库根目录执行，输出目录需要尚不存在：

```bash
python3 skills/ai-ggbond-sticker-writer/scripts/sticker_pack.py build \
  --input skills/ai-ggbond-sticker-writer/assets/demo/plan.json \
  --out /tmp/wechat-sticker-demo-v1
python3 skills/ai-ggbond-sticker-writer/scripts/sticker_pack.py audit \
  /tmp/wechat-sticker-demo-v1
```

演示计划不含成图，会如实显示待生成。构建器离线生成正文、逐页提示词、来源记录、真实宽度预览和交接文件，不调用生图服务或微信账号。用自己的图片填充计划并完成实际核对后，重新构建新版本目录。

已生成完整原生交接包时，安装发布器原有依赖后进行本地预检：

```bash
bun skills/ai-ggbond-post-to-wechat/scripts/wechat-api.ts \
  /path/to/delivery/newspic-bundle.json --type newspic --dry-run
```

原生内容保留纯文本，第一张图承担封面，图片按计划顺序上传。内容/图片改变会使原哈希核对失效；未核对或中途上传失败时停止创建草稿。只有已获对应授权才进行外部草稿操作，本地预检不代表已经发布。

## 安装与维护

已有对应写作、长图和发布技能的环境，可用贴图的 [本地安装器](../skills/ai-ggbond-sticker-writer/references/local-maintenance.md) 更新两个模块和衔接入口。默认只展示计划；检查后按已有授权执行 `--apply`。未知发布器版本停止覆盖，先合并补丁。旧合集入口只有匹配已知旧版哈希时才存档；当前版本的源码入口保持可用。

```bash
python3 skills/ai-ggbond-sticker-writer/scripts/install_local.py \
  --home "$HOME" \
  --layout-source skills/ai-ggbond-wechat-layout \
  --backup-dir /path/to/private-backups
```

模型、账号凭据和网关配置不由安装器修改。维护备份、个人稿件与真实账号验证记录应留在本地，不提交到源码仓库。

## 验证

```bash
python3 -m unittest discover -s skills/ai-ggbond-sticker-writer/tests -p 'test_*.py'
python3 -m unittest discover -s skills/ai-ggbond-wechat-layout/tests -p 'test_*.py'
bun test skills/ai-ggbond-sticker-writer/tests/newspic-bundle.test.ts
```

Python 的旧生图兼容测试需要 requests/Pillow，但使用模拟配置与网络，不发起收费请求。发布器适配测试模拟上传回调。图片、浏览器、草稿读回和手机微信是不同验收层级；本次源码同步不包含真实生图、微信写入或真机验收结论。

精排中复用的两个上游 SVG 文件及 MIT 许可、版权署名位于 [vendor](../skills/ai-ggbond-wechat-layout/vendor/)，来源与固定版本见 [上游说明](../skills/ai-ggbond-wechat-layout/references/upstream.md)。
