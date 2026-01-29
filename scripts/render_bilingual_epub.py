#!/usr/bin/env python3
import argparse
import html
from pathlib import Path

from ebooklib import epub


CSS = """
.pair {
  margin: 0.3em 0;
}
.en {
  font-size: 0.9em;
  line-height: 1.2;
}
.zh {
  font-size: 1.05em;
  line-height: 1.45;
  margin-top: 0.05em;
}
"""


def load_pairs(aligned_tsv: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in aligned_tsv.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            raise ValueError(
                f"Expected tab-separated aligned pairs, got: {line!r}"
            )
        en = parts[0].strip()
        zh = parts[1].strip()
        pairs.append((en, zh))
    return pairs


def build_xhtml(pairs: list[tuple[str, str]], lang_en: str, lang_zh: str) -> str:
    body_lines = [
        '<section class="bilingual">'
    ]
    for en, zh in pairs:
        body_lines.append('<div class="pair">')
        body_lines.append(f'<div class="en" lang="{lang_en}">{html.escape(en)}</div>')
        body_lines.append(f'<div class="zh" lang="{lang_zh}">{html.escape(zh)}</div>')
        body_lines.append("</div>")
    body_lines.append("</section>")

    return """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{lang_en}">
<head>
  <meta charset="utf-8" />
  <title>Bilingual Text</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
""".format(lang_en=lang_en) + "\n".join(body_lines) + "\n</body>\n</html>\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render aligned sentence pairs into a reflowable EPUB3."
    )
    parser.add_argument("--aligned", required=True, type=Path, help="TSV with EN\tZH per line")
    parser.add_argument("--out", required=True, type=Path, help="Output EPUB path")
    parser.add_argument("--title", default="Bilingual Edition", help="EPUB title")
    parser.add_argument("--author", default="", help="EPUB author")
    parser.add_argument("--lang-en", default="en", help="Language code for English text")
    parser.add_argument("--lang-zh", default="zh", help="Language code for Chinese text")
    args = parser.parse_args()

    pairs = load_pairs(args.aligned)
    book = epub.EpubBook()
    book.set_title(args.title)
    book.set_language(args.lang_en)
    if args.author:
        book.add_author(args.author)

    style = epub.EpubItem(uid="style", file_name="style.css", media_type="text/css", content=CSS)
    book.add_item(style)

    chapter = epub.EpubHtml(title="Bilingual", file_name="bilingual.xhtml", lang=args.lang_en)
    chapter.set_content(build_xhtml(pairs, args.lang_en, args.lang_zh))
    book.add_item(chapter)

    book.toc = (epub.Link("bilingual.xhtml", "Bilingual", "bilingual"),)
    book.spine = ["nav", chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(str(args.out), book)


if __name__ == "__main__":
    main()
