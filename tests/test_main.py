"""Tests for command-line command handling."""

from __future__ import annotations

from pathlib import Path

import src.main as main_module
from src.crawler import CrawledPage
from src.indexer import InvertedIndex, load_index
from src.main import handle_command


INDEX: InvertedIndex = {
    "good": {
        "https://quotes.toscrape.com/": {
            "title": "Page One",
            "frequency": 2,
            "positions": [0, 2],
        }
    },
    "friends": {
        "https://quotes.toscrape.com/": {
            "title": "Page One",
            "frequency": 1,
            "positions": [1],
        }
    },
}


def test_handle_build_crawls_builds_saves_and_updates_index(
    monkeypatch,
    tmp_path: Path,
) -> None:
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/",
            title="Quotes to Scrape",
            text="Good friends good",
        )
    ]
    monkeypatch.setattr(main_module, "crawl_site", lambda: pages)
    index_path = tmp_path / "index.json"

    index, should_exit, lines = handle_command("build", None, index_path)

    assert should_exit is False
    assert index is not None
    assert index["good"]["https://quotes.toscrape.com/"]["frequency"] == 2
    assert load_index(index_path) == index
    assert lines == [
        "Crawled 1 pages.",
        "Built index with 2 unique words.",
        f"Saved index to {index_path}.",
    ]


def test_handle_load_loads_saved_index(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    main_module.save_index(INDEX, index_path)

    index, should_exit, lines = handle_command("load", None, index_path)

    assert should_exit is False
    assert index == INDEX
    assert lines == ["Loaded index with 2 unique words."]


def test_handle_print_requires_loaded_index() -> None:
    index, should_exit, lines = handle_command("print good", None)

    assert index is None
    assert should_exit is False
    assert lines == ["No index loaded. Run build or load first."]


def test_handle_print_outputs_word_entries() -> None:
    index, should_exit, lines = handle_command("print good", INDEX)

    assert index == INDEX
    assert should_exit is False
    assert lines == [
        "Inverted index for 'good':",
        "- https://quotes.toscrape.com/ | title: Page One | "
        "frequency: 2 | positions: [0, 2]",
    ]


def test_handle_find_outputs_matching_pages() -> None:
    _index, should_exit, lines = handle_command("find good friends", INDEX)

    assert should_exit is False
    assert lines == [
        "Found 1 page(s) for 'good friends':",
        "- https://quotes.toscrape.com/ | title: Page One | score: 3",
    ]


def test_handle_empty_find_query_returns_usage() -> None:
    _index, should_exit, lines = handle_command("find", INDEX)

    assert should_exit is False
    assert lines == ["Usage: find <query terms>"]


def test_handle_unknown_command_returns_help() -> None:
    _index, should_exit, lines = handle_command("dance", INDEX)

    assert should_exit is False
    assert lines[0] == "Unknown command: dance"


def test_handle_exit_sets_exit_flag() -> None:
    index, should_exit, lines = handle_command("exit", INDEX)

    assert index == INDEX
    assert should_exit is True
    assert lines == ["Goodbye."]
