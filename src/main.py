"""Command-line interface for the search engine tool."""

from __future__ import annotations

from pathlib import Path

from src.crawler import crawl_site
from src.indexer import INDEX_PATH, InvertedIndex, build_index, load_index, save_index
from src.search import find_pages, get_word_entries

COMMANDS_HELP = "Commands: build, load, print <word>, find <query>, help, exit"


def handle_command(
    command: str,
    index: InvertedIndex | None,
    index_path: str | Path = INDEX_PATH,
) -> tuple[InvertedIndex | None, bool, list[str]]:
    """Handle one shell command and return the updated state and output."""

    stripped_command = command.strip()
    if not stripped_command:
        return index, False, ["Please enter a command."]

    command_name, *parts = stripped_command.split(maxsplit=1)
    argument = parts[0] if parts else ""

    if command_name == "build":
        pages = crawl_site()
        new_index = build_index(pages)
        save_index(new_index, index_path)
        return (
            new_index,
            False,
            [
                f"Crawled {len(pages)} pages.",
                f"Built index with {len(new_index)} unique words.",
                f"Saved index to {index_path}.",
            ],
        )

    if command_name == "load":
        loaded_index = load_index(index_path)
        return loaded_index, False, [f"Loaded index with {len(loaded_index)} unique words."]

    if command_name == "print":
        return index, False, format_print_command(index, argument)

    if command_name == "find":
        return index, False, format_find_command(index, argument)

    if command_name == "help":
        return index, False, [COMMANDS_HELP]

    if command_name in {"exit", "quit"}:
        return index, True, ["Goodbye."]

    return index, False, [f"Unknown command: {command_name}", COMMANDS_HELP]


def format_print_command(index: InvertedIndex | None, word: str) -> list[str]:
    """Format output for the print command."""

    if index is None:
        return ["No index loaded. Run build or load first."]
    if not word.strip():
        return ["Usage: print <word>"]

    entries = get_word_entries(index, word)
    if not entries:
        return [f"No index entries found for '{word}'."]

    lines = [f"Inverted index for '{word.lower()}':"]
    for url, stats in sorted(entries.items()):
        lines.append(
            f"- {url} | title: {stats['title']} | "
            f"frequency: {stats['frequency']} | positions: {stats['positions']}"
        )

    return lines


def format_find_command(index: InvertedIndex | None, query: str) -> list[str]:
    """Format output for the find command."""

    if index is None:
        return ["No index loaded. Run build or load first."]
    if not query.strip():
        return ["Usage: find <query terms>"]

    results = find_pages(index, query)
    if not results:
        return [f"No pages found for '{query}'."]

    lines = [f"Found {len(results)} page(s) for '{query}':"]
    for result in results:
        lines.append(f"- {result.url} | title: {result.title} | score: {result.score}")

    return lines


def main() -> None:
    """Run the interactive command shell."""

    index: InvertedIndex | None = None
    should_exit = False

    print("COMP3011 Search Engine Tool")
    print(COMMANDS_HELP)

    while not should_exit:
        try:
            command = input("> ")
        except EOFError:
            break

        try:
            index, should_exit, lines = handle_command(command, index)
        except FileNotFoundError as exc:
            lines = [str(exc)]
        except Exception as exc:
            lines = [f"Error: {exc}"]

        for line in lines:
            print(line)


if __name__ == "__main__":
    main()
