# PDF内容提取工作流

## 使用场景
当用户提供PDF链接作为文章素材来源时（如行业报告、白皮书、学术论文、官方手册），需要先提取全文内容再进行写作。

## 提取步骤

### 1. 下载PDF
```bash
curl -L -o /tmp/source.pdf "PDF_URL"
```

### 2. 安装pymupdf（如未安装）
```bash
python3 -m pip install pymupdf
```

### 3. 提取全文
```python
import fitz
doc = fitz.open('/tmp/source.pdf')
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    print(f'=== PAGE {page_num+1} ===')
    print(text)
    print()
```

### 4. 保存到临时文件供后续使用
```bash
python3 -c "
import fitz
doc = fitz.open('/tmp/source.pdf')
with open('/tmp/source_text.md', 'w') as f:
    for i, page in enumerate(doc):
        f.write(f'=== PAGE {i+1} ===\n')
        f.write(page.get_text())
        f.write('\n\n')
" 
```

## 常见问题

### PDF是图片/扫描件
- pymupdf对纯图片PDF提取效果差
- 需要用OCR工具（如PaddleOCR skill）处理
- 先用pymupdf试提取，如果文字很少则判断为扫描件

### PDF过大（>100页）
- 分批提取，每次20页
- 或用`web_extract`工具直接提取摘要（如果只需要概要）

### PDF有密码保护
- pymupdf支持密码：`doc = fitz.open('/tmp/source.pdf')` + `doc.authenticate('password')`

## 与web_extract的配合
- `web_extract`对PDF支持有限，经常只能拿到摘要
- 对于需要全文的场景，**必须用pymupdf本地提取**
- 对于只需要概要的场景，可以先用`web_extract`快速获取

## 输出质量检查
- 提取后检查文字是否完整（对比PDF页数和提取内容）
- 检查是否有乱码（特别是中英文混排的PDF）
- 检查表格和图表是否能正确提取（通常表格需要手动整理）
