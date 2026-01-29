# Bilingual EPUB Pipeline (Lingtrain → EPUB)

This repo contains a minimal, runnable pipeline that follows the final spec:

- **Sentence-level alignment** using Lingtrain (semantic alignment).
- **Vertical bilingual rendering** with English on top and Chinese below.
- **Reflowable EPUB3** output without forced line breaks or punctuation edits.

## Quick Start

### 1) Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Prepare sentences for alignment

```bash
python scripts/prepare_for_alignment.py \
  --en path/to/english.epub \
  --zh path/to/chinese.epub \
  --out work/
```

This generates:

- `work/en.sentences.txt`
- `work/zh.sentences.txt`
- `work/metadata.json`

If your EPUB uses `<div>` wrappers without `<p>` tags, add `--include-divs` to include those nodes.

### 3) Align with Lingtrain

Use Lingtrain Aligner to create a tab-separated alignment file:

```
<english sentence>\t<chinese sentence>
```

Save the aligned output as `work/aligned.tsv`.

### 4) Render bilingual EPUB

```bash
python scripts/render_bilingual_epub.py \
  --aligned work/aligned.tsv \
  --out output/bilingual.epub \
  --title "Your Book Title" \
  --author "Author Name" \
  --lang-en en \
  --lang-zh zh
```

The EPUB will contain vertical bilingual pairs:

```html
<div class="pair">
  <div class="en">English sentence…</div>
  <div class="zh">中文句子……</div>
</div>
```

## Batch Processing Structure

Recommended folder layout for multiple books:

```
books/
  book-001/
    input/
      en.epub
      zh.epub
    work/
      en.sentences.txt
      zh.sentences.txt
      aligned.tsv
    output/
      bilingual.epub
  book-002/
    ...
```

## Notes

- The scripts avoid splitting punctuation or forcing line breaks.
- Sentence splitting is heuristic; Lingtrain alignment handles semantic pairing.
- If you already have aligned sentence pairs, you can skip step 2.

## Quick Smoke Test (No EPUB Needed)

You can render the sample pairs in `examples/aligned.tsv`:

```bash
python scripts/render_bilingual_epub.py \
  --aligned examples/aligned.tsv \
  --out output/sample.epub \
  --title "Sample Bilingual"
```
