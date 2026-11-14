# 超长图生成故障排除指南

## 常见问题与解决方案

### 1. API Key 相关问题

#### 症状：`Incorrect API key provided: dummy`
**原因**：`image_generate` 工具使用的是默认 dummy key，未正确配置
**解决**：
```bash
# 检查配置
grep -A 4 "image_gen:" ~/.hermes/config.yaml

# 确保 api_key 不为空
hermes config set image_gen.api_key "你的完整KEY"
```

#### 症状：`无效的令牌` (401)
**原因**：API Key 过期或被截断
**排查步骤**：
1. 检查 Key 长度：`grep "api_key:" ~/.hermes/config.yaml | wc -c`
2. 如果 < 20 字符，说明被截断
3. 手动编辑 config.yaml 填入完整 Key
4. 到 https://api.openlux.ai 确认 Key 状态

#### 症状：`该令牌无权访问模型` (403)
**原因**：API Key 没有目标模型权限
**解决**：
```bash
# 尝试其他模型
# 在脚本中修改 model 参数
data = {
    'model': 'gpt-image-1',  # 尝试其他模型
    'prompt': '...',
}
```

#### 症状：`您多次使用无效令牌` (429)
**原因**：短时间内多次失败触发限流
**解决**：
1. 等待 120 秒
2. 检查 Key 是否有效后再重试
3. 避免连续快速重试

### 2. 图片生成问题

#### 症状：生成的图片是空白/纯色
**原因**：使用了 PIL 占位图而非 AI 生成
**解决**：
- 使用 `generate_long_image.py` 而非 `render_lightweight.py`
- 确保 API Key 有效

#### 症状：超长图拼接有明显接缝
**原因**：重叠区域不足或裁剪不准确
**解决**：
```python
# 增加重叠区域
overlap = 200  # 从 100 增加到 200
```

#### 症状：图片内容与主题不符
**原因**：Prompt 不够具体
**解决**：
```python
# 更详细的 prompt
prompt = """
Create a professional infographic about AI Tools Guide.

Specific content to include:
- Section 1: Basic concepts with icons
- Section 2: Core skills with examples
- Section 3: Advanced techniques

Style: Dark tech theme, neon blue (#00D4FF) accents
Layout: Vertical, clear visual hierarchy
"""
```

### 3. 渲染脚本问题

#### 症状：`playwright` 未安装
**原因**：Playwright 浏览器未下载
**解决**：
```bash
# 安装 Playwright
pip install playwright
playwright install chromium

# 或使用轻量版脚本（无需 Playwright）
python3 scripts/render_lightweight.py --preset xiaohongshu
```

#### 症状：`ModuleNotFoundError: No module named 'yaml'`
**原因**：缺少 PyYAML 依赖
**解决**：
```bash
pip install pyyaml
```

### 4. 网络问题

#### 症状：`SSLError` 或连接超时
**原因**：网络代理或防火墙限制
**解决**：
```bash
# 设置代理
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897

# 或使用备用链路
export YUNWU_BASE_URL="https://api.openlux.ai/v1"
```

### 5. 文件权限问题

#### 症状：`Permission denied`
**原因**：脚本没有执行权限
**解决**：
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

## 调试技巧

### 1. 逐步测试
```bash
# 先测试 API 连接
python3 scripts/test_yunwu_api.py

# 再测试单张图片生成
python3 scripts/generate_long_image.py --prompt "test" --preset square --output /tmp/test.png

# 最后生成超长图
python3 scripts/generate_long_image.py --prompt "教程" --preset super_long_medium --output /tmp/long.png
```

### 2. 查看详细日志
在脚本中添加：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. 检查返回数据
```python
response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
```

## 联系支持

如果问题仍未解决：
1. 检查云雾 API 状态页：https://status.yunwu.ai
2. 查看 API 文档：https://api.openlux.ai/docs
3. 联系云雾 API 客服
4. 在 GitHub 提交 Issue：https://github.com/BetterZflyee/ai-ggbond-skills/issues
