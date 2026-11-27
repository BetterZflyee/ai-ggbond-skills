# 鼠标驱动起点与验收接口

默认 `deck.py init` 创建 `presentation.html`、`interactive-audio.js` 和 `project.json`。HTML已内嵌声音模块，可直接离线打开；`build`从可编辑音频文件更新内嵌脚本，输出带版本的独立交付文件。旧版无`audioRuntime`配置的工程仍按原方式构建。默认示例验证两种程序材质、光照、镜头、过渡及状态声景，正式作品按主题重做。

## 状态组织

- `beat / targetBeat`：当前已落定的节拍与用户想前往的节拍。
- `journey`：由当前位置进入下一目标的有限过渡；快速改方向从当前状态重起，不跳回预设起点。
- `environmentTime`：海浪、雾或颗粒等环境时钟，不决定用户什么时候换场。
- `orbit / light / owner`：可探索输入和控制归属；松手后保留当前观察。

示例将前后世界分别绘入离屏纹理，用具有折射、边缘高光的水膜接住交接。这属于内部渲染。页面保留主题内容、镜头与光源的直接操作；正常画面没有导航控件、操作提示或数值HUD。

## 协议

```js
window.__presentation = {
  get ready() { return ready; },
  next() {}, previous() {},
  goTo(index, {immediate=false}={}) {},
  getState() {
    return {ready, error, beat, targetBeat, beatCount,
      moving, transition, environmentTime,
      orbit, light, cameraOwner, lightOwner, glError, audio};
  }
};
```

`transition`为当前有限过渡的0–1进度；停留时为1。`goTo`从任意当前状态平滑进入目标，`immediate`用于确定性审看或低动态模式。ready在首个有效画面完成后置true。发生错误时界面显示原因，接口ready为false；初始化不能依赖声音解锁。

协议是验收所需的内部能力，不要求为每个方法增加产品按钮。

## 默认状态声景

默认起点通过`AGDInteractiveAudio.create({scenes, controls})`建立声景，保留手动探索与停留。材质示例中的海面和矿物地形有不同音色；水膜的画面与声音共用`blend`，太阳拖动通过`light`改变实际滤波。正式作品为自己的空间、材料与动作编写配置，保留状态接口；不把示例海面或本轮顺丰七场复制成所有主题。

首次真实`pointerdown`或有效`keydown`调用声音解锁；初始化ready不等待音频许可。滚轮可推进画面，冷启动的滚轮本身未必取得音频播放许可。M键控制静音，页面不增加播放器、常驻控件或解锁提示。

```js
const sound = AGDInteractiveAudio.create({
  scenes: [{id:'room', tones:[110,165], toneGain:.035,
    noiseGain:.03, cutoff:2200, beatSound:'paper', transitionSound:'air'}],
  controls: [{scene:'room', input:'pressure', target:'cutoff', min:700, max:4200}]
});
sound.update({scene:'room', nextScene:null, blend:0, targetScene:'room',
  beat:2, motionId:7, motionProgress:.3, motionDuration:1.4,
  crossScene:false, reverse:false, input:{pressure:.6}});
// 用实际画面接触阈值触发；在音源内部峰值偏移前排音，避免每帧重复触发。
sound.trigger('paper', {gain:.15, pan:0, motionId:7});
```

`scenes`可配置和弦频率、持续层电平、噪声、滤波与声像；`controls.target`支持`cutoff / noiseGain / pitch / pan`。音色生成器包含`paper / tape / scan / clack / knock / servo / glass / particle / pulse / air / impact / latch`，正式作品按材料选用或扩展。`nextScene + blend`使用等功率权重；也可传`weights`数组。`targetScene`用于选择正向或反向运动的目标材质音，`motionId`对一次有限运动只排一次音。新运动会淡出旧瞬态，未解锁前只保存当前状态；有效解锁后排入仍未结束的当前运动。

适配器还提供`unlock / setMuted / setActive / getState / renderOffline / dispose`。`getState()`暴露`contextState / unlocked / active / muted / scene / sceneWeights / input / parameters / liveRms / livePeak / activeTransientCount / soundEvents`；分析器位于主音量之后。默认HTML把`unlockAudio / setMuted / renderAudioOffline`附在内部`__presentation`接口，`getState().audio`提供音频状态。正常产品不展示这些调试字段。

`renderOffline({scene, input, seconds, sampleRate, events:[{kind,at,gain}], muted})`返回`{channels:[Float32Array,Float32Array],sampleRate,duration,sameSourceGraph:true}`，复用实际PCM工厂与混音图。离线导出不会改变实播事件计数。它用于信号核验与试听素材，不是实播的逐采样录制。

适配器接收当前场景、节拍、局部姿态、过渡进度/时长/方向和交互参数。场景持续层在停留时保留；接触、扫描等短音由作者在实际阈值越过时调用`trigger`并去重。返回或跳转不重放途中全部事件。环境、动作、转场三总线汇入高通、压缩、主音量与后置分析器，后台状态让主输出平滑降至精确零。

音频验收接口应能观测当前声景、过渡、活跃声音与主音量之后的实际输出。真实浏览器中完成解锁、非静音、静音近零和恢复检查；并验证改变参数确实影响声景、画面与声音在同一转场时长内交接。详细素材与混音方法见[声景与材质化过渡](sound-and-transitions.md)。

## 示例操作

- 拖动画面：改变观察方向与相机角度，释放后保留。
- 直接命中画面里的太阳并拖动：改变真实光照高度，影响水面反射或石材受光，释放后保留。太阳位置由与着色器相同的相机与光照公式投影，未另加按钮或标签。
- 短点画面、右键、滚轮或方向键：改变节拍目标，平滑转场；页面不展示操作教学。
- 镜头、内容拖动与短点推进分别拥有手势，拖动后松手不触发推进。

低动态模式保留镜头和内容操作，缩短节拍转场并停住环境动态。

## 检查

```bash
node <skill-dir>/scripts/verify-interactive.cjs <HTML> --out <新的验收目录> \
  --interaction-script <工程/interaction-check.cjs> \
  --audio-check-script <工程/audio-check.cjs>
```

默认起点可使用`--starter`；验证完整路径、返回、中间状态、真实镜头和画面内太阳拖动、释放后状态、短点/右键/滚轮和键盘、窄屏、无提示UI、错误日志。为隔离光照与镜头带来的画面变化，示例验收在低动态页中停住环境后真实拖动，既检查参数变化，也检查实际像素变化。

自定义内容和声音脚本均导出 `async function(page)` 或 `{check: async(page)=>...}`，返回`{passed:true,details}`。内容检查断言实际状态和手势归属，声音检查覆盖真实手势后的后置主输出、静音恢复、场景/动作/参数匹配。缺少任一检查时记partial并退出2；失败退出1；完整运行检查通过退出0。用户明确要求静音的作品，可用`--silent-reason '用户明确要求静音'`替代声音脚本，并保留需求记录。

`--starter`仅验证代码起点的运行与示例操作，不证明正式作品的内容因果、视觉审看或主观听审。按[制作与验收标准](production-and-acceptance.md)分别记录这些检查。

相关入口：[SKILL.md](../SKILL.md)、[动作配方](motion-recipes.md)。
