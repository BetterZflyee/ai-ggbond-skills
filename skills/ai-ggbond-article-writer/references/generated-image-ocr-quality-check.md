# Generated Image OCR Quality Check with PaddleOCR

## Trigger
Use this after generating公众号文章配图、封面图、信息图、微信贴图，尤其是含中文标题、标签、流程节点、代码片段或数据的小字图片。

## Why
Vision review tools can fail or miss text defects. In one session, `vision_analyze` returned HTTP 502 while generated images existed and were usable. PaddleOCR successfully extracted text from all 7 generated images and exposed Chinese text defects that visual preview could miss.

## Preferred Workflow
1. Generate images with the confirmed model, usually `gpt-image-2`; do not switch models without user confirmation.
2. Run PaddleOCR on every generated image before declaring the set ready.
3. Compare OCR output against the intended text labels.
4. Classify each image:
   - **Keep**: headline/key labels correct; only harmless decorative symbols appear.
   - **Keep but optional optimize**: main headline correct but tiny incidental text has small errors.
   - **Regenerate**: core title, section label, framework node, architecture label, or visible sentence has wrong Chinese/乱码/错字.
5. Prefer single-image regeneration over full batch regeneration.
6. When regenerating, reduce text density: keep 3–5 large labels, avoid code snippets and dense dashboards unless absolutely necessary.

## Command Pattern
Run from the PaddleOCR text-recognition skill root:

```bash
cd /Users/admin/.hermes/skills/paddleocr-text-recognition
for f in /path/to/article/images/*.png; do
  echo "=== $(basename "$f") ==="
  uv run scripts/ocr_caller.py --file-path "$f" --stdout --pretty \
    | python -c 'import sys,json; d=json.load(sys.stdin); print("OK=", d.get("ok")); print(d.get("text") or "[NO TEXT]"); err=d.get("error");
if err: print("ERROR=", err)'
done
```

If the shell security scanner warns about piping `uv` output to `python`, either request approval or save JSON files first and parse them in a separate step.

## Example Findings from 7-Image Article Batch
- `cover.png`: main title correct, but tiny code text had defects such as `代码朴全建议` and `Noe` instead of `None`; acceptable only if tiny text is not visible in cover usage.
- `infographic.png`: mostly good; minor OCR issue `Al` vs `AI`.
- `03-copilot-vs-agent.png`: regenerate because OCR found corrupted visible text like `部署预恰遇过`.
- `04-agent-runtime-architecture.png`: regenerate because architecture labels had defects like `远行状态` instead of `运行状态`.

## Practical Rule
For公众号配图，文字正确性 beats decorative richness. The more tiny text in an AI-generated image, the higher the error probability. Use OCR as a gate before publishing.

## gpt-image-2 Chinese Character Dropping & Spacing Fix

### Symptom
gpt-image-2 occasionally drops or tangles individual Chinese characters, especially in short, dense titles. Example: "不是作弊" rendered as "不是作" (missing "弊").

### Root Cause
gpt-image-2 struggles with tightly-packed Chinese characters in decorative/title contexts. Without explicit spacing, adjacent characters can merge or drop during rendering.

### Fix: Add Character Spacing to Prompt
When generating Chinese title text, explicitly request spacing between characters:

```
标题：不是作弊 四个汉字 每个字之间有明显间距 字体清晰无重叠无变形
```

This may cause the title to split into two lines ("不是" / "作弊") — this is acceptable as long as all characters are present and legible.

### Regeneration Workflow
When OCR reveals a dropped character in a title/label:
1. Do NOT re-run the same prompt (will likely produce same defect)
2. Add spacing instructions to the prompt: `每个字之间有明显间距 字体清晰无重叠无变形`
3. Add `无重影` to the negative constraints
4. Regenerate and re-OCR to verify all characters present
5. Accept two-line rendering if all characters are correct
