# AI GGBond Skills

个人 Claude Code / Trae Skills 集合，用于提升日常工作效率。

## 📁 仓库结构

```
ai-ggbond-skills/
├── skills/                          # 所有 Skills
│   ├── ai-super-individual-wechat-writer/    # 微信公众号写作 (原创)
│   ├── wechat-sticker-creator/               # 微信贴图生成 (原创)
│   ├── marketing-image-generator/            # 营销图片生成 (原创)
│   ├── baoyu-cover-image/                    # 封面图生成 (基于 baoyu 修改)
│   ├── baoyu-post-to-wechat/                 # 微信发布 (基于 baoyu 修改)
│   └── ...
├── third-party/                     # 第三方 Skill 来源记录
│   ├── baoyu-cover-image/ORIGIN.md
│   └── baoyu-post-to-wechat/ORIGIN.md
└── README.md
```

## 🚀 使用方式

### 本地开发

Skills 代码位于 `github/ai-ggbond-skills/skills/`，通过软链接同步到 `.trae/skills/` 使用：

```powershell
# 创建软链接 (以管理员身份运行 PowerShell)
New-Item -ItemType SymbolicLink -Path ".trae\skills\ai-super-individual-wechat-writer" -Target "github\ai-ggbond-skills\skills\ai-super-individual-wechat-writer"
```

### 版本管理

```bash
# 查看所有版本
git tag

# 回退到指定版本
git checkout <tag-name>

# 创建新版本
git add .
git commit -m "feat: xxx"
git tag v1.x.x
git push origin main --tags
```

## 📝 Skills 清单

### 原创 Skills

| Skill | 描述 | 状态 |
|-------|------|------|
| ai-super-individual-wechat-writer | 微信公众号文章写作 | ✅ 稳定 |
| wechat-sticker-creator | 微信贴图生成 | ✅ 稳定 |
| marketing-image-generator | 营销图片生成 | ✅ 稳定 |

### 基于第三方修改

| Skill | 原始来源 | 描述 |
|-------|----------|------|
| baoyu-cover-image | [baoyu-skills](https://github.com/jimliu/baoyu-skills) | 封面图生成 |
| baoyu-post-to-wechat | [baoyu-skills](https://github.com/jimliu/baoyu-skills) | 微信发布 |

## ⚙️ 配置

用户配置存储在 `~/.ai-ggbond-skills/`：

```
~/.ai-ggbond-skills/
├── .env                    # API keys
└── config.yaml             # 用户偏好
```

## 📌 注意事项

- 原创 Skills 完全自由修改
- 基于第三方的 Skills 修改后记录到 `third-party/<skill>/ORIGIN.md`

## 📄 License

MIT
