#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from ebooklib import epub


def extract_text(epub_path: Path, include_divs: bool) -> list[str]:
    book = epub.read_epub(str(epub_path))
    texts: list[str] = []
    tags = ["p", "li", "h1", "h2", "h3", "h4", "h5", "h6"]
    if include_divs:
        tags.append("div")
    for item in book.get_items_of_type(epub.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        for element in soup.find_all(tags):
            if element.name == "div" and element.find(["p", "li"]):
                continue
            text = " ".join(element.stripped_strings)
            if text:
                texts.append(text)
    return texts


def split_english(paragraphs: list[str]) -> list[str]:
    sentences: list[str] = []
    splitter = re.compile(r"(?<=[.!?])\s+")
    for paragraph in paragraphs:
        for sentence in splitter.split(paragraph):
            cleaned = sentence.strip()
            if cleaned:
                sentences.append(cleaned)
    return sentences


def split_chinese(paragraphs: list[str]) -> list[str]:
    sentences: list[str] = []
    splitter = re.compile(r"(?<=[。！？])")
    for paragraph in paragraphs:
        for sentence in splitter.split(paragraph):
            cleaned = sentence.strip()
            if cleaned:
                sentences.append(cleaned)
    return sentences


def write_lines(lines: list[str], path: Path) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract sentences from English and Chinese EPUBs for Lingtrain alignment."
    )
    parser.add_argument("--en", required=True, type=Path, help="Path to English EPUB")
    parser.add_argument("--zh", required=True, type=Path, help="Path to Chinese EPUB")
    parser.add_argument("--out", required=True, type=Path, help="Output directory")
    parser.add_argument(
        "--include-divs",
        action="store_true",
        help="Also extract text from <div> elements (off by default to avoid duplicates).",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    en_paragraphs = extract_text(args.en, args.include_divs)
    zh_paragraphs = extract_text(args.zh, args.include_divs)

    en_sentences = split_english(en_paragraphs)
    zh_sentences = split_chinese(zh_paragraphs)

    write_lines(en_sentences, args.out / "en.sentences.txt")
    write_lines(zh_sentences, args.out / "zh.sentences.txt")

    metadata = {
        "english_epub": str(args.en),
        "chinese_epub": str(args.zh),
        "include_divs": args.include_divs,
        "english_sentence_count": len(en_sentences),
        "chinese_sentence_count": len(zh_sentences),
    }
    (args.out / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
