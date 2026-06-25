# 独立工具包模式

## 何时使用
当 agent 无法直接完成任务（如 API Key 无法通过工具传递）时，创建独立工具包让用户在终端手动运行。

## 工具包结构

```
/tmp/<toolkit_name>/
├── setup.sh           # 一键配置脚本
├── test.py            # 验证脚本
├── generate.py        # 主功能脚本
└── README.md          # 使用说明
```

## 打包与交付

```bash
# 打包
cd /tmp && tar -czf toolkit.tar.gz setup.sh test.py generate.py README.md

# 通过飞书发送
send_message(target='feishu:oc_xxx', message='MEDIA:/tmp/toolkit.tar.gz')
```

## 关键原则

1. **脚本自包含**：不依赖 agent 环境，用户直接 python3 运行
2. **配置从文件读**：从 config.yaml 读取，不硬编码
3. **错误信息清晰**：明确告诉用户需要做什么
4. **提供验证步骤**：test.py 必须在 generate.py 之前运行
