/**
 * Dependency-free Canvas 2D presentation runtime.
 * Logical stage: 1920 × 1080, letterboxed into the supplied canvas.
 *
 * Scene definition:
 * { id, title, beats: [{dur, delay?, hold?}], notes?: string[],
 *   enterWith?: 'fade'|'zoom'|'slide'|transitionFunction,
 *   transitionDuration?: number,
 *   create(ctx) => { enter?(state), exit?(state), update?(state),
 *     render(ctx2d, state), pointer?(kind, x, y, state) => boolean,
 *     resize?(view), dispose?(), transition?(transitionArgs) } }
 *
 * Transitions receive {ctx, A, B, p, width, height, from, to, api}.
 * A/B are logical-size canvases; from/to contain {definition, instance, state}.
 * A custom transition is responsible for matching objects across scenes.
 * All create/render/update/transition hooks are synchronous. Preload assets first.
 */

export const WIDTH = 1920;
export const HEIGHT = 1080;
export const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smoothstep = value => { const t = clamp(value); return t * t * (3 - 2 * t); };
export const damp = (speed, dt) => 1 - Math.exp(-speed * dt);
export const easing = Object.freeze({
  linear: t => clamp(t),
  inCubic: t => clamp(t) ** 3,
  outCubic: t => 1 - (1 - clamp(t)) ** 3,
  inOutCubic: value => {
    const t = clamp(value);
    return t < 0.5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2;
  },
  outQuart: t => 1 - (1 - clamp(t)) ** 4,
  outBack: value => { const t = clamp(value) - 1; return 1 + 2.4 * t ** 3 + 1.4 * t ** 2; },
});

export const builtInTransitions = Object.freeze({
  fade({ ctx, A, B, p, width, height }) {
    ctx.drawImage(A, 0, 0, width, height);
    ctx.globalAlpha = p;
    ctx.drawImage(B, 0, 0, width, height);
  },
  zoom({ ctx, A, B, p, width, height }) {
    ctx.drawImage(A, 0, 0, width, height);
    const scale = lerp(0.88, 1, easing.outCubic(p));
    ctx.translate(width / 2, height / 2);
    ctx.scale(scale, scale);
    ctx.globalAlpha = p;
    ctx.drawImage(B, -width / 2, -height / 2, width, height);
  },
  slide({ ctx, A, B, p, width, height }) {
    const q = easing.inOutCubic(p);
    ctx.drawImage(A, -q * width, 0, width, height);
    ctx.drawImage(B, (1 - q) * width, 0, width, height);
  },
});

const FIXED_DT = 1 / 60;
const DEFAULT_BEAT = Object.freeze({ dur: 1, delay: 0, hold: 3 });
const finite = (value, fallback) => Number.isFinite(value) ? value : fallback;
const nonnegative = (value, fallback = 0) => Math.max(0, finite(value, fallback));

function hashString(text) {
  let hash = 2166136261;
  for (const character of text) hash = Math.imul(hash ^ character.codePointAt(0), 16777619);
  return hash >>> 0;
}

function randomGenerator(seed) {
  let value = seed >>> 0;
  return () => {
    value = (value + 0x6D2B79F5) | 0;
    let mixed = Math.imul(value ^ value >>> 15, 1 | value);
    mixed ^= mixed + Math.imul(mixed ^ mixed >>> 7, 61 | mixed);
    return ((mixed ^ mixed >>> 14) >>> 0) / 4294967296;
  };
}

export function createDeck(options = {}) {
  const { canvas, scenes, onGesture, onError, onChange } = options;
  if (!canvas || typeof canvas.getContext !== 'function')
    throw new TypeError('createDeck requires a canvas element.');
  if (!Array.isArray(scenes) || !scenes.length)
    throw new TypeError('createDeck requires at least one scene.');

  const document = canvas.ownerDocument;
  const window = document?.defaultView;
  if (!document || !window) throw new Error('createDeck requires a browser document.');
  const reducedMotion = !!(options.reducedMotion ??
    window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false);
  const screen = canvas.getContext('2d');
  if (!screen) throw new Error('Canvas 2D is unavailable.');
  const ids = new Set();
  const records = scenes.map((definition, index) => {
    if (!definition || typeof definition.id !== 'string' || !definition.id || ids.has(definition.id))
      throw new TypeError(`Scene ${index} needs a unique, nonempty string id.`);
    if (typeof definition.create !== 'function')
      throw new TypeError(`Scene ${definition.id} needs create(ctx).`);
    ids.add(definition.id);
    const beats = (definition.beats?.length ? definition.beats : [DEFAULT_BEAT]).map(beat => ({
      ...beat,
      dur: Math.max(0.001, finite(beat.dur, 1)),
      delay: nonnegative(beat.delay),
      hold: nonnegative(beat.hold, 3),
    }));
    return { definition, index, beats, instance: null, state: null, surface: null };
  });

  const listeners = new Map();
  const removers = [];
  const previousDeck = window.__deck;
  const oldTouchAction = canvas.style.touchAction;
  const oldTabindex = canvas.getAttribute('tabindex');
  canvas.style.touchAction = 'none';
  if (oldTabindex === null) canvas.setAttribute('tabindex', '0');

  let api, current = -1, transition = null, pendingAdvance = false;
  let auto = !!options.autoplay, paused = options.autoStart === false;
  let disposed = false, frameId = 0, previousTime = null, clock = 0;
  let interacted = false, gesture = null;
  const maxDpr = Math.max(0.5, finite(options.maxDpr, 2));
  const mouse = { x: 0, y: 0, tx: 0, ty: 0, px: WIDTH / 2, py: HEIGHT / 2, down: false, inside: false };
  const view = { width: WIDTH, height: HEIGHT, w: WIDTH, h: HEIGHT,
    x0: 0, y0: 0, x1: WIDTH, y1: HEIGHT,
    cssWidth: WIDTH, cssHeight: HEIGHT, scale: 1, offsetX: 0, offsetY: 0, dpr: 1 };

  function makeCanvas(width = WIDTH, height = HEIGHT) {
    const element = document.createElement('canvas');
    element.width = width;
    element.height = height;
    return element;
  }
  const composition = makeCanvas();
  const compositionContext = composition.getContext('2d');

  function emit(type, data) {
    for (const callback of listeners.get(type) || []) callback(data);
    if (type === 'move' && onChange) onChange(data, api);
  }
  function notify() { emit('move', api.info()); }
  function ensureLive() { if (disposed) throw new Error('This deck has been disposed.'); }
  function indexOfScene(id) {
    const index = typeof id === 'number' ? id : records.findIndex(record => record.definition.id === id);
    if (!Number.isInteger(index) || index < 0 || index >= records.length)
      throw new RangeError(`Unknown scene: ${String(id)}`);
    return index;
  }
  function activeRecord() { return records[transition ? transition.to : current]; }

  function ensureRecord(record) {
    if (record.instance) return record;
    const progress = record.beats.map(() => 0);
    const since = record.beats.map(() => 0);
    const state = { t: 0, globalTime: clock, dt: 0, beat: 0, reducedMotion,
      p: progress, progress, _since: since, n: progress.length,
      enter: 1, exit: 0, dir: 1, mouse, view, q: 1,
      at: beat => (progress[beat] || 0) * (record.beats[beat]?.dur || 0),
      k(beat, start, end, ease = easing.inOutCubic) {
        return ease(clamp((this.at(beat) - start) / Math.max(0.0001, end - start)));
      },
      since: beat => since[beat] || 0,
    };
    record.state = state;
    record.surface = makeCanvas();
    const helpers = { clamp, lerp, smoothstep, damp, easing };
    const context = { width: WIDTH, height: HEIGHT, view, mouse, helpers, reducedMotion,
      canvas: record.surface, screenCanvas: canvas, createCanvas: makeCanvas,
      clamp, lerp, smoothstep, damp, easing,
      random: randomGenerator(hashString(record.definition.id) ^ finite(options.seed, 1)),
      get deck() { return api; },
    };
    const instance = record.definition.create(context);
    if (!instance || typeof instance.then === 'function' || typeof instance.render !== 'function')
      throw new TypeError(`Scene ${record.definition.id}: create must synchronously return { render(ctx2d, state) }.`);
    record.instance = instance;
    instance.resize?.(view);
    return record;
  }

  function resetRecord(record, beat = 0, completeCurrent = false) {
    ensureRecord(record);
    const state = record.state;
    state.t = 0; state.dt = 0; state.globalTime = clock;
    state.beat = clamp(Math.floor(finite(beat, 0)), 0, record.beats.length - 1);
    state.enter = 1; state.exit = 0; state.dir = completeCurrent ? -1 : 1;
    for (let i = 0; i < state.n; i++) {
      const complete = i < state.beat || (completeCurrent && i === state.beat);
      state.p[i] = complete ? 1 : 0;
      state._since[i] = complete ? record.beats[i].delay + record.beats[i].dur + record.beats[i].hold : 0;
    }
    record.instance.enter?.(state);
    if (reducedMotion) stepRecord(record, 0);
    else record.instance.update?.(state);
  }

  function stepRecord(record, dt) {
    const state = record.state;
    state.dt = dt; state.t += dt; state.globalTime = clock;
    for (let i = 0; i < state.n; i++) {
      const beat = record.beats[i];
      if (i <= state.beat) {
        state._since[i] += dt;
        if (state._since[i] >= beat.delay)
          state.p[i] = reducedMotion ? 1
            : Math.min(1, state.p[i] + dt / beat.dur * (i < state.beat ? 3 : 1));
      } else {
        state._since[i] = 0;
        state.p[i] = reducedMotion ? 0 : Math.max(0, state.p[i] - dt / beat.dur * 2.4);
      }
    }
    record.instance.update?.(state);
  }

  function transitionSpec(to, override) {
    // Keep scene time and direct interaction alive, but replace spatial motion
    // (including author-defined transitions) with a one-frame opacity change.
    if (reducedMotion)
      return { name: 'fade', render: builtInTransitions.fade, owner: to.instance, duration: 0.01 };
    const chosen = override ?? to.instance.transition ?? to.definition.transition ?? to.definition.enterWith ?? options.transition ?? 'fade';
    const name = typeof chosen === 'string' ? chosen : 'custom';
    const entry = typeof chosen === 'string'
      ? (options.transitions?.[chosen] ?? builtInTransitions[chosen]) : chosen;
    if (!entry) throw new RangeError(`Unknown transition: ${name}`);
    const render = typeof entry === 'function' ? entry : entry.render;
    if (typeof render !== 'function') throw new TypeError(`Transition ${name} needs a render function.`);
    return { name, render, owner: to.instance,
      duration: Math.max(0.001, finite(entry.duration ?? entry.dur,
        finite(to.definition.transitionDuration, finite(options.transitionDuration, 0.7)))) };
  }

  function finishTransition() {
    if (!transition) return;
    const finished = transition;
    records[finished.from].instance.exit?.(records[finished.from].state);
    current = finished.to;
    records[current].state.enter = 1;
    records[current].state.exit = 0;
    transition = null;
    notify();
    if (pendingAdvance) { pendingAdvance = false; advance(); }
  }

  function go(index, { reverse = false, beat = 0, with: override } = {}) {
    if (index === current && !transition) return;
    if (transition) finishTransition();
    const to = ensureRecord(records[index]);
    resetRecord(to, beat, reverse);
    const spec = transitionSpec(reverse ? records[current] : to, override);
    transition = { from: current, to: index, p: 0, time: 0, speed: 1, reverse,
      ...spec, duration: spec.duration * (reverse ? 0.55 : 1) };
    records[current].state.exit = reverse ? 1 : 0;
    to.state.enter = reverse ? 1 : 0;
    emit('transition', { from: records[current].definition.id, to: to.definition.id, name: spec.name });
    notify();
    render();
  }

  function advance() {
    ensureLive();
    if (transition) { transition.speed = 3.5; pendingAdvance = true; return; }
    const record = records[current];
    if (record.state.beat < record.beats.length - 1) {
      record.state.beat++; record.state.dir = 1;
      if (reducedMotion) stepRecord(record, 0);
      notify();
    } else if (current < records.length - 1) go(current + 1);
    render();
  }

  function back() {
    ensureLive();
    if (transition) { transition.speed = 3.5; return; }
    const record = records[current];
    record.state.dir = -1;
    if (record.state.beat > 0) {
      record.state.beat--;
      if (reducedMotion) stepRecord(record, 0);
      notify();
    }
    else if (current > 0) go(current - 1, { reverse: true, beat: records[current - 1].beats.length - 1 });
    render();
  }

  function jump(id, beat = 0) {
    ensureLive();
    const index = indexOfScene(id);
    pendingAdvance = false;
    if (transition) finishTransition();
    records[current]?.instance?.exit?.(records[current].state);
    current = index;
    resetRecord(records[current], beat);
    notify(); render();
    return api;
  }

  function tick(dt, allowAuto = true) {
    clock += dt;
    const factor = damp(5, dt);
    mouse.x += (mouse.tx - mouse.x) * factor;
    mouse.y += (mouse.ty - mouse.y) * factor;
    if (transition) {
      const trans = transition;
      trans.time += dt * trans.speed;
      trans.p = clamp(trans.time / trans.duration);
      const from = records[trans.from], to = records[trans.to];
      const q = trans.reverse ? 1 - trans.p : trans.p;
      if (trans.reverse) { to.state.exit = q; from.state.enter = q; }
      else { from.state.exit = q; to.state.enter = q; }
      stepRecord(from, dt); stepRecord(to, dt);
      if (trans.p >= 1) finishTransition();
    } else {
      const record = records[current];
      stepRecord(record, dt);
      const beat = record.beats[record.state.beat];
      if (allowAuto && auto && record.state.since(record.state.beat) > beat.delay + beat.dur + beat.hold) {
        if (current === records.length - 1 && record.state.beat === record.beats.length - 1) api.setAuto(false);
        else advance();
      }
    }
  }

  function drawRecord(record) {
    const ctx = record.surface.getContext('2d');
    ctx.save();
    try {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0, 0, WIDTH, HEIGHT);
      record.instance.render(ctx, record.state);
    } finally { ctx.restore(); }
    return record.surface;
  }

  function render() {
    ensureLive();
    if (current < 0) return;
    let picture;
    if (transition) {
      const trans = transition;
      const from = records[trans.from], to = records[trans.to];
      const first = trans.reverse ? to : from, second = trans.reverse ? from : to;
      const A = drawRecord(first), B = drawRecord(second);
      compositionContext.save();
      try {
        compositionContext.setTransform(1, 0, 0, 1, 0, 0);
        compositionContext.clearRect(0, 0, WIDTH, HEIGHT);
        trans.render.call(trans.owner, { ctx: compositionContext, A, B,
          p: trans.reverse ? 1 - trans.p : trans.p,
          width: WIDTH, height: HEIGHT, from: first, to: second, api });
      } finally { compositionContext.restore(); }
      picture = composition;
    } else picture = drawRecord(records[current]);

    screen.save();
    try {
      screen.setTransform(1, 0, 0, 1, 0, 0);
      screen.globalAlpha = 1;
      screen.globalCompositeOperation = 'source-over';
      screen.fillStyle = options.background ?? '#0b0f14';
      screen.fillRect(0, 0, canvas.width, canvas.height);
      screen.setTransform(view.dpr * view.scale, 0, 0, view.dpr * view.scale,
        view.dpr * view.offsetX, view.dpr * view.offsetY);
      screen.drawImage(picture, 0, 0, WIDTH, HEIGHT);
    } finally { screen.restore(); }
  }

  function resize() {
    if (disposed) return;
    const bounds = canvas.getBoundingClientRect();
    const width = Math.max(1, bounds.width || canvas.clientWidth || WIDTH);
    const height = Math.max(1, bounds.height || canvas.clientHeight || HEIGHT);
    view.cssWidth = width; view.cssHeight = height;
    view.dpr = clamp(finite(window.devicePixelRatio, 1), 0.5, maxDpr);
    view.scale = Math.min(width / WIDTH, height / HEIGHT);
    view.offsetX = (width - WIDTH * view.scale) / 2;
    view.offsetY = (height - HEIGHT * view.scale) / 2;
    canvas.width = Math.max(1, Math.round(width * view.dpr));
    canvas.height = Math.max(1, Math.round(height * view.dpr));
    for (const record of records) record.instance?.resize?.(view);
    if (current >= 0) render();
  }

  function frame(now) {
    frameId = 0;
    if (disposed || paused) return;
    const dt = previousTime === null ? 0 : clamp((now - previousTime) / 1000, 0, 0.05);
    previousTime = now;
    try { tick(dt); render(); }
    catch (error) {
      setPaused(true);
      emit('error', error);
      if (onError) onError(error); else window.console.error(error);
      return;
    }
    if (!paused && !disposed) frameId = window.requestAnimationFrame(frame);
  }

  function setPaused(value) {
    ensureLive();
    paused = !!value;
    previousTime = null;
    if (frameId) window.cancelAnimationFrame(frameId);
    frameId = 0;
    if (!paused) frameId = window.requestAnimationFrame(frame);
    return api;
  }

  function fixedSteps(seconds, callback) {
    const duration = nonnegative(seconds);
    const whole = Math.floor(duration / FIXED_DT);
    for (let i = 0; i < whole; i++) callback(FIXED_DT);
    const remainder = duration - whole * FIXED_DT;
    if (remainder > 1e-10) callback(remainder);
  }

  function discard(record) {
    record.instance?.dispose?.();
    record.instance = null; record.state = null; record.surface = null;
  }

  function simulate(record, beatIndex, seconds) {
    discard(record);
    resetRecord(record, 0);
    const targetBeat = clamp(Math.floor(finite(beatIndex, 0)), 0, record.beats.length - 1);
    for (let beat = 0; beat <= targetBeat; beat++) {
      record.state.beat = beat;
      if (reducedMotion) stepRecord(record, 0);
      const definition = record.beats[beat];
      const duration = beat === targetBeat ? nonnegative(seconds)
        : definition.delay + definition.dur + definition.hold;
      fixedSteps(duration, dt => { clock += dt; stepRecord(record, dt); });
    }
    record.state.dt = 0;
    record.instance.update?.(record.state);
  }

  /** Freeze RAF, recreate this scene, then replay from enter at 1/60 s. */
  function seek(id, beatIndex = 0, seconds = 0, pointer = {}) {
    ensureLive();
    const index = indexOfScene(id);
    setPaused(true);
    gesture = null; pendingAdvance = false; transition = null;
    records[current]?.instance?.exit?.(records[current].state);
    current = index; clock = 0;
    const mx = finite(pointer.mx, 0), my = finite(pointer.my, 0);
    Object.assign(mouse, { x: mx, y: my, tx: mx, ty: my,
      px: (mx + 1) / 2 * WIDTH, py: (1 - my) / 2 * HEIGHT,
      down: false, inside: false });
    simulate(records[index], beatIndex, seconds);
    notify(); render();
    return api;
  }

  /** Freeze RAF and replay the complete incoming transition to a normalized p. */
  function transitionAt(id, progress = 0) {
    ensureLive();
    const index = indexOfScene(id);
    if (index === 0) return seek(0, 0, 0);
    setPaused(true);
    gesture = null; pendingAdvance = false; transition = null;
    records[current]?.instance?.exit?.(records[current].state);
    current = index - 1; clock = 0;
    Object.assign(mouse, { x: 0, y: 0, tx: 0, ty: 0,
      px: WIDTH / 2, py: HEIGHT / 2, down: false, inside: false });
    const from = records[current], finalBeat = from.beats.length - 1;
    const last = from.beats[finalBeat];
    simulate(from, finalBeat, last.delay + last.dur + last.hold);
    discard(records[index]);
    go(index);
    const duration = transition.duration * clamp(finite(progress, 0));
    fixedSteps(duration, dt => tick(dt, false));
    if (progress >= 1 && transition) {
      transition.p = 1;
      finishTransition();
    }
    render();
    return api;
  }

  function coordinates(event) {
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left - view.offsetX) / view.scale;
    const y = (event.clientY - rect.top - view.offsetY) / view.scale;
    return { x, y, inside: x >= 0 && x <= WIDTH && y >= 0 && y <= HEIGHT };
  }
  function setPointer(point) {
    mouse.px = point.x; mouse.py = point.y; mouse.inside = point.inside;
    mouse.tx = clamp(point.x / WIDTH * 2 - 1, -1, 1);
    mouse.ty = clamp(1 - point.y / HEIGHT * 2, -1, 1);
  }
  function interaction(event) {
    if (interacted) return;
    interacted = true;
    onGesture?.(event, api);
    emit('gesture', event);
  }
  function scenePointer(kind, point) {
    if (transition) return false;
    const record = records[current];
    return !!record.instance.pointer?.(kind, point.x, point.y, record.state);
  }
  function releaseGesture(kind = 'cancel', event) {
    if (!gesture) return;
    const previous = gesture;
    gesture = null; mouse.down = false;
    const point = event ? coordinates(event) : previous.point;
    scenePointer(kind, point);
    if (canvas.hasPointerCapture?.(previous.id)) canvas.releasePointerCapture(previous.id);
  }
  function handleDown(event) {
    if (gesture || (event.button !== 0 && event.pointerType !== 'touch')) return;
    const point = coordinates(event);
    if (!point.inside) return;
    event.preventDefault();
    interaction(event);
    if (paused) setPaused(false);
    canvas.focus({ preventScroll: true });
    setPointer(point); mouse.down = true;
    const claimed = scenePointer('down', point);
    gesture = { id: event.pointerId, claimed, x: event.clientX, y: event.clientY,
      time: window.performance.now(), point };
    // Capture all initiated gestures, so leaving the stage cannot strand a swipe.
    canvas.setPointerCapture?.(event.pointerId);
  }
  function handleMove(event) {
    if (gesture && event.pointerId !== gesture.id) return;
    const point = coordinates(event);
    setPointer(point);
    if (gesture) gesture.point = point;
    scenePointer('move', point);
  }
  function handleUp(event) {
    if (!gesture || event.pointerId !== gesture.id) return;
    const previous = gesture;
    releaseGesture('up', event);
    if (previous.claimed) return;
    const dx = event.clientX - previous.x, dy = event.clientY - previous.y;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) dx < 0 ? advance() : back();
    else if (Math.abs(dx) < 12 && Math.abs(dy) < 12 && window.performance.now() - previous.time < 600) advance();
  }
  function editableTarget(target) {
    return target?.closest?.('input,textarea,select,button,a[href],[contenteditable]:not([contenteditable="false"]),[role="textbox"]');
  }
  function handleKey(event) {
    if (event.metaKey || event.ctrlKey || event.altKey || editableTarget(event.target)) return;
    const key = event.key;
    const forward = ['ArrowRight', 'ArrowDown', ' ', 'PageDown', 'Enter'].includes(key);
    const backward = ['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(key);
    if (!forward && !backward && !['Home', 'End', 'a', 'A'].includes(key)) return;
    event.preventDefault();
    if (event.repeat) return;
    interaction(event);
    if (paused) setPaused(false);
    releaseGesture();
    if (forward) advance();
    else if (backward) back();
    else if (key === 'Home') jump(0);
    else if (key === 'End') jump(records.length - 1);
    else if (key.toLowerCase() === 'a') api.setAuto(!auto);
  }
  function listen(target, type, handler, extra) {
    target.addEventListener(type, handler, extra);
    removers.push(() => target.removeEventListener(type, handler, extra));
  }

  api = {
    scenes,
    canvas,
    view,
    get state() { return activeRecord()?.state; },
    get instance() { return activeRecord()?.instance; },
    get auto() { return auto; },
    get paused() { return paused; },
    get time() { return clock; },
    get transition() { return transition; },
    info() {
      const record = activeRecord();
      if (!record) return null;
      return { scene: record.definition.id, id: record.definition.id, index: record.index,
        title: record.definition.title || record.definition.id, beat: record.state.beat,
        beats: record.beats.length, notes: record.definition.notes?.[record.state.beat] || '',
        t: record.state.t, time: clock, auto, paused,
        transition: transition ? { name: transition.name, progress: transition.p } : null };
    },
    advance, back, jump, seek, renderAt: seek, transitionAt, render, resize,
    setAuto(value) { ensureLive(); auto = !!value; emit('auto', auto); return api; },
    setPaused,
    pause() { return setPaused(true); },
    play() { return setPaused(false); },
    // Deterministically advance the current live state; useful after injected events.
    step(seconds = FIXED_DT) { ensureLive(); fixedSteps(seconds, dt => tick(dt)); render(); return api; },
    on(type, callback) {
      ensureLive();
      if (typeof callback !== 'function') throw new TypeError('Listener must be a function.');
      if (!listeners.has(type)) listeners.set(type, new Set());
      listeners.get(type).add(callback);
      return () => listeners.get(type)?.delete(callback);
    },
    dispose() {
      if (disposed) return;
      releaseGesture();
      setPaused(true);
      records[current]?.instance?.exit?.(records[current].state);
      disposed = true;
      removers.forEach(remove => remove());
      for (const record of records) discard(record);
      listeners.clear();
      canvas.style.touchAction = oldTouchAction;
      if (oldTabindex === null) canvas.removeAttribute('tabindex');
      else canvas.setAttribute('tabindex', oldTabindex);
      if (window.__deck === api) {
        if (previousDeck === undefined) delete window.__deck;
        else window.__deck = previousDeck;
      }
    },
  };

  resize();
  current = indexOfScene(options.startScene ?? 0);
  resetRecord(records[current], options.startBeat ?? 0);
  render();
  listen(canvas, 'pointerdown', handleDown);
  listen(canvas, 'pointermove', handleMove);
  listen(canvas, 'pointerup', handleUp);
  listen(canvas, 'pointercancel', event => {
    if (gesture?.id === event.pointerId) releaseGesture('cancel', event);
  });
  listen(canvas, 'lostpointercapture', event => {
    if (gesture?.id === event.pointerId) releaseGesture('cancel', event);
  });
  listen(canvas, 'contextmenu', event => { event.preventDefault(); interaction(event); back(); });
  listen(window, 'keydown', handleKey);
  listen(window, 'blur', () => releaseGesture());
  listen(window, 'resize', resize);
  listen(document, 'visibilitychange', () => { previousTime = null; });
  if (typeof window.ResizeObserver === 'function') {
    const observer = new window.ResizeObserver(resize);
    observer.observe(canvas);
    removers.push(() => observer.disconnect());
  }
  if (options.expose !== false) window.__deck = api;
  if (!paused) frameId = window.requestAnimationFrame(frame);
  notify();
  return api;
}
