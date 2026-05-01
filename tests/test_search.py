"""Tests for search behaviour."""

from __future__ import annotations

from src.indexer import InvertedIndex
from src.search import SearchResult, find_pages, get_word_entries


INDEX: InvertedIndex = {
    "good": {
        "https://quotes.toscrape.com/": {
            "title": "Page One",
            "frequency": 2,
            "positions": [0, 4],
        },
        "https://quotes.toscrape.com/page/2/": {
            "title": "Page Two",
            "frequency": 1,
            "positions": [3],
        },
    },
    "friends": {
        "https://quotes.toscrape.com/": {
            "title": "Page One",
            "frequency": 1,
            "positions": [1],
        },
    },
    "life": {
        "https://quotes.toscrape.com/page/2/": {
            "title": "Page Two",
            "frequency": 3,
            "positions": [0, 6, 9],
        },
    },
}


def test_get_word_entries_is_case_insensitive() -> None:
    entries = get_word_entries(INDEX, "GOOD")

    assert set(entries) == {
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    }


def test_get_word_entries_returns_empty_dict_for_punctuation_only() -> None:
    assert get_word_entries(INDEX, "!!!") == {}


def test_find_pages_returns_single_word_results_ranked_by_frequency() -> None:
    results = find_pages(INDEX, "good")

    assert results == [
        SearchResult(
            url="https://quotes.toscrape.com/",
            title="Page One",
            score=2,
            matched_words=["good"],
        ),
        SearchResult(
            url="https://quotes.toscrape.com/page/2/",
            title="Page Two",
            score=1,
            matched_words=["good"],
        ),
    ]


def test_find_pages_requires_all_words_in_multi_word_query() -> None:
    results = find_pages(INDEX, "good friends")

    assert results == [
        SearchResult(
            url="https://quotes.toscrape.com/",
            title="Page One",
            score=3,
            matched_words=["good", "friends"],
        )
    ]


def test_find_pages_returns_empty_list_for_missing_word() -> None:
    assert find_pages(INDEX, "good unknown") == []


def test_find_pages_returns_empty_list_for_empty_query() -> None:
    assert find_pages(INDEX, "   ") == []
