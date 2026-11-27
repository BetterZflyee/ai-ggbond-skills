# 平面分支运行底座 API

`assets/runtime.js` 是显式 `flat` 分支的无依赖 Canvas 2D 底座，用于平面图解与调度验证。内建统一时间、节拍、输入归属、离屏合成和指定状态定位。默认交互音画起点见 [interactive-api.md](interactive-api.md)；三维作品也可沿用这里的时间契约并替换渲染层。

## 工程与单文件

`scripts/deck.py init --engine flat` 生成 `runtime.js`、`deck.js`、`shell.html`、`project.json`。编辑场景和网页壳后，`build` 合并为带内联 module 脚本的 HTML，可直接用浏览器打开。

`runtime.js` 导出 `createDeck` 与数学工具；`deck.js` 导出 `scenes` 数组。构建器只合并本地模块声明，保留 `export const/function/class` 的内容并移除导出标记，不解析第三方 import。需要依赖的作品先用合适的 bundler 打包依赖，再合并；构建器遇到 import 会明确停止。

构建目标已存在时停止，选择新的版本名；初始化不覆盖已有工程文件。网页壳中的 `__TITLE__ / __RUNTIME__ / __SCENES__` 是构建时插入点。

## 场景接口

```js
export const scenes = [{
  id: 'mechanism', title: '场景标题',
  beats: [{dur:3, delay:0, hold:4}, {dur:5, hold:5}],
  notes: ['第一拍口播与来源', '第二拍口播与来源'],
  enterWith: 'fade', transitionDuration: .9,
  create(ctx) {
    return {
      enter(state) {},
      update(state) {},
      render(canvas2d, state) {},
      pointer(kind, x, y, state) { return false; },
      resize(view) {}, exit(state) {}, dispose() {}
    };
  }
}];
```

所有生命周期同步执行。初始化前完成图片、字体、模型等异步加载，加载失败给可见反馈。

- 逻辑舞台为 1920×1080；显示画布保持比例并居中补边。`view.scale/offsetX/offsetY/cssWidth/cssHeight` 描述视口。
- `ctx` 提供 `width/height/view/mouse/canvas/screenCanvas/createCanvas/deck`；`canvas` 为场景离屏画布。
- 数学工具 `clamp/lerp/smoothstep/damp/easing` 可直接取用，也在 `ctx.helpers` 中。
- `ctx.random()` 按场景 ID 与 seed 重建。使用它或自行固定随机种子，避免定位截图随运行顺序变化。

## 状态与时间

`state.t` 是本次进入场景后的时间；返回拍数时继续增加。`state.dt/globalTime/beat/dir/enter/exit/view` 描述当前状态；`state.p` 与 `state.progress` 为同一个拍进度数组。

`at(beat)` 返回该拍已经完成的动画秒数，`since(beat)` 包含该拍起步后的延迟与停留。`k(beat,start,end,ease?)` 将拍内时间段映射到 0–1，默认 `inOutCubic`。可用缓动包括 `linear/inCubic/outCubic/inOutCubic/outQuart/outBack`。

当前拍正常推进，跨过的旧拍 3 倍补齐，后续拍 2.4 倍回落。帧时间上限 50ms，鼠标按帧率无关的指数平滑跟随。

底座读取减少动态效果偏好，可用 `options.reducedMotion` 覆盖。标记在 ctx/state 中可用：目标拍跳至终态、未来拍归零，转场改为短淡入；场景自行据此关闭漂移、呼吸等非必要循环，并为参数交接提供即时模式。窄屏网页壳把图形放在上方，当前标题和讲者文字作为可读的 DOM 内容显示在下方。

`mouse.x/y` 为平滑后的 [-1,1] 坐标，Y 向上；`tx/ty` 为目标。`px/py` 为即时设计坐标，Y 向下；另有 `down/inside`。

## 输入所有权

`pointer('down',x,y,state)` 返回 true 时，场景接管本次手势。运行时捕获指针并阻止松手翻页。`move/up/cancel` 仍送给场景；在 `up/cancel` 清除自己的拖动状态。

底座处理方向键、空格、PageUp/Down、Home/End、A 自动播放，以及画布点击、水平滑动、右键返回。表单输入与按键连发不会触发翻页。网页壳负责备注、总览、全屏与黑屏；需要音频时扩展首次手势钩子与静音 UI。

交互数据属于场景。例如用 `get debug(){return {value,dragging,userWeight};}` 暴露可验证状态；浏览器脚本经 `window.__deck.instance.debug` 断言参数变化。

## 连贯转场

可使用 `fade/zoom/slide`，也可在场景 `transition`、实例 `transition`、`enterWith` 函数或初始化 `transitions[name]` 中提供自定义实现：

```js
function bridge({ctx, A, B, p, width, height, from, to, api}) {
  // A/B 为两张逻辑舞台 canvas；from/to 对应这两幅画面的场景记录。
  // 共享对象的几何定义、遮挡与位置匹配由此处及两个场景共同组织。
}
```

自定义转场绘制整个舞台，p=0 必须得到 A，p=1 得到 B。反向时交换 A/B 并传入 1-p；实例方法的 this 保留实际定义者。时长可通过 `transitionDuration` 或 `{render,duration}` 配置。

起步示范使用同一中心对象和从该位置展开的圆形揭示。正式作品应为关键交接设计专属关系。

## 初始化与测试接口

```js
const deck = createDeck({canvas, scenes, seed:1, maxDpr:2,
  onGesture(event, deck) {}, onChange(info, deck) {}, onError(error) {}});
window.__deck = deck;
window.ready = true;
```

| API | 用途 |
|---|---|
| `scenes`, `state`, `instance`, `info()` | 场景定义、当前状态、实例与位置；转场中当前信息指向目标场景 |
| `advance()`, `back()`, `jump(id,beat)` | 推进、返回、立即定位 |
| `setAuto(bool)`, `play()`, `pause()`, `setPaused(bool)` | 自动推进与帧循环控制 |
| `seek(id,beat,seconds,{mx,my})` | 暂停、重建场景，从进入起按固定步长模拟 |
| `renderAt(...)` | seek 别名 |
| `transitionAt(toId,p)` | 重建相邻场景，模拟到指定转场进度 |
| `step(seconds)`, `render()`, `resize()` | 固定步长推进、立即绘制、更新视口 |
| `on(event,callback)` | 订阅 move/transition/auto/gesture/error，返回取消订阅函数 |
| `dispose()` | 清理帧循环、事件、Observer 和场景 |

seek/transitionAt 同步，也可 await。真实导航按键或画布按下会恢复播放。测试事件后调用 `pause()`，再 `step(seconds)`，能隔离墙钟时间。

验收脚本检查约定接口；若重写引擎，保留同等测试能力并适配调用。来源：[动作配方](motion-recipes.md)；入口：[SKILL.md](../SKILL.md)。
