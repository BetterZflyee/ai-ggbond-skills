# Browser 模式踩坑（2026-05-27）

## 问题 1：贴图菜单找不到（2026-05-27 实测）

微信公众平台后台 UI 已改版。`wechat-browser.ts` 在登录后搜索「贴图」菜单项时，DOM 中只返回 `["更多"]`，找不到「贴图」入口。

**症状**：
```
[wechat-browser] Looking for "贴图" menu...
[wechat-browser] Menu items: {"count":1,"texts":["更多"]}
[wechat-browser] Menu position: null
Error: 贴图 menu not found or not visible
```

**影响**：Browser 模式推送贴图 (newspic) 完全不可用。

**当前替代方案**：
1. 用户手动在微信公众号后台操作
2. 等待脚本适配新版 UI

## 问题 2：agent-browser 依赖未安装（2026-05-27 实测）

`wechat-agent-browser.ts` 依赖 `agent-browser` 可执行文件，当前环境未安装：
```
Error: agent-browser failed to start: Executable not found in $PATH: "agent-browser"
```

## 问题 3：API 模式贴图 45166（持续）

`--type newspic` 在 API 模式下经常触发 45166 content hint 错误。

**现象**：正文图片上传成功，封面也上传成功，但草稿创建阶段报 `45166: invalid content hint`。

**当前结论**：API 模式推送贴图不可靠，等待修复。

## 问题 4：ECONNRESET 图片上传断连（持续）

图片 >500KB 时微信 API 触发 ECONNRESET。必须预压缩到 <500KB（推荐 50-200KB JPEG quality=75）。

## 问题 5：文件选择器失效

**症状**：`wechat-browser.ts` 成功登录、找到"贴图"菜单、进入编辑器，但报 `File input not found with any selector`。

## 问题 6：baoyu-chrome-cdp 依赖缺失

```bash
cd scripts && npx -y bun install baoyu-chrome-cdp
```

## 问题 7：macOS `python` vs `python3`

macOS 默认无 `python` 命令，必须使用 `python3`。
