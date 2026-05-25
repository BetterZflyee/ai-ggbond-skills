# XHS 通用提取模板（Hermes 适配版）

原版使用 OpenClaw `evaluate()`，本版适配 Hermes `browser_console(expression=...)`。

## 执行方式

```
browser_console(expression="<JS代码>")
```

返回值为 JS 表达式的返回值（对象/数组会被序列化）。

## 基础提取模板 — 首页/搜索列表

```js
JSON.stringify((() => {
  const pickText = (el, sels) => {
    for (const s of sels) {
      const v = el.querySelector?.(s)?.textContent?.trim();
      if (v) return v;
    }
    return '';
  };
  const num = (v) => {
    const m = String(v || '').replace(/,/g, '').match(/\d+(?:\.\d+)?/);
    return m ? Number(m[0]) : 0;
  };
  return [...document.querySelectorAll('.note-item, .feeds-page .note-item, [class*="note"]')]
    .slice(0, 20)
    .map(el => ({
      title: pickText(el, ['.title', '.note-title', 'h3', 'span']),
      author: pickText(el, ['.author', '.name', '.nickname']),
      likes: pickText(el, ['.like-wrapper', '.count', '[class*="like"]']),
      cover_text: pickText(el, ['.cover', '.img', '[class*="cover"]']),
    }))
    .filter(x => x.title);
})())
```

## 详情页提取模板 — 单篇笔记

```js
JSON.stringify((() => {
  const t = (s) => document.querySelector(s)?.textContent?.trim() || '';
  return {
    title: t('h1, .title, [class*="title"]'),
    body: t('.content, .note-content, [class*="content"]'),
    author: t('.author, .name, .username'),
    likes: t('[class*="like"] .count, .like-count'),
    comments: t('[class*="comment"] .count, .comment-count'),
    collects: t('[class*="collect"] .count, .collect-count'),
    tags: [...document.querySelectorAll('[class*="tag"], [class*="topic"]')].map(e => e.textContent.trim()).join(', '),
    publish_time: t('[class*="date"], [class*="time"], time'),
  };
})())
```

## 首页搜索入口 — 搜索后提取结果

先在搜索框输入关键词（`browser_type`），再执行提取：

```js
JSON.stringify([...document.querySelectorAll('.search-result .note-item, .feeds-page .note-item')]
  .slice(0, 10)
  .map(el => ({
    title: el.querySelector('.title, h3, [class*="title"]')?.textContent?.trim() || '',
    author: el.querySelector('.name, .author, [class*="name"]')?.textContent?.trim() || '',
    likes: el.querySelector('.count, [class*="like"]')?.textContent?.trim() || '',
  }))
  .filter(x => x.title))
```

## 使用建议

- 先 `browser_snapshot()` 确认页面结构，再根据实际 selector 调整提取脚本
- 先做 10-20 条试跑，再扩大样本
- 字段缺失返回空字符串，`filter` 过滤无效条目
- 若 `browser_console` 返回超长结果被截断，先缩小 `slice()` 范围再试
- 小红书页面结构经常变化，提取前务必 snapshot 验证 selector

## 与原版差异

| 原版 (OpenClaw) | 本版 (Hermes) |
|----------------|--------------|
| `evaluate(script)` | `browser_console(expression=script)` |
| 直接返回对象 | 需 `JSON.stringify()` 包裹才能可靠返回 |
| 支持 `$0`/`$$` 等 devtools API | 不支持 devtools-only API，用标准 DOM API |
| 可多行自由格式 | 建议单行或紧凑格式，避免换行问题 |
