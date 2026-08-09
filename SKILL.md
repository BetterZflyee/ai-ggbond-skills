---
name: ai-ggbond-video-analysis
description: 视频全链路解析 — 关键帧抽取 + 语音转写 + 结构化报告生成。当用户说"分析这个视频""解析视频""视频关键帧""视频转文字""视频报告""帮我看看这个视频"时使用。支持本地文件（.mp4/.mov/.mkv 等）和 URL。自动处理视频损坏修复、音频转写、画面帧提取、Markdown 报告生成。
---

# 视频分析 Skill

对视频进行全链路解析：提取关键帧 → 语音转写 → 生成结构化 Markdown 报告。

## 前置依赖

- `ffmpeg` / `ffprobe` — 视频处理
- `curl` — API 调用（Python `urllib` 在 SF 环境有 SSL 兼容问题）
- `watch` skill — 画面帧提取
- SF 内网环境 — 语音转写 API 仅限 SF 内网访问

## 工作流程

### 第一步：视频预处理

先检查视频是否可正常解码：

```bash
ffprobe -v error -show_entries format=duration,bit_rate -of csv=p=0 "<video_path>"
```

如果报错或时长异常，说明视频可能损坏。常见问题是 **HEVC 编码损坏**（微信传输大视频高发），用以下命令修复：

```bash
ffmpeg -err_detect ignore_err -max_error_rate 0.99 \
  -i "<video_path>" \
  -t <可解码时长> -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  "<fixed_path>.mp4" -y
```

### 第二步：画面帧提取

使用 `watch` skill 提取关键帧：

```bash
# 启动 watch skill，传入视频路径
# 参数：--detail balanced（推荐，最多 100 帧）或 token-burner（不设上限）
# 如果视频较长（>10min），建议 --detail efficient（最多 50 帧）
```

**重要**：watch 脚本内部会调用 `SKILL_DIR/scripts/watch.py`。如果视频之前已修复，传给 watch 修复后的文件。

### 第三步：音频提取

从视频中提取音频并压缩：

```bash
ffmpeg -i "<video_path>" -vn -ac 1 -ar 16000 -b:a 32k "<audio_path>.mp3" -y
```

参数说明：
- `-ac 1`：单声道（减小文件）
- `-ar 16000`：16kHz 采样率（ASR 最优）
- `-b:a 32k`：32kbps 码率（平衡体积与质量）

### 第四步：语音转写

使用本 skill 捆绑的 `scripts/transcribe.py`：

```bash
python3 <skill_dir>/scripts/transcribe.py <audio.mp3> <output.json>
```

**技术细节**（遇到问题时参考）：
- API 地址：`https://llm-model-hub-apis.sf-express.com/v1/audio/transcriptions`
- 模型：`aliyun/qwen3-asr-flash-filetrans`
- 认证：JWT Bearer Token（从 `~/.claude/settings.json` 的 `ANTHROPIC_AUTH_TOKEN` 自动读取）
- 输入格式：`data:audio/mp3;base64,<base64>` 放入 `file_url` 参数
- 限制：每个分片 base64 不超过 61,440 字符（约 10 秒音频），脚本自动分片
- 频率限制：遇到 429 自动等待重试
- 任务模式：创建任务 → 轮询状态 → 下载结果

### 第五步：生成报告

结合画面帧和转写文本，生成结构化 Markdown 报告。报告模板：

```markdown
# 视频分析报告：[主题]

> **来源**：[文件路径或 URL]
> **时长**：XX 分 XX 秒
> **分辨率**：W×H
> **分析日期**：YYYY-MM-DD

## 一、视频概述

[2-3 句话概括视频内容和场景]

## 二、核心观点（按时间线）

| 时间 | 观点 | 关键内容 |
|------|------|----------|
| MM:SS | [一句话概括] | [具体内容] |

## 三、关键画面帧

挑选 8-12 张代表性帧，按主题分组展示，每张标注时间戳和说明。

## 四、完整转写文本

按时间线排列所有转写句子。

## 五、涉及的系统/模块/概念

表格列出视频中提到的关键系统、模块、概念及简要说明。

## 六、技术备注

记录视频处理过程中的技术细节（损坏修复、转写覆盖率等）。
```

### 报告保存位置

根据项目目录结构约定，保存到当天日期文件夹下：

```
08-日记与迭代/YYYY/MM/YYYY-MM-DD/YYYY-MM-DD-<主题>.md
```

## 错误处理

| 问题 | 原因 | 解决 |
|------|------|------|
| 视频无法解码 | HEVC 损坏 | 用 ffmpeg 重编码为 H.264 |
| 转写 502 | HTTP 端点不可用 | 改用 HTTPS 端点 |
| 转写 SSL 错误 | Python urllib SSL 兼容问题 | 脚本已改用 curl |
| 转写 429 | API 频率限制 | 脚本内置重试等待 |
| 转写 FILE_404 | file_url 被当成 URL 而非 base64 | 使用 `data:audio/mp3;base64,...` 格式 |
| 请求体过大 | base64 超过 6MB | 压缩音频到 32kbps 以下 |
| 参数过长 | file_url 值超过 61KB | 分片为 ~10 秒每片 |

## 注意事项

1. **不要用 Python urllib 调 API** — SF 环境有 SSL 兼容问题，统一用 curl
2. **不要用 HTTP 端点** — `llm-model-hub-apis` 的 HTTP 端点经常 502，用 HTTPS
3. **不要传裸 base64 到 file_url** — 必须用 `data:audio/mp3;base64,...` 格式
4. **音频先压缩再转写** — 32kbps MP3 单声道 16kHz 是最优参数
5. **视频损坏先修复** — 微信传输的视频常有 HEVC 损坏，先重编码再处理