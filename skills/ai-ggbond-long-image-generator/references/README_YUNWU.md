# 云雾 API 配置与超长图生成指南

## 📁 文件说明

| 文件 | 用途 |
|------|------|
| `setup_yunwu.sh` | API Key 配置脚本 |
| `test_yunwu_api.py` | API 连接测试 |
| `generate_long_image.py` | 超长图生成器 |

---

## 🚀 快速开始

### Step 1: 配置 API Key

```bash
# 方法 1: 使用脚本配置（推荐）
bash /tmp/setup_yunwu.sh 你的完整API_KEY

# 方法 2: 手动编辑配置文件
nano ~/.hermes/config.yaml
# 找到 image_gen 部分，修改 api_key
```

### Step 2: 测试 API 连接

```bash
python3 /tmp/test_yunwu_api.py
```

期望输出：
```
✅ API 连接成功!
✅ 测试图片已保存: /tmp/api_test_success.png
```

### Step 3: 生成超长图

```bash
# 生成小红书竖图
python3 /tmp/generate_long_image.py --prompt "AI工具使用指南" --preset xiaohongshu --output /tmp/test.png

# 生成超长图（4倍高度）
python3 /tmp/generate_long_image.py --prompt "完整教程" --preset super_long_medium --output /tmp/long.png

# 自定义尺寸
python3 /tmp/generate_long_image.py --prompt "内容" --width 1080 --height 5400 --output /tmp/custom.png
```

---

## 📐 可用预设

| 预设 | 尺寸 | 说明 |
|------|------|------|
| `xiaohongshu` | 1080×1440 | 小红书竖图 |
| `xiaohongshu_long` | 1080×2400 | 小红书长图 |
| `super_long_small` | 1080×3200 | 超长图-小号 |
| `super_long_medium` | 1080×4320 | 超长图-中号 |
| `super_long_large` | 1080×5400 | 超长图-大号 |
| `super_long_extreme` | 1080×7200 | 超长图-极限 |

---

## ❓ 常见问题

### Q: API Key 无效怎么办？
A: 到 https://yunwu.ai 重新生成 API Key

### Q: 图片生成失败？
A: 检查 API 余额是否充足，模型是否有权限

### Q: 超长图拼接有接缝？
A: 调整 `overlap` 参数（默认 100px）

---

## 🔗 相关资源

- 云雾 API: https://yunwu.ai
- AI朱朱侠长图生成 Skill: ~/.hermes/profiles/gongcheng/skills/creative/ai-ggbond-long-image-generator
