# SuperIp 内容资产路径规范

## 背景

飞哥希望将内容资产统一收敛到 `/Users/admin/SuperIp` 下管理，避免文章、贴图、图片散落在当前目录、`/tmp`、Windows 旧路径或旧大小写目录中。

## 当前标准路径

| 内容类型 | 默认路径 |
|---|---|
| 公众号文章 | `/Users/admin/SuperIp/article` |
| 微信贴图 | `/Users/admin/SuperIp/stickers` |

## 公众号文章目录结构

```text
/Users/admin/SuperIp/article/
└── YYYYMMDDHHMM-文章标题/
    ├── YYYYMMDDHHMM-文章标题.md
    ├── YYYYMMDDHHMM-文章标题.html
    ├── _briefs/
    ├── _knowledge_base/
    └── images/
        ├── cover.png
        ├── infographic.png
        └── 02-xxx.png
```

## 操作要求

1. 写作前先创建正式目录，后续文章、HTML、图片、brief、知识库都放在同一目录内。
2. `article_manager.py` 如仍有 Windows 路径问题，不要退回 `/tmp/article-*`；应手动创建 `/Users/admin/SuperIp/article/YYYYMMDDHHMM-标题/`。
3. 回复用户时给出最终落盘路径，便于继续发布到公众号。
4. 贴图技能已同步默认输出到 `/Users/admin/SuperIp/stickers`，文章技能不要与贴图目录混用。
