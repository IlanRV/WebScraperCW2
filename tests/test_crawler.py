"""Tests for crawler behaviour."""

from __future__ import annotations

from src.crawler import CrawledPage, crawl_site, extract_page_text, find_next_page_url


PAGE_ONE = """
<html>
  <head><title>Quotes to Scrape</title></head>
  <body>
    <div class="quote">
      <span class="text">"The world as we have created it."</span>
      <small class="author">Albert Einstein</small>
      <div class="tags">
        <a class="tag">change</a>
        <a class="tag">world</a>
      </div>
    </div>
    <li class="next"><a href="/page/2/">Next</a></li>
  </body>
</html>
"""

PAGE_TWO = """
<html>
  <head><title>Quotes Page 2</title></head>
  <body>
    <div class="quote">
      <span class="text">"It is our choices that show what we truly are."</span>
      <small class="author">J.K. Rowling</small>
      <div class="tags">
        <a class="tag">choices</a>
      </div>
    </div>
  </body>
</html>
"""


class FakeResponse:
    """Small stand-in for requests.Response used by the crawler tests."""

    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    """Session that returns predefined HTML pages by URL."""

    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages
        self.requested_urls: list[str] = []

    def get(self, url: str, timeout: int) -> FakeResponse:
        self.requested_urls.append(url)
        return FakeResponse(self.pages[url])


def test_extract_page_text_includes_quote_author_and_tags() -> None:
    text = extract_page_text(PAGE_ONE)

    assert "The world as we have created it." in text
    assert "Albert Einstein" in text
    assert "change" in text
    assert "world" in text


def test_find_next_page_url_returns_absolute_url() -> None:
    next_url = find_next_page_url(PAGE_ONE, "https://quotes.toscrape.com/")

    assert next_url == "https://quotes.toscrape.com/page/2/"


def test_find_next_page_url_returns_none_without_next_link() -> None:
    next_url = find_next_page_url(PAGE_TWO, "https://quotes.toscrape.com/page/2/")

    assert next_url is None


def test_crawl_site_follows_pagination_and_waits_between_pages() -> None:
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": PAGE_ONE,
            "https://quotes.toscrape.com/page/2/": PAGE_TWO,
        }
    )
    delays: list[float] = []

    pages = crawl_site(
        session=session,
        sleeper=delays.append,
    )

    assert pages == [
        CrawledPage(
            url="https://quotes.toscrape.com/",
            title="Quotes to Scrape",
            text='"The world as we have created it." Albert Einstein change world',
        ),
        CrawledPage(
            url="https://quotes.toscrape.com/page/2/",
            title="Quotes Page 2",
            text='"It is our choices that show what we truly are." J.K. Rowling choices',
        ),
    ]
    assert session.requested_urls == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert delays == [6]
