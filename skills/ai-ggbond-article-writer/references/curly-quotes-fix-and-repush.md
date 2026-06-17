# 特殊引号修复与重推流程（2026-06-08 实战）

## 问题

文章中出现日文/繁体中文引号 `「」`，在微信编辑器中显示不正常。

## 修复

```bash
cd 文章目录
sed -i '' 's/「/"/g; s/」/"/g' 文章.md
```

修复后必须重新推送到微信草稿箱。

## 重推流程

```bash
# 写推送脚本
cat > /tmp/push_wechat.sh << 'EOF'
#!/bin/bash
export WECHAT_APP_ID=wx...
export WECHAT_APP_SECRET=...
cd /path/to/wechat-api/scripts
export http_proxy=http://100.117.255.36:8888
export https_proxy=http://100.117.255.36:8888
npx -y bun wechat-api.ts "文章.md" --theme default --color blue --title "标题" --summary "摘要" --author "AI朱朱侠" --cover "封面.jpg"
EOF

# 后台运行（多图长文需要 10+ 分钟）
bash /tmp/push_wechat.sh
```

## 注意事项

- 每次重推都会重新上传所有图片
- 多图长文不要杀进程，等系统通知
- ECONNRESET = 图片太大，需要压缩到 <500KB
