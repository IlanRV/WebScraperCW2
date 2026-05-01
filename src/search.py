"""Search helpers for querying the inverted index."""

from __future__ import annotations

from dataclasses import dataclass

from src.indexer import InvertedIndex, PageStats, tokenize


@dataclass(frozen=True)
class SearchResult:
    """A page that matches a search query."""

    url: str
    title: str
    score: int
    matched_words: list[str]


def get_word_entries(index: InvertedIndex, word: str) -> dict[str, PageStats]:
    """Return index entries for a single word, ignoring case."""

    words = tokenize(word)
    if not words:
        return {}

    return index.get(words[0], {})


def find_pages(index: InvertedIndex, query: str) -> list[SearchResult]:
    """Find pages containing every word in a query."""

    query_words = tokenize(query)
    if not query_words:
        return []

    entries_by_word = [index.get(word, {}) for word in query_words]
    if any(not entries for entries in entries_by_word):
        return []

    matching_urls = set(entries_by_word[0])
    for entries in entries_by_word[1:]:
        matching_urls.intersection_update(entries)

    results = [
        build_search_result(url, query_words, entries_by_word)
        for url in matching_urls
    ]

    return sorted(results, key=lambda result: (-result.score, result.url))


def build_search_result(
    url: str,
    query_words: list[str],
    entries_by_word: list[dict[str, PageStats]],
) -> SearchResult:
    """Create a SearchResult by combining word statistics for one URL."""

    score = 0
    title = url

    for entries in entries_by_word:
        stats = entries[url]
        score += int(stats["frequency"])
        stored_title = stats.get("title")
        if isinstance(stored_title, str):
            title = stored_title

    return SearchResult(
        url=url,
        title=title,
        score=score,
        matched_words=query_words,
    )
