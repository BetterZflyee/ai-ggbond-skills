# XHS 运行规则（Hermes CDP 适配版）

## 0.1 低 token 与快照约束

- 优先 `browser_snapshot()`（compact模式），减少完整页面 dump
- 只在关键节点做 snapshot：登录确认、到发布页、填写完成、发布前停顿
- 避免反复抓取同一页面；重复调用优先复用已获取的 snapshot
- 每个动作最多重试 1 次；第二次失败改稳健路径并汇报
- 记录关键证据：账号名、页面状态、按钮可见、字数等，返回可执行信号

## 0.2 浏览器稳定规则（最高优先）

- 默认使用 Hermes CDP 浏览器工具链
- 每次动作前先确认在目标页面（`browser_snapshot()` 验证）
- 若出现页面加载失败，先 `browser_navigate` 到首页再重试
- 连续 2 次点击/导航失败后改稳健路径（如直达点击改为先 snapshot 再定位），不做盲重试

## 0.3 Hermes 浏览器工具映射

| 动作 | Hermes 工具 | 说明 |
|------|-----------|------|
| 打开页面 | `browser_navigate(url)` | 导航到指定 URL |
| 获取页面结构 | `browser_snapshot()` | 返回 compact 页面快照，含可交互元素 ref |
| 完整页面内容 | `browser_snapshot(full=true)` | 用于需要完整内容的场景（谨慎使用） |
| 点击元素 | `browser_click(ref="@eXX")` | 根据 snapshot 中的 ref 点击 |
| 输入文本 | `browser_type(ref="@eXX", text="...")` | 在输入框中输入文本 |
| 执行 JS | `browser_console(expression="...")` | 用于提取页面数据 |
| 键盘操作 | `browser_press(key="Enter")` | 发送键盘事件 |
| 截图视觉分析 | `browser_vision(question="...")` | 用于需要视觉理解的场景 |

## 0.4 页面数据提取模板（替代原版 evaluate）

使用 `browser_console(expression=...)` 执行 JS 提取页面数据：

```js
// 提取笔记列表
(() => {
  const pickText = (el, sels) => {
    for (const s of sels) {
      const v = el.querySelector?.(s)?.textContent?.trim();
      if (v) return v;
    }
    return '';
  };
  return [...document.querySelectorAll('.note-item, .feeds-page .note-item')]
    .slice(0, 20)
    .map(el => ({
      title: pickText(el, ['.title', '.note-title', 'h3']),
      author: pickText(el, ['.author', '.name']),
      likes: pickText(el, ['.like-wrapper', '.count']),
    }))
    .filter(x => x.title);
})()
```

## 3.5 搜索并浏览（核心约束）

1. 仅从搜索结果页点击进入帖子，禁止直接 `browser_navigate` 到 `/explore/<id>`
2. 默认跳过本账号作者内容（避免自刷）
3. 进入后先校验：不是 404、可见评论/互动信息、可识别标题或作者
4. 进入方式优先点卡片本体，避免点头像/作者名导致跳错
5. 若评论控件需先触发输入事件，使用 `browser_press` 或 `browser_console` 触发
6. 两条点击失败或 404 后返回搜索页换下一条，不对同链接直跳重试

## 6.0 回放与降级

- 若搜索结构变化先 `browser_snapshot(full=true)` 更新 selector 再继续
- 关键页（创作页、探索页、用户页）尽量复用已打开 tab
- 先告诉用户"已达异常节点"，避免无意义继续操作导致误发
- 发布页关键动作失败时：
  1) 先 `browser_snapshot()` 刷新 ref
  2) 同动作最多再试 1 次
  3) 仍失败则切稳健路径（同义入口/用户手动最后一击）
- 轮播详情页抓图时，禁止取第一个 `.img-container`；必须优先抓取 `.swiper-slide-active:not(.swiper-slide-duplicate) .img-container img`
- 图生图产物需要做"相似度体感检查"
- 涉及文件上传时，默认先检查文件路径是否可访问

## 首次使用注意事项

- 浏览器首次访问小红书需要扫码登录
- 登录后 cookie 会保持在浏览器 session 中
- 后续同一会话无需重复登录
- 若跨会话需要重新登录，使用 `browser_navigate` 到首页，完成扫码
