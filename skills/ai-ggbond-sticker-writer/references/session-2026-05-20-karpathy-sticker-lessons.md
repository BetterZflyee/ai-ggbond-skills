# 2026-05-20 Karpathy 微信贴图生成经验

## 触发场景
用户围绕 X 新闻“Karpathy 加入 Anthropic”要求生成微信贴图，并继续要求人物档案信息图。

## 用户纠偏
1. **严禁用本地 PIL/占位图冒充生图结果**
   - 当云雾/gpt-image-2 429 或超时时，不要用 PIL 本地拼图作为替代成品。
   - 用户明确反馈：“很丑，严格用 gpt-image-2”。
   - 正确做法：说明当前生图失败/超时，等待用户授权重试；若用户要求生成，必须严格指定 `--model gpt-image-2`。

2. **人物档案必须高信息密度且源头准确**
   - 用户指出 Karpathy 人物介绍“内容太简陋，信息度要高”。
   - 随后提供官网 https://karpathy.ai/ 并质疑“我们说的是同一个人吗？”
   - 正确做法：人物档案类贴图优先抓取官网/一手资料，再补权威媒体；不要把新闻线（如 Anthropic 入职）喧宾夺主。

3. **官网档案要体现原始自述和真实履历**
   - Karpathy 官网关键自述：`I like to train deep neural nets on large datasets 🧠🤖💥`
   - 官网履历重点：
     - 2024-：AI 教育视频 / YouTube，技术向 Zero to Hero 与大众向 LLM 内容
     - 2023-2024：回 OpenAI，组建 midtraining 与 synthetic data generation 团队
     - 2017-2022：Tesla AI Director，领导 Autopilot Vision，短暂参与 Optimus；负责数据标注、神经网络训练、自研推理芯片部署
     - 2015-2017：OpenAI research scientist / founding member
     - 2011-2015：Stanford PhD，导师 Fei-Fei Li；CS231n 主讲，课程人数 150→330→750
     - 2009-2011：UBC MSc，physically-simulated figures 控制器学习
     - 2005-2009：University of Toronto，CS + Physics 双专业，Math 辅修；接触 Geoff Hinton 课程与 reading group
   - 代表项目/内容：micrograd、char-rnn、arxiv-sanity、neuraltalk2、ConvNetJS、Software 2.0、A Recipe for Training Neural Networks、The Unreasonable Effectiveness of RNN。

## 生图执行经验
- 严格模型命令示例：
```bash
python ~/.hermes/skills/creative/ai-ggbond-sticker-writer/scripts/generate_sticker_images_v2.py \
  --markdown "/tmp/karpathy_official_profile_high_density.md" \
  --style high-density \
  --ratio 16:9 \
  --model gpt-image-2 \
  --max-images 1 \
  --image-interval 60 \
  --output-dir "/Users/admin/SuperIp/stickers/.../images" \
  --watermark "AI朱朱侠"
```
- 终端/execute_code 可能 300 秒超时，但图片可能已成功落盘；超时后应立即 `search_files` 或 `ls` 检查 output-dir，而不是直接判断失败。
- 生成失败或 429 时，不得擅自换模型；用户已强调模型选择原则。

## 输出质量规则
- 如果用户要“人物档案”，不要只写标签；至少包含：一句话定位、时间线、代表作品、教育/工程/研究影响、资料来源。
- 信息图宜用 high-density 或 folder 风格；人物档案更适合分多张图（履历时间线 / 代表作品 / 核心影响），避免一张图文字过密。
