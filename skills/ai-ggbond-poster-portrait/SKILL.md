---
name: ai-ggbond-poster-portrait
description: GPT Image 2女性肖像海报生成系统。生成具有摄影感、电影感、情绪感的高质量女性肖像海报，同时避免安全审核问题。支持云雾API直接对接。
triggers:
  - 肖像海报
  - 女性写真
  - CCD风格
  - 摄影感海报
  - 电影感人像
  - 情绪感写真
  - GPT Image 2 肖像
  - 街拍风格
version: 2.1.0
author: ai-ggbond
---

# GPT Image 2 女性肖像海报生成系统

## 核心理念
生成具有摄影感、电影感、情绪感的高质量女性肖像海报，同时避免GPT Image 2的安全审核问题。支持云雾API直接对接，确保图像生成稳定可靠。

## 云雾API配置（首次使用必读）

### 配置加载优先级

配置按以下优先级加载（高优先级覆盖低优先级）：

| 优先级 | 来源 | 路径 | 说明 |
|--------|------|------|------|
| 1 | 环境变量 | `os.environ` | 系统环境变量 |
| 2 | 项目级配置 | `./.ai-ggbond-skills/.env` | 当前项目目录 |
| 3 | 用户级配置 | `~/.ai-ggbond-skills/.env` | 用户主目录 |

### 首次使用配置

**方式一：手动创建配置文件（推荐）**

```bash
# 用户级配置（推荐，所有项目共享）
mkdir -p ~/.ai-ggbond-skills
cat > ~/.ai-ggbond-skills/.env << 'EOF'
YUNWU_API_KEY=sk-8lcvuMcVjtK1RkRpa640NLTzCmg9uIZtqFnviqTOIBwKxstB
YUNWU_BASE_URL=https://api.openlux.ai
YUNWU_DEFAULT_MODEL=gpt-image-2
EOF
```

**⚠️ Hermes HOME路径陷阱**：Hermes terminal中 `$HOME` 和 `~` 展开为 `/Users/admin/.hermes/profiles/gongcheng/home`（非 `/Users/admin`）。配置文件实际创建在 `~/.ai-ggbond-skills/.env` = `/Users/admin/.hermes/profiles/gongcheng/home/.ai-ggbond-skills/.env`。skills目录在 `/Users/admin/.hermes/skills/`（symlink）。

### 可选配置项

```bash
# 多链路配置（自动切换，应对429负载饱和）
YUNWU_BASE_URLS=https://api.openlux.ai,https://api.openlux.ai,https://api.openlux.ai

# 图片生成端点（默认：/v1/images/generations）
YUNWU_IMAGE_ENDPOINT=/v1/images/generations

# 重试策略
YUNWU_MAX_RETRIES=3
YUNWU_RETRY_DELAY=8

# 图片间隔（秒，避免连续请求触发429）
YUNWU_IMAGE_INTERVAL=20

# 超时时间（秒）
YUNWU_IMAGE_TIMEOUT=300

# 代理策略（默认尊重系统代理，设置1禁用）
YUNWU_DISABLE_PROXY=0
```

## 输入参数模板
```
摄影风格：{摄影风格}
写真方向：{写真方向}
场景方向：{场景方向}
服装方向：{服装方向}
气质标签：{气质标签}
五官方向：{五官方向}
身形方向：{身形方向}
线条强调：{线条强调}
镜头方向：{镜头方向}
姿态动作：{姿态动作}
光线氛围：{光线氛围}
滤镜效果：{滤镜效果}
画幅比例：{画幅比例}
补充要求：{补充要求}
```

## 摄影风格示例

### 1. 柔光CCD风
- 特点：复古数码质感、柔光、轻颗粒、轻数码噪点
- 适用：情绪感、故事感、安静疏离的氛围
- 示例参数：
  ```
  摄影风格：柔光CCD风
  滤镜效果：夜色柔光CCD色彩 + 奶白高光 + 轻颗粒 + 轻数码噪点
  ```

### 2. 胶片风
- 特点：颗粒感、色彩偏移、复古质感
- 适用：文艺、怀旧、温暖的氛围
- 示例参数：
  ```
  摄影风格：日系胶片风
  滤镜效果：暖色调胶片质感 + 自然颗粒 + 色彩偏移
  ```

### 3. 商业写真风
- 特点：高清晰度、精致光线、商业质感
- 适用：品牌、时尚、高级感
- 示例参数：
  ```
  摄影风格：商业写真风
  滤镜效果：高清商业质感 + 精致光线 + 干净背景
  ```

## 场景方向示例

### 1. 夜晚街头写真
- 场景：城市街道、霓虹灯、路灯、雨夜
- 氛围：都市感、情绪化、电影感
- 示例：
  ```
  场景方向：雨夜车内副驾驶 / 车窗旁
  光线氛围：雨夜路灯反射 + 车内冷暖混合柔闪
  ```

### 2. 咖啡馆写真
- 场景：咖啡馆角落、窗边、书架旁
- 氛围：安静、文艺、温暖
- 示例：
  ```
  场景方向：咖啡馆窗边座位
  光线氛围：午后自然光 + 室内暖光
  ```

### 3. 天台写真
- 场景：城市天台、日落、天空
- 氛围：自由、开阔、青春
- 示例：
  ```
  场景方向：城市天台 / 日落时分
  光线氛围：黄金时刻自然光 + 城市背景虚化
  ```

## 服装方向示例

### 1. 休闲时尚
```
服装方向：深灰色修身上衣 + 宽松外套半披 + 高腰短裙
```

### 2. 文艺清新
```
服装方向：白色棉麻衬衫 + 浅色牛仔裤 + 帆布鞋
```

### 3. 都市轻熟
```
服装方向：黑色针织衫 + 高腰阔腿裤 + 高跟鞋
```

## 气质标签示例

### 安静疏离型
```
气质标签：安静、疏离、情绪感、克制、有故事感
```

### 温暖治愈型
```
气质标签：温暖、治愈、亲切、自然、有亲和力
```

### 时尚高级型
```
气质标签：时尚、高级、冷艳、自信、有气场
```

## 五官方向示例

### 清冷淡颜
```
五官方向：清冷淡颜
```

### 温柔暖颜
```
五官方向：温柔暖颜
```

### 混血高级颜
```
五官方向：混血高级颜
```

## 镜头方向示例

### 半身到大腿
```
镜头方向：半身到大腿
```

### 全身
```
镜头方向：全身
```

### 特写
```
镜头方向：面部特写
```

## 完整提示词示例

### 示例1：雨夜CCD风格
```
摄影风格：柔光CCD风
写真方向：夜晚街头写真
场景方向：雨夜车内副驾驶 / 车窗旁
服装方向：深灰色修身上衣 + 宽松外套半披 + 高腰短裙
气质标签：安静、疏离、情绪感、克制、有故事感
五官方向：清冷淡颜
身形方向：匀称柔美
线条强调：中
镜头方向：半身到大腿
姿态动作：靠近车窗坐姿，身体轻微侧向镜头，一只手自然搭在腿边
光线氛围：雨夜路灯反射 + 车内冷暖混合柔闪
滤镜效果：夜色柔光CCD色彩 + 奶白高光 + 轻颗粒 + 轻数码噪点
画幅比例：9:16
补充要求：像雨夜车内被CCD相机随手拍下的一帧，安静、情绪化、电影感强
```

### 示例2：午后咖啡馆
```
摄影风格：日系胶片风
写真方向：室内写真
场景方向：咖啡馆窗边座位
服装方向：白色棉麻衬衫 + 浅色A字裙
气质标签：安静、文艺、温柔、自然、有书卷气
五官方向：温柔暖颜
身形方向：纤细修长
线条强调：低
镜头方向：半身
姿态动作：坐在窗边，手捧咖啡杯，微微低头微笑
光线氛围：午后自然光从窗户洒入 + 室内暖光
滤镜效果：暖色调胶片质感 + 自然颗粒 + 轻微光晕
画幅比例：4:5
补充要求：像午后咖啡馆里被胶片相机记录的一刻，温暖、治愈、有生活气息
```

### 示例3：天台日落
```
摄影风格：商业写真风
写真方向：户外写真
场景方向：城市天台 / 日落时分
服装方向：黑色吊带裙 + 高跟鞋
气质标签：时尚、高级、自信、有气场、女神感
五官方向：混血高级颜
身形方向：高挑匀称
线条强调：高
镜头方向：全身
姿态动作：站在天台边缘，风吹动头发，身体微微后仰
光线氛围：黄金时刻自然光 + 城市背景虚化
滤镜效果：高清商业质感 + 暖色调 + 精致光影
画幅比例：16:9
补充要求：像时尚杂志的封面大片，高级、大气、有视觉冲击力
```

## 安全审核避坑指南

### 🟢 安全词汇（推荐使用）
```
adult female character, mature temperament, refined feminine beauty,
gentle confidence, elegant composure, natural smile,
healthy fullness, rounded and balanced figure, natural curves,
soft S-shaped posture, relaxed shoulders and neck,
high-fashion feeling, commercial portrait, brand lookbook,
fashion editorial, clean soft light, tasteful clothing,
character art design
```

### 🔴 危险词汇（避免使用）
```
temptation, provocation, seducing, nipples, nudity,
breast close-up, hip close-up, cleavage, private parts,
wet-body temptation, clothes slipping off, vulgar pose,
adult photoshoot, borderline adult content, fetish styling,
minor-looking girl, lolita, childlike but sexy
```

### 常见错误与修正

#### 1. 年龄不明确
- ❌ `girl, lolita, childlike, cute and sexy`
- ✅ `20-year-old woman, adult female character, mature natural face shape`

#### 2. 强调身体部位
- ❌ `emphasize the chest/hips, very large chest, close-up of body parts`
- ✅ `healthy full upper body, natural rounded chest outline, balanced overall figure`

#### 3. 挑逗姿势
- ❌ `provocative pose, lying face down, teasing movement, low-angle upward shot`
- ✅ `natural standing pose, upright seated pose, slight side turn, calm elegant posture`

#### 4. 私密场景
- ❌ `sexy photoshoot on a bed, wet body in bathroom, dim ambiguous room`
- ✅ `bright indoor space, soft bedroom-like scene, premium home interior`

#### 5. 暴露服装
- ❌ `revealing, extremely short, low-cut, transparent, clothes about to slip off`
- ✅ `elegant tailoring, soft material, fitted silhouette, tasteful and refined`

#### 6. 泳装场景
- ❌ `sexy swimsuit beauty, hot body, wet body, low angle`
- ✅ `high-end swimwear brand lookbook, adult female model, healthy and confident`

#### 7. 回眸姿势
- ❌ `sexy looking back, emphasize the hips, low angle`
- ✅ `body turns slightly, head looks back naturally, shoulders and neck relaxed`

#### 8. S型曲线
- ❌ `emphasize S-curve, large chest, tiny waist, lifted hips`
- ✅ `natural soft S-shaped dynamic posture; shoulders, waist, hips create smooth visual rhythm`

## 提示词改写公式

### 原始想法
"我想生成一个性感、有魅力的女性角色，身材很吸引人。"

### 错误写法
```
sexy beautiful woman, hot body, large chest, lifted hips, seductive eyes, low-angle shot
```

### 安全改写
```
A 20-year-old adult female character with a fresh, elegant temperament, a healthy full figure, and naturally flowing body curves. Her posture is open and relaxed, the shoulder and neck lines are soft, the upper body is naturally full, and the waist is gently defined. The image uses a high-fashion magazine portrait style, soft light, a clean background, and restrained composition.
```

## 使用流程

1. **确定摄影风格**：根据想要的氛围选择摄影风格
2. **选择场景**：根据摄影风格匹配合适的场景
3. **设计服装**：根据场景和气质选择服装
4. **定义气质**：明确想要表达的气质标签
5. **设置参数**：填写五官、身形、镜头等参数
6. **添加光线滤镜**：根据氛围设置光线和滤镜
7. **审核安全词汇**：检查是否包含危险词汇
8. **生成海报**：使用云雾API生成图像

## 图像生成（云雾API对接）

### 方式一：直接API调用（推荐）

```python
import os, base64, time, requests
from pathlib import Path

def load_yunwu_config():
    """加载云雾API配置"""
    config = {
        "api_key": os.environ.get("YUNWU_API_KEY", ""),
        "base_url": os.environ.get("YUNWU_BASE_URL", "https://api.openlux.ai"),
        "base_urls": os.environ.get("YUNWU_BASE_URLS", "https://api.openlux.ai,https://api.openlux.ai,https://api.openlux.ai"),
        "endpoint": os.environ.get("YUNWU_IMAGE_ENDPOINT", "/v1/images/generations"),
        "model": os.environ.get("YUNWU_DEFAULT_MODEL", "gpt-image-2"),
        "max_retries": int(os.environ.get("YUNWU_MAX_RETRIES", "3")),
        "retry_delay": int(os.environ.get("YUNWU_RETRY_DELAY", "8")),
        "timeout": int(os.environ.get("YUNWU_IMAGE_TIMEOUT", "300")),
    }
    
    # 从配置文件读取（如果环境变量为空）
    if not config["api_key"]:
        config_paths = [
            Path("./.ai-ggbond-skills/.env"),
            Path("~/.ai-ggbond-skills/.env").expanduser(),
        ]
        for config_path in config_paths:
            if config_path.exists():
                for line in config_path.read_text().splitlines():
                    if line.startswith("YUNWU_API_KEY="):
                        config["api_key"] = line.split("=", 1)[1].strip()
                        break
                if config["api_key"]:
                    break
    
    # 解析多链路
    config["base_url_list"] = [u.strip() for u in config["base_urls"].split(",") if u.strip()]
    
    return config

def generate_portrait(prompt, output_path, ratio="9:16", model=None):
    """
    生成肖像海报
    
    Args:
        prompt: 完整的提示词
        output_path: 输出图片路径
        ratio: 画幅比例 (9:16, 16:9, 1:1, 4:5)
        model: 模型名称（可选，默认使用配置）
    
    Returns:
        bool: 是否成功
    """
    config = load_yunwu_config()
    
    if not config["api_key"]:
        print("❌ 错误：未配置YUNWU_API_KEY")
        print("请创建配置文件 ~/.ai-ggbond-skills/.env 并添加：")
        print("YUNWU_API_KEY=sk-your-api-key")
        return False
    
    # 根据比例设置尺寸
    size_map = {
        "9:16": "1024x1792",
        "16:9": "1792x1024",
        "1:1": "1024x1024",
        "4:5": "1024x1280",
    }
    size = size_map.get(ratio, "1024x1792")
    
    # 使用指定模型或默认模型
    use_model = model or config["model"]
    
    # 构建请求数据
    data = {
        "model": use_model,
        "prompt": prompt,
        "n": 1,
        "size": size,
    }
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }
    
    # 尝试所有链路
    for base_url in config["base_url_list"]:
        endpoint = f"{base_url}{config['endpoint']}"
        print(f"🔄 尝试链路: {base_url}")
        
        for attempt in range(config["max_retries"]):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=data,
                    timeout=config["timeout"]
                )
                
                if response.status_code == 200:
                    result = response.json()
                    img_data = result["data"][0]
                    
                    # 保存图片
                    if "b64_json" in img_data:
                        img_bytes = base64.b64decode(img_data["b64_json"])
                        with open(output_path, "wb") as f:
                            f.write(img_bytes)
                    elif "url" in img_data:
                        img_response = requests.get(img_data["url"], timeout=60)
                        with open(output_path, "wb") as f:
                            f.write(img_response.content)
                    
                    print(f"✅ 图片已保存: {output_path}")
                    return True
                    
                elif response.status_code == 429:
                    print(f"⚠️ 链路负载饱和 (429)，等待 {config['retry_delay'] * (attempt + 1)} 秒后重试...")
                    time.sleep(config["retry_delay"] * (attempt + 1))
                    continue
                    
                else:
                    print(f"❌ 请求失败: {response.status_code} - {response.text[:200]}")
                    break
                    
            except requests.exceptions.Timeout:
                print(f"⏰ 请求超时，重试 {attempt + 1}/{config['max_retries']}")
                time.sleep(config["retry_delay"])
                continue
                
            except Exception as e:
                print(f"❌ 请求异常: {e}")
                break
    
    print("❌ 所有链路均失败")
    return False

# 使用示例
if __name__ == "__main__":
    # 构建提示词
    prompt = """A 22-year-old adult female character with a petite and delicate build, youthful appearance, and gentle sweet temperament. She is sitting on a comfortable sofa in a cozy living room, looking directly at the camera with a soft natural smile. 

Photography style: Soft CCD aesthetic with vintage digital texture
Scene: Living room sofa with warm home interior
Clothing: Cream-colored knit sweater paired with casual shorts, comfortable and relaxed styling
Temperament: Gentle, sweet, approachable, warm, and friendly
Facial features: Soft rounded face with delicate features, natural makeup
Body type: Petite and slender, balanced proportions
Camera angle: Half-body to thigh shot
Pose: Sitting naturally on the sofa, body slightly turned toward the camera, hands resting comfortably on her lap
Lighting: Soft indoor natural light mixed with warm ambient lighting, gentle shadows
Filter effect: CCD color palette with creamy highlights, light film grain, subtle digital noise

The image should look like a casual CCD camera snapshot taken at home, warm and intimate, with a nostalgic digital aesthetic. Soft focus, gentle colors, and a cozy atmosphere."""
    
    # 生成图片
    output_path = "portrait_ccd_style.png"
    success = generate_portrait(prompt, output_path, ratio="9:16")
    
    if success:
        print("🎉 生成完成！")
    else:
        print("💥 生成失败，请检查配置和网络")
```

### 方式二：使用脚本生成

将上述代码保存为 `generate_portrait.py`，然后运行：

```bash
python3 generate_portrait.py
```

## 画幅比例与尺寸对照表

| 比例 | 尺寸 | 适用场景 |
|------|------|----------|
| 9:16 | 1024x1792 | 竖版海报、手机壁纸、小红书 |
| 16:9 | 1792x1024 | 横版海报、桌面壁纸、公众号封面 |
| 1:1 | 1024x1024 | 正方形、朋友圈、头像 |
| 4:5 | 1024x1280 | 竖版、Instagram |

## 模型选择建议

| 模型 | 特点 | 推荐场景 |
|------|------|----------|
| gpt-image-2 | 默认推荐，稳定性好 | 大多数场景 |
| gpt-image-1 | 上一代，更稳定 | 敏感内容、政治时事 |
| gemini-2.5-flash-image | 速度快 | 快速预览 |
| dall-e-3 | 英文渲染好 | 英文内容 |
| qwen-image-edit-2509 | 中文优化 | 中文文字为主 |

## 错误处理与重试策略

### 429 负载饱和
- **表现**：`"当前分组上游负载已饱和"`
- **处理**：自动切换下一条链路，按指数退避等待

### 500 敏感词
- **表现**：`"sensitive words detected"`
- **处理**：调整提示词，用职位代替人名，或改用英文

### 超时
- **表现**：连接超时 >180s
- **处理**：检查网络，增加timeout，或简化提示词

### API密钥错误
- **表现**：`"Incorrect API key provided: dummy"`
- **处理**：检查配置文件，确保YUNWU_API_KEY正确

## Pitfalls

- **Codex CLI/Desktop 不是图片生成工具**：用户说"用 Codex 生成图片"时，需要澄清 Codex 是代码工具，无法调用 GPT Image 2。详见 `references/openai-codex-ecosystem.md`。
- **ChatGPT Plus ≠ OpenAI API**：Plus 订阅是网页消费级产品，不提供 API 额度。两者账户独立，需要在 platform.openai.com 单独注册和充值。
- **云雾 API 余额不足**：报错 `insuffi` 开头时，需充值。当前价格约 $0.004/张。
- **429 负载饱和**：多链路自动切换 + 指数退避等待
- **500 敏感词**：调整提示词，用职位代替人名，或改用英文
- **超时**：检查网络，增加 timeout，或简化提示词

## 最终目标

生成具有以下特点的女性肖像海报：
- 摄影感强，像真实相机拍摄
- 情绪化，有故事感
- 电影感强，适合社交平台传播
- 高级感，不低俗
- 符合安全审核要求

## 参考文件
- `references/ccd-style-examples.md` — CCD风格提示词库、中英术语映射、场景/姿态/光线/滤镜模板
- `references/yunwu-api-integration.md` — 云雾API集成指南、配置说明、错误处理、脚本使用
- `references/openai-codex-ecosystem.md` — OpenAI Codex 工具生态调研：Codex Desktop/CLI/API 区别，为什么 Codex 不能生成图片

## 参考来源
基于@liyue_ai的GPT Image 2女性肖像提示词安全指南。
基于ai-ggbond-sticker-writer的云雾API对接方案。