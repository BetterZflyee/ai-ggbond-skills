# 2026-05-25 科技蓝精排版成功模式（v3）

## 背景

《GitHub 热榜上周杀疯了：AI Agent 正在集体补课》排版迭代三次：
- v1：暖米白手绘风 + 语义分段，用户反馈「可读性很差」
- v2：科技蓝简化版，用户反馈「排版太简陋、链接不能点」
- **v3：复用此前 Antigravity 文章的成功 HTML 结构 + 科技蓝配色 → 用户认可**

## 成功 HTML 结构（可直接复用）

### 整体容器
```html
<section style="max-width:750px; margin:0 auto; padding:24px 16px 40px 16px; box-sizing:border-box; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',...; background:#FFFFFF;">
```

### 标题区（正文内，H1 + 副标题）
```html
<h1 style="margin:22px 0 14px 0; text-align:center; color:#1E293B; font-size:24px; line-height:1.42; font-weight:800;">
  主标题
</h1>
<p style="margin:0 auto 28px auto; max-width:620px; text-align:center; color:#475569; font-size:14px; line-height:1.75;">
  副标题
</p>
```

### 章节标题（分隔线 + H2）
```html
<div style="margin:48px 0 12px 0;">
  <div style="width:42px; height:3px; background:#2563EB; border-radius:2px; margin-bottom:13px;"></div>
  <h2 style="margin:0; color:#1E293B; font-size:19px; line-height:1.52; font-weight:800;">
    章节标题
  </h2>
</div>
```

### 配图（居中容器 + 阴影 + 圆角）
```html
<div style="margin:22px 0 34px 0; text-align:center;">
  <img src="images/xxx.png" alt="" style="display:block; width:100%; max-width:100%; height:auto; border-radius:14px; box-shadow:0 8px 28px rgba(30,64,175,0.08);">
</div>
```

### 正文段落
```html
<p style="margin:18px 0; text-align:justify; color:#1E293B; font-size:15.5px; line-height:1.92; letter-spacing:0.3px;">
  正文内容，<strong style="color:#1D4ED8; font-weight:700;">加粗关键词</strong>继续正文。
</p>
```

### 引用卡片（蓝底 + 左边框）
```html
<section style="margin:28px 0; padding:18px 18px 18px 20px; background:#EFF6FF; border-left:4px solid #3B82F6; border-radius:10px;">
  <p style="margin:0; color:#1E293B; font-size:15px; line-height:1.9; text-align:justify;">
    <strong>《书名》作者说：引用内容。</strong>
  </p>
</section>
```

### 可点击链接
```html
<a href="https://github.com/xxx/xxx" style="color:#3B82F6; text-decoration:underline;">https://github.com/xxx/xxx</a>
```

## 配色方案

| 元素 | 色值 | 用途 |
|---|---|---|
| 正文 | `#1E293B` | 深灰蓝，不刺眼 |
| 强调 | `#1D4ED8` | 深蓝加粗 |
| 链接 | `#3B82F6` | 亮蓝下划线 |
| 副标题 | `#475569` | 中灰 |
| 分隔线 | `#2563EB` | 蓝色 |
| 引用背景 | `#EFF6FF` | 浅蓝底 |
| 引用边框 | `#3B82F6` | 蓝左边框 |

## 曾经被否定的版本及原因

| 版本 | 问题 |
|---|---|
| v1 暖米白手绘 | 用户说「可读性很差」 |
| v2 科技蓝简化 | 只有 `<p>` + `<h2>` + 简单引用，用户说「排版太简陋」「链接不能点」 |
| v3（成功） | 完整视觉体系：分隔线 + 阴影 + 引用卡 + `<a>` 链接 + 标题在正文内 |

## 标题处理规则（飞哥 2026-05-25 确认）

- 主标题和副标题用 **破折号「——」** 合并，放在草稿箱标题栏
- 正文顶部同时显示 H1 主标题 + 副标题段落（与草稿箱标题栏一致）
- 示例：`GitHub 热榜上周杀疯了：AI Agent 正在集体补课——它们补的不是模型能力，而是记忆、技能、上下文和工作流`
