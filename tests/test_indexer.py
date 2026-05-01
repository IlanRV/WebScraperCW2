"""Tests for inverted index construction."""

from __future__ import annotations

import pytest

from src.crawler import CrawledPage
from src.indexer import build_index, load_index, save_index, tokenize


def test_tokenize_lowercases_words_and_removes_punctuation() -> None:
    words = tokenize('"Good friends", said Alice! Good.')

    assert words == ["good", "friends", "said", "alice", "good"]


def test_build_index_records_frequency_positions_and_title() -> None:
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/",
            title="Quotes to Scrape",
            text="Good friends are good",
        )
    ]

    index = build_index(pages)

    assert index["good"]["https://quotes.toscrape.com/"] == {
        "title": "Quotes to Scrape",
        "frequency": 2,
        "positions": [0, 3],
    }
    assert index["friends"]["https://quotes.toscrape.com/"]["frequency"] == 1


def test_build_index_tracks_the_same_word_across_multiple_pages() -> None:
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/",
            title="Page One",
            text="life is good",
        ),
        CrawledPage(
            url="https://quotes.toscrape.com/page/2/",
            title="Page Two",
            text="good choices",
        ),
    ]

    index = build_index(pages)

    assert set(index["good"]) == {
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    }


def test_save_and_load_index_round_trip(tmp_path) -> None:
    index = build_index(
        [
            CrawledPage(
                url="https://quotes.toscrape.com/",
                title="Quotes to Scrape",
                text="simple test simple",
            )
        ]
    )
    index_path = tmp_path / "index.json"

    save_index(index, index_path)
    loaded = load_index(index_path)

    assert loaded == index


def test_load_index_raises_for_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_index(tmp_path / "missing.json")
