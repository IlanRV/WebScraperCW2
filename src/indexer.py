"""Inverted index construction and persistence."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.crawler import CrawledPage

INDEX_PATH = Path("data/index.json")
WORD_PATTERN = re.compile(r"[a-zA-Z0-9]+(?:'[a-zA-Z0-9]+)?")

type PageStats = dict[str, int | list[int] | str]
type InvertedIndex = dict[str, dict[str, PageStats]]


def tokenize(text: str) -> list[str]:
    """Split text into lowercase searchable words."""

    return [match.group(0).lower() for match in WORD_PATTERN.finditer(text)]


def add_page_to_index(index: InvertedIndex, page: CrawledPage) -> None:
    """Add one crawled page to an inverted index."""

    for position, word in enumerate(tokenize(page.text)):
        page_entries = index.setdefault(word, {})
        stats = page_entries.setdefault(
            page.url,
            {
                "title": page.title,
                "frequency": 0,
                "positions": [],
            },
        )

        stats["frequency"] = int(stats["frequency"]) + 1
        positions = stats["positions"]
        if isinstance(positions, list):
            positions.append(position)


def build_index(pages: list[CrawledPage]) -> InvertedIndex:
    """Build an inverted index from crawled pages."""

    index: InvertedIndex = {}

    for page in pages:
        add_page_to_index(index, page)

    return index


def save_index(index: InvertedIndex, path: str | Path = INDEX_PATH) -> None:
    """Save an inverted index as readable JSON."""

    index_path = Path(path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


def load_index(path: str | Path = INDEX_PATH) -> InvertedIndex:
    """Load an inverted index from JSON."""

    index_path = Path(path)
    if not index_path.exists():
        raise FileNotFoundError(f"Index file not found: {index_path}")

    data: Any = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Index file is invalid: expected a JSON object")

    return data
