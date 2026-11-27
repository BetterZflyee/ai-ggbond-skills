# agd｜交互动画 HTML 演示

**版本：2.3.1**。只给主题，自主完成场景因果衔接、镜头光影、极简交互和声音匹配，交付可离线打开的独立 HTML 与可编辑工程。

[技能指令](SKILL.md) · [制作与验收标准](references/production-and-acceptance.md) · [下载 2.3.1 技能包](https://github.com/BetterZflyee/ai-ggbond-skills/releases/tag/agd-html-presentation-v2.3.1)

## 默认标准

- 内容按场景因果递进，主体、空间与观察尺度随解释任务变化。
- 平滑镜头、真实材质与光照，双场实时渲染并连续交接。
- 鼠标探索和内容对象直接操作；页面保留主题内容，默认无箭头、教程、HUD 或播放器。
- 声景、动作音和转场音共享画面状态。首次点击或有效按键启用声音，M 静音/恢复。
- 交付带版本的单文件 HTML、工程、来源/素材账本、预览、同源试听和验收记录。

## 安装与使用

将本目录完整放入支持 Agent Skills 的宿主技能目录。例如，在已克隆本仓库的根目录执行：

```bash
mkdir -p ~/.codex/skills
ln -s "$PWD/skills/agd-html-presentation" ~/.codex/skills/agd-html-presentation
```

已有同名入口时保留它，按本机安装方式更新。之后调用技能并给主题即可：

> 使用 agd-html-presentation，以“一滴水如何进入城市”为主题，完整生成一版。

模型自行完成研究、导演卡、素材与声音生成、代码实现、真实操作验收和交付。生成规模、场景数量与视觉语言按主题决定。

## 代码起点与依赖

初始化与构建只需 Python 3 标准库。成品浏览器需支持 WebGL2 和 WebAudio；起点自带程序视觉和可配置声音模块。

```bash
python3 scripts/deck.py init --topic "主题" --project /path/to/project
python3 scripts/deck.py build --project /path/to/project --output /path/to/project/presentation-V1.0.html
```

起点展示海面/矿物世界与接口。正式作品按主题重新设计场景、镜头、素材、声音和交互。工程中的 `interactive-audio.js` 可编辑，构建时重新内联入 HTML；成品运行无需网络下载该文件。

自动验收另需 Node.js、Playwright 和 Google Chrome。脚本以 `channel: 'chrome'` 运行，可用 `--playwright-module` 指定已有 Playwright 模块。

```bash
node scripts/verify-interactive.cjs /path/to/project/presentation-V1.0.html \
  --out /path/to/new-verification --starter \
  --playwright-module /path/to/node_modules/playwright
```

`--starter`用于起点烟测。正式作品需提供自己的 `--interaction-script` 和 `--audio-check-script`，按[接口说明](references/interactive-api.md)核对真实内容和声音；缺少证据记为 partial。用户明确静音时可记录 `--silent-reason`。

## 本版验证

默认起点通过49项独立浏览器检查，覆盖真实拖动、声音实际输出、M静音恢复、场景与参数响应、快速改向、同源离线PCM、后台处理、窄屏和错误日志；另通过7项构建契约检查。运行检查与正式作品的内容、连续画面审看、主观听审分别记录。
