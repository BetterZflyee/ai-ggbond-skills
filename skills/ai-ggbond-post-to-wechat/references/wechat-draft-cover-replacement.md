# 微信公众号草稿封面原地替换

## 适用场景

文章已经成功进入草稿箱，但封面比例、构图或文字有问题。目标是保留原草稿和正文，只替换封面，避免重新上传全部正文图片、生成重复草稿。

## 推荐链路

1. `GET /cgi-bin/token` 获取 access token。
2. `POST /cgi-bin/material/add_material?type=image` 上传新封面，获得新的永久素材 `media_id`。
3. `POST /cgi-bin/draft/get` 读取原草稿；保留标题、摘要、作者、正文及正文微信图片 URL。
4. 将原文章对象中的 `thumb_media_id` 替换为新封面素材 ID。
5. `POST /cgi-bin/draft/update`，参数：
   - `media_id`: 原草稿 ID
   - `index`: 0
   - `articles`: 更新后的文章对象
6. 再次 `POST /cgi-bin/draft/get` 回读，确认 `thumb_media_id` 等于新封面素材 ID。

## 更新字段白名单

提交 `draft/update` 时仅保留接口接受的字段，避免把查询响应中的只读字段原样回传：

- `article_type`
- `title`
- `author`
- `digest`
- `content`
- `content_source_url`
- `thumb_media_id`
- `need_open_comment`
- `only_fans_can_comment`

## 验证标准

只有同时满足以下条件，才可宣告替换成功：

- `draft/update` 返回 `errcode: 0`；
- 回读草稿成功；
- 回读的 `thumb_media_id` 与新封面素材 ID 完全相同；
- 原草稿 `media_id` 保持不变。

## 网络

动态 IP 环境可通过 Tailscale 内网 tinyproxy：

```bash
export http_proxy=http://100.117.255.36:8888
export https_proxy=http://100.117.255.36:8888
```

使用 Tailscale IP，不使用 VPS 公网 IP 访问代理，避免 hairpin/NAT 问题。

## 安全

凭证从环境文件加载，日志只输出“是否存在/长度”，不得打印 AppSecret。更新草稿时不要把凭证硬编码进可长期保留的脚本。
