# ai-ggbond 技能同步到 GitHub 仓库

将本地 `~/.hermes/skills/` 下的所有 ai-ggbond-* 技能同步到 GitHub 仓库 `BetterZflyee/ai-ggbond-skills`。

## 前置条件

- GitHub CLI (`gh`) 或 HTTPS clone 能力
- SSH 不可用（Hermes VM 环境限制），必须走 HTTPS

## 同步脚本

```bash
# 1. 克隆仓库（HTTPS 方式）
cd /tmp && rm -rf ai-ggbond-skills
git clone https://github.com/BetterZflyee/ai-ggbond-skills.git

# 2. 清除旧技能
cd /tmp/ai-ggbond-skills
rm -rf skills/ai-ggbond-*

# 3. 从本地各子目录复制全部 ai-ggbond 技能
cp -r /Users/admin/.hermes/skills/ai-ggbond-x-followings-feed skills/
cp -r /Users/admin/.hermes/skills/creative/ai-ggbond-article-writer skills/
cp -r /Users/admin/.hermes/skills/creative/ai-ggbond-github-trending skills/
cp -r /Users/admin/.hermes/skills/creative/ai-ggbond-sticker-writer skills/
cp -r /Users/admin/.hermes/skills/productivity/ai-ggbond-brain-setup skills/
cp -r /Users/admin/.hermes/skills/productivity/ai-ggbond-post-to-wechat skills/
cp -r /Users/admin/.hermes/skills/social-media/ai-ggbond-publish-to-x skills/
cp -r /Users/admin/.hermes/skills/social-media/ai-ggbond-run-xiaohongshu skills/

# 4. 验证
ls skills/

# 5. 提交推送
git add -A
git commit -m "sync: 更新全部 ai-ggbond 技能"
git push
```

## 技能分布一览

| 技能 | 本地路径 |
|------|---------|
| ai-ggbond-x-followings-feed | `~/.hermes/skills/` (根) |
| ai-ggbond-article-writer | `~/.hermes/skills/creative/` |
| ai-ggbond-github-trending | `~/.hermes/skills/creative/` |
| ai-ggbond-sticker-writer | `~/.hermes/skills/creative/` |
| ai-ggbond-brain-setup | `~/.hermes/skills/productivity/` |
| ai-ggbond-post-to-wechat | `~/.hermes/skills/productivity/` |
| ai-ggbond-publish-to-x | `~/.hermes/skills/social-media/` |
| ai-ggbond-run-xiaohongshu | `~/.hermes/skills/social-media/` |

## Pitfalls

- **SSH 克隆会失败**（`Permission denied (publickey)`），必须用 HTTPS
- **本地技能分布在多个子目录**（creative/productivity/social-media），不是扁平结构
- 删除废弃技能后，仓库中对应的旧文件会被 Git 自动识别为删除
- 如果技能改名（如 push-to-x → publish-to-x），Git 会自动识别为重命名（R），保留历史
