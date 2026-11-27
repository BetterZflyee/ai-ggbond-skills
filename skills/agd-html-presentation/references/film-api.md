# 定时音画模式与验收接口

显式 `deck.py init --engine cinematic` 创建 `film.html` 与 `project.json`。film.html 内含可编辑的 GLSL、声音合成与时间控制，`build` 按版本生成独立 HTML。示范的世界和32秒时间线是素材实验；正式演示按主题重新设计。

此音画起点通过两个阶段组织画面：各自计算两个完整世界到离屏纹理，再用材质化过渡合成到屏幕。世界表面、镜头、太阳、雾和声音读取同一时间。HTML不依赖外部媒体文件。

此模式用于用户明确需要定时播放或音画演示的任务。默认鼠标驱动演示使用[交互接口](interactive-api.md)，不要求播放、暂停和音频接口。

## 本模式的协议

使用 `window.__film` 或 `window.__lab` 暴露下列接口：

```js
window.__film = {
  ready: true,
  duration: 32,                        // 秒；正式作品可自定
  seek(seconds) {},                   // 暂停并确定性计算、绘制
  play() {}, pause() {},
  getState() {                        // 可序列化的小对象
    return {time, playing, muted, viewMode, phase, transition};
  },
  renderAudioOffline(seconds, sampleRate) {
    return {channels:[leftPCM,rightPCM], sampleRate, duration};
  }
};
```

方法可同步或返回Promise。ready应在着色器、缓冲、必要素材全部可用后置为true；载入失败给可见反馈并记录错误。

seek时保持时间、随机种子和输入一致，避免因反复定位改变材质。需要时重置历史累积、粒子或模拟状态。播放与定位使用同一套光照、镜头和素材函数。

离线音频须复用实际音源和调度，返回 AudioBuffer 或 `{channels:[Float32Array,...],sampleRate,duration}`。保留峰值余量、声道、事件与静音状态；不要用独立测试正弦波代替成品音轨。

## 示例起点的内容交互

- 点击播放启用音频并启动统一时间线，拖动时间条可定位。
- “视图”按钮或 D 键在最终合成、法线、基础材质之间切换，用来观察中间素材。
- M 或声音按钮切换静音；空格暂停/播放，方向键按秒定位。
- `setViewMode(mode)`、`setMuted(bool)`供可重复验收调用；实际交互检查仍通过真实输入。

示范观察模式不是正式演示必须保留的UI。根据主题选择对观众有意义的内容操作，并在debug状态中暴露相应参数。

## 验收器覆盖什么

```bash
node <skill-dir>/scripts/verify-film.cjs <HTML> --out <新的目录> \
  --interaction-script <工程/interaction-check.cjs>
```

脚本读取已有 Playwright/Chrome，检查 WebGL2、时间定位、多时刻画面、页面错误、内容交互、离线音频与窄屏溢出，并实际启动播放。缺少Playwright可传 `--playwright-module <模块入口>`，也可用等价工具完成检查。

默认连续播放最多45秒，报告记录实际覆盖；`--play-seconds`可指定本次长度。较长作品还应完成一条完整叙事路径，不能把45秒抽检记作全片播放。

`interaction-check.cjs` 导出 `async function(page)`，返回 `{passed:true,details}`，真实操作材料/光源/相机/参数等，断言 getState/debug 中的变化。可同时验证播放、音频解锁与静音；仅有导航不算内容交互。

完整检查通过退出0，缺少交互验证记partial并退出2，失败退出1。离线采样验证非静音、有限数值、RMS和峰值；听感仍需实际听审。

## 从实验扩展为演示

把时间线拆成有语义的场景与节拍；每拍有起始、变化、落点、口播和来源。讲者推进改变段落目标，统一时钟继续推动环境与声景。提供返回、定位或总览，定义用户参数与编排轨迹的混合。

重计算优先预生成纹理/图集/体噪声；运行时更新相位、镜头、光和必要形变。给各类素材保存种子、通道、色彩空间和预算。见[程序素材配方](procedural-materials.md)、[声音与过渡配方](sound-and-transitions.md)。

视觉验收要确认材料和空间确实成立：法线模式与高光对应、光源移动改变受光、过渡中有真实的中间材料状态，最终画面可连续观看。这个协议只提供运行证据，完成度由作品本身决定。

相关入口：[SKILL.md](../SKILL.md)。
