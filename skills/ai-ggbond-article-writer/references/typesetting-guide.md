# 微信公众号排版指南

## 概览

本文档提供微信公众号专业排版的完整指南，包括字体规范、配色策略、HTML模板和常用组件库。

## 排版核心原则

### 排版三大功能

1. **拯救碎片化注意力**
   - 读者只有3秒注意力（地铁、卫生间、工作间隙）
   - 干净排版实现"无痛阅读"
   - 避免：彩虹色 + 密集文字 = 瞬间跳出

2. **视觉导航系统**
   - 层级标题作为路标
   - 关键词高亮实现3秒信息抓取

3. **视觉品牌识别**
   - 一致排版 = 可识别的品牌签名
   - 坚持3个月建立品牌印记

### 风格一致性公式

```
风格 = 标题格式 + 主色调 + 正文格式 + 图片风格 + 头尾引导
```

**关键规则**：坚持一种风格3个月以上。频繁切换风格（今天文艺，明天赛博朋克）会导致粉丝流失。

## 字体规范

### 字号指南

| 字号 | 用途 | 说明 |
|------|------|------|
| 12px | 注释、来源标注 | 最小可读字号 |
| 14px | 紧凑优雅风格 | 文艺号首选 |
| 15px | 安全默认 | 永不出错的选择 |
| 16px | 较大文字 | 视觉不够精致 |
| 17px | 小节标题 | 章节标题使用 |

**推荐**：正文使用 14px 或 15px，平衡可读性和美观度。

**注意**：面向老年读者时，所有字号 +2px。

## 间距规范

### 字间距

- 推荐：1-1.5px
- 避免二维码被压缩

### 行间距

- 推荐：1.5-1.75倍
- 亲密但不侵扰

### 段落间距

- 段落之间：1空行
- 章节之间：上2行 + 下1行

### 页边距

- 推荐：8-16px
- 边缘留白减轻阅读压力

## 对齐原则

| 内容类型 | 对齐方式 | 说明 |
|---------|---------|------|
| 正文 | 两端对齐 | 避免右边缘参差不齐 |
| 短文/注释 | 居中对齐 | 瞬间提升高级感 |

## 配色策略

### 黄金法则

**1个主色 + ≤2个辅助色**

使用一致的主色调增加阅读连贯性。彩虹色文字造成碎片化和混乱。

### 按内容类型自动选色

| 内容类型 | 主色调 | 辅助色 | 适用场景 |
|---------|--------|--------|---------|
| 科技/商务 | #1E88E5 | #E3F2FD | 科技、商务、专业内容 |
| 生活/美食 | #A8DADC | #F1FAEE | 生活方式、美食分享 |
| 励志/能量 | #FF6B35 | #FFF3E0 | 励志、正能量内容 |
| 教育/知识 | #00897B | #E0F2F1 | 知识分享、教程 |
| 奢华/高端 | #7B1FA2 | #F3E5F5 | 高端品牌、奢侈品 |
| 健康/养生 | #43A047 | #E8F5E9 | 健康、养生内容 |

### 正文颜色

- 推荐正文：#595959 或 #3f3f3f（比纯黑#000000柔和）
- 强调色：使用品牌主色 + 加粗
- **关键规则**：每屏≤3处强调，全强调 = 无强调！

### 颜色心理学

**活力积极**：
- 橙色、黄色
- 适用：励志、正能量内容

**专业商务**：
- 蓝色、灰色、红色
- 适用：企业、正式内容

**清新文艺**：
- 莫兰迪色系（低饱和度YYDS！）
- 适用：生活方式、美学内容

## HTML模板结构

### 基础模板

```html
<section style="max-width: 750px; margin: 0 auto; padding: 20px 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; font-size: 15px; color: #3f3f3f; line-height: 1.75; letter-spacing: 0.5px; background: #ffffff;">

  <!-- 主标题 -->
  <h1 style="font-size: 24px; font-weight: bold; color: #1a1a1a; text-align: center; margin: 20px 0 30px 0; line-height: 1.4;">
    文章主标题
  </h1>

  <!-- 副标题 (可选) -->
  <p style="font-size: 14px; color: #666; text-align: center; margin: -20px 0 30px 0; font-style: italic;">
    副标题或一句话概括
  </p>

  <!-- 引言段落 -->
  <p style="margin: 20px 0; text-align: justify;">
    引言内容，用于吸引读者注意力。
  </p>

  <!-- 章节编号 -->
  <div style="margin: 40px 0 10px 0;">
    <span style="display: inline-block; font-size: 18px; font-weight: bold; color: {{PRIMARY_COLOR}}; padding: 5px 15px; border-left: 4px solid {{PRIMARY_COLOR}};">
      01.
    </span>
  </div>

  <h2 style="font-size: 17px; font-weight: bold; color: #1a1a1a; margin: 15px 0;">
    章节标题
  </h2>

  <p style="margin: 15px 0; text-align: justify;">
    正文内容。可以使用 <strong style="color: {{PRIMARY_COLOR}};">加粗强调</strong> 突出关键词。
  </p>

  <!-- 图片 -->
  <div style="text-align: center; margin: 30px 0;">
    <img src="[IMAGE_URL]" alt="描述" style="max-width: 100%; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <p style="font-size: 12px; color: #999; text-align: center; margin-top: 10px;">
      图片说明
    </p>
  </div>

  <!-- 底部CTA -->
  <div style="margin: 30px 0 0 0; padding: 20px; border-top: 1px solid #e0e0e0; text-align: center;">
    <p style="margin: 0; font-size: 14px; color: #666;">
      📌 更多相关内容，关注主页查看~
    </p>
  </div>

</section>
```

## 常用组件库

### 1. 引用块

```html
<div style="border-left: 4px solid {{PRIMARY_COLOR}}; padding-left: 15px; margin: 20px 0; font-style: italic; color: #666;">
  <p style="margin: 5px 0;">引用文字或名言</p>
  <p style="margin: 5px 0; font-size: 13px; color: #999;">— 来源或作者</p>
</div>
```

### 2. 编号列表

```html
<div style="margin: 20px 0;">
  <div style="display: flex; margin: 15px 0;">
    <div style="flex-shrink: 0; width: 28px; height: 28px; background: {{PRIMARY_COLOR}}; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; margin-right: 12px;">1</div>
    <div style="flex: 1;"><p style="margin: 0;">第一点内容</p></div>
  </div>
  <div style="display: flex; margin: 15px 0;">
    <div style="flex-shrink: 0; width: 28px; height: 28px; background: {{PRIMARY_COLOR}}; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; margin-right: 12px;">2</div>
    <div style="flex: 1;"><p style="margin: 0;">第二点内容</p></div>
  </div>
</div>
```

### 3. 提示框

```html
<div style="background: {{ACCENT_COLOR}}; border-left: 4px solid {{PRIMARY_COLOR}}; padding: 15px 20px; margin: 20px 0; border-radius: 4px;">
  <p style="margin: 0 0 10px 0; font-weight: bold; color: {{PRIMARY_COLOR}};">
    💡 温馨提示
  </p>
  <p style="margin: 0; color: #3f3f3f; font-size: 14px;">
    提示内容文字
  </p>
</div>
```

### 4. 数据展示

```html
<div style="display: flex; gap: 10px; margin: 25px 0; flex-wrap: wrap;">
  <div style="flex: 1; min-width: 100px; text-align: center; padding: 20px; background: {{ACCENT_COLOR}}; border-radius: 8px;">
    <div style="font-size: 28px; font-weight: bold; color: {{PRIMARY_COLOR}}; margin-bottom: 5px;">80%</div>
    <div style="font-size: 13px; color: #666;">用户满意度</div>
  </div>
  <div style="flex: 1; min-width: 100px; text-align: center; padding: 20px; background: {{ACCENT_COLOR}}; border-radius: 8px;">
    <div style="font-size: 28px; font-weight: bold; color: {{PRIMARY_COLOR}}; margin-bottom: 5px;">10万+</div>
    <div style="font-size: 13px; color: #666;">阅读量</div>
  </div>
</div>
```

### 5. 两栏布局

```html
<div style="display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap;">
  <div style="flex: 1; min-width: 200px; padding: 15px; background: #f8f8f8; border-radius: 8px;">
    <h3 style="margin: 0 0 10px 0; font-size: 16px; color: {{PRIMARY_COLOR}};">左侧标题</h3>
    <p style="margin: 0; font-size: 14px;">左侧内容</p>
  </div>
  <div style="flex: 1; min-width: 200px; padding: 15px; background: #f8f8f8; border-radius: 8px;">
    <h3 style="margin: 0 0 10px 0; font-size: 16px; color: {{PRIMARY_COLOR}};">右侧标题</h3>
    <p style="margin: 0; font-size: 14px;">右侧内容</p>
  </div>
</div>
```

### 6. 分隔线

```html
<div style="margin: 30px 0; text-align: center;">
  <div style="display: inline-block; width: 50px; height: 3px; background: {{PRIMARY_COLOR}};"></div>
</div>
```

### 7. 行动按钮

```html
<div style="text-align: center; margin: 30px 0;">
  <a href="[LINK_URL]" style="display: inline-block; padding: 12px 40px; background: {{PRIMARY_COLOR}}; color: white; text-decoration: none; border-radius: 25px; font-size: 15px; font-weight: bold; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
    点击查看更多
  </a>
</div>
```

### 8. 卡片样式

```html
<div style="background: white; border-radius: 12px; padding: 20px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
  <h3 style="margin: 0 0 15px 0; color: {{PRIMARY_COLOR}}; font-size: 17px;">卡片标题</h3>
  <p style="margin: 0; color: #3f3f3f; line-height: 1.75;">卡片内容</p>
</div>
```

## 常见错误避免

| 错误 | 说明 | 正确做法 |
|------|------|---------|
| 彩虹乱色 | 使用5+颜色破坏一致性 | 1主色+≤2辅助色 |
| 文字墙 | 无间距 = 瞬间疲劳 | 适当段落间距 |
| 强调过载 | 太多强调 = 无强调 | 每屏≤3处强调 |
| 风格不一 | 文章中途切换字体/颜色 | 保持全文一致 |
| 字号过大 | 18px+正文缺乏精致感 | 正文14-15px |
| 缺乏视觉断点 | 无图片或章节分隔 | 2-3张配图 |
| 正文居中 | 手机端难以阅读 | 正文两端对齐 |
| 忽略手机预览 | 发布前不检查 | 必须手机预览 |

## 质量检查三问

发布前问自己：

1. **读者能在3秒内找到重点吗？**
2. **手机屏幕上看会难受吗？**
3. **整体风格像一个人写的吗？**

**终极原则**：排版服务于读者，不是自我满足！

## 推荐排版工具

| 工具 | 特点 | 链接 |
|------|------|------|
| 135编辑器 | 全能冠军 | https://www.135editor.com/ |
| 秀米编辑器 | 清新风格 | https://xiumi.us/ |
| 96编辑器 | 免费福音 | https://bj.96weixin.com/ |
| i排版编辑器 | 黑科技玩家 | https://x.ipaiban.com/ |
| 一伴助手 | 微信后台"外挂" | https://yiban.io/ |
| 微信原生编辑器 | 极简选择 | https://mp.weixin.qq.com/ |

## 使用说明

1. 将 `{{PRIMARY_COLOR}}` 替换为主色调（如 #1E88E5）
2. 将 `{{ACCENT_COLOR}}` 替换为辅助色（如 #E3F2FD）
3. 将 `[IMAGE_URL]` 替换为实际图片链接
4. 复制 `<section>` 标签内的全部内容到微信编辑器
5. 在135编辑器或秀米中粘贴HTML代码
6. 替换图片占位符为实际图片
7. 手机预览后发布
