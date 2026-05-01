"""Crawler for the COMP3011 search engine coursework.

The crawler starts at the quotes website homepage, extracts the readable
quote/tag/author text from each page, follows the "next" pagination link,
and returns a list of crawled pages ready for indexing.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Callable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import Session

BASE_URL = "https://quotes.toscrape.com/"
POLITENESS_DELAY_SECONDS = 6
REQUEST_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class CrawledPage:
    """A web page captured by the crawler."""

    url: str
    title: str
    text: str


class CrawlError(RuntimeError):
    """Raised when the crawler cannot retrieve a page."""


def extract_page_text(html: str) -> str:
    """Extract searchable content from a quotes.toscrape.com HTML page."""

    soup = BeautifulSoup(html, "html.parser")
    parts: list[str] = []

    for quote in soup.select(".quote"):
        text = quote.select_one(".text")
        author = quote.select_one(".author")
        tags = quote.select(".tags .tag")

        if text is not None:
            parts.append(text.get_text(" ", strip=True))
        if author is not None:
            parts.append(author.get_text(" ", strip=True))
        parts.extend(tag.get_text(" ", strip=True) for tag in tags)

    return " ".join(parts)


def find_next_page_url(html: str, current_url: str) -> str | None:
    """Return the absolute URL for the next page, or None at the end."""

    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if next_link is None:
        return None

    href = next_link.get("href")
    if not href:
        return None

    return urljoin(current_url, href)


def fetch_page(session: Session, url: str) -> str:
    """Fetch a URL and return its HTML, raising CrawlError on failure."""

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CrawlError(f"Failed to fetch {url}: {exc}") from exc

    return response.text


def crawl_site(
    start_url: str = BASE_URL,
    politeness_delay: int = POLITENESS_DELAY_SECONDS,
    session: Session | None = None,
    sleeper: Callable[[float], None] = sleep,
) -> list[CrawledPage]:
    """Crawl the target website and return all discovered quote pages."""

    http = session or requests.Session()
    pages: list[CrawledPage] = []
    visited: set[str] = set()
    current_url: str | None = start_url

    while current_url is not None:
        if current_url in visited:
            break

        visited.add(current_url)
        html = fetch_page(http, current_url)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else current_url

        pages.append(
            CrawledPage(
                url=current_url,
                title=title,
                text=extract_page_text(html),
            )
        )

        next_url = find_next_page_url(html, current_url)
        if next_url is not None:
            sleeper(politeness_delay)

        current_url = next_url

    return pages
