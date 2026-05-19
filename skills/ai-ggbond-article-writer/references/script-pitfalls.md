# 脚本踩坑记录 / Script Pitfalls

## article_manager.py 路径硬编码问题

**问题**：`article_manager.py` 第33行硬编码了 Windows 路径 `F:\\AI Workstation\\AI\\Super_OPC\\SuperIp\\Article/` 作为日志文件路径。在 macOS/Linux 上运行会报 `FileNotFoundError`。

**报错信息**：
```
FileNotFoundError: [Errno 2] No such file or directory: '/Users/admin/.hermes/skills/creative/ai-ggbond-article-writer/F:\\AI Workstation\\AI\\Super_OPC\\SuperIp\\Article/article_manager.log'
```

**临时解决**：跳过 article_manager.py，手动创建文件夹结构：
```bash
mkdir -p /path/to/Article/YYYYMMDDHHMM-文章标题/images
```

**预期文件夹结构**：
```
Article/
└── YYYYMMDDHHMM-文章标题/
    ├── YYYYMMDDHHMM-文章标题.md      # Markdown原文
    ├── YYYYMMDDHHMM-文章标题.html     # HTML排版版本（后生成）
    └── images/                        # 图片文件夹
        ├── cover.png                  # 封面图（2.35:1）
        ├── infographic.png            # 信息图（16:9）
        └── 02-xxx.png                 # 章节配图
```

**根本修复**：需要将 article_manager.py 中的硬编码路径改为基于参数或当前目录的动态路径。待修复。

## generate_images_v4.py 依赖问题

V4版本脚本依赖 `yunwu.ai` API 和 `YUNWU_API_KEY` 环境变量。如果未配置：
- 脚本会自动尝试3个API节点（主站、国内服务器、CF站）
- 都失败则报错，需检查 API Key 和账户额度

**macOS 注意**：Python 3.9 + LibreSSL 2.8.3 会抛 `NotOpenSSLWarning`，不影响功能但会在 stderr 输出警告。
