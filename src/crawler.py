"""Web crawler for collecting quote pages into plain searchable text.

The crawler is intentionally small, but it is structured for testability:
HTTP access, crawl delay, base URL, and page limits can all be injected from
tests or benchmarks.
"""

from collections import deque
import time
from typing import Any, Protocol
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class CrawlerError(Exception):
    """Base class for crawler-specific failures."""


class CrawlerParseError(CrawlerError):
    """Raised when a page is missing expected quote markup."""


class HttpSession(Protocol):
    """Minimal HTTP interface required by :class:`Crawler`."""

    def get(self, url: str, timeout: int) -> Any:
        ...


def format_elapsed_time(seconds: float) -> str:
    """Format elapsed seconds as a compact human-readable duration.

    Examples:
        ``62`` becomes ``"1 minute 2 seconds"`` and ``3600`` becomes
        ``"1 hour"``.
    """

    seconds = int(round(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts: list[str] = []

    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")

    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if seconds or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return " ".join(parts)


class Crawler:
    """Breadth-first crawler scoped to a single base URL.

    Args:
        base_url: Root URL for the crawl. Links outside this root are ignored.
        session: HTTP client compatible with ``requests.get``. Supplying this
            makes tests deterministic and avoids live-network dependencies.
        delay: Seconds to sleep after each successful page fetch.
        max_pages: Optional hard limit on successfully visited pages.
    """

    def __init__(
        self,
        base_url: str = "https://quotes.toscrape.com",
        session: HttpSession | None = None,
        delay: float = 1,
        max_pages: int | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests
        self.delay = delay
        self.max_pages = max_pages

    @staticmethod
    def _required_text(element: Any, description: str) -> str:
        """Return text from a required BeautifulSoup element.

        Raises:
            CrawlerParseError: If the element is missing from the page.
        """

        if element is None:
            raise CrawlerParseError(f"Missing {description}.")

        return element.get_text()

    def _extract_page_text(self, soup: BeautifulSoup) -> str:
        """Extract searchable text from a parsed quote page."""

        page_text = ""

        for quote in soup.find_all("div", class_="quote"):
            quote_text = self._required_text(
                quote.find("span", class_="text"),
                "quote text",
            )
            author = self._required_text(
                quote.find("small", class_="author"),
                "quote author",
            )
            tags = quote.find_all("a", class_="tag")
            tag_text = " ".join(tag.get_text() for tag in tags)
            page_text += f"{quote_text} {author} {tag_text} "

        author_details = soup.find("div", class_="author-details")

        if author_details:
            page_text += author_details.get_text(separator=" ", strip=True)

        return page_text

    def _should_queue_url(
        self,
        url: str,
        visited_urls: set[str],
        queued_urls: set[str],
    ) -> bool:
        """Return whether a discovered URL should be added to the frontier."""

        return (
            url.startswith(self.base_url)
            and "#" not in url
            and url not in visited_urls
            and url not in queued_urls
        )

    def _discover_links(
        self,
        soup: BeautifulSoup,
        visited_urls: set[str],
        queued_urls: set[str],
    ) -> list[str]:
        """Return crawlable links discovered in a parsed page."""

        discovered_links: list[str] = []

        for link in soup.find_all("a"):
            href = link.get("href")

            if not href:
                continue

            full_url = urljoin(self.base_url, href).rstrip("/")

            if self._should_queue_url(full_url, visited_urls, queued_urls):
                discovered_links.append(full_url)

        return discovered_links

    def crawl(self) -> dict[str, str]:
        """Crawl pages and return a mapping of URL to extracted text.

        The crawler extracts quote text, author names, tags, and author-detail
        text from pages matching the structure of ``quotes.toscrape.com``. HTTP
        and parsing errors are logged and skipped so one failed page does not
        abort the whole crawl.
        """

        start_time = time.perf_counter()

        urls_to_visit: deque[str] = deque([self.base_url])
        queued_urls = {self.base_url}
        visited_urls: set[str] = set()

        pages: dict[str, str] = {}

        while urls_to_visit:
            if self.max_pages is not None and len(visited_urls) >= self.max_pages:
                break

            current_url = urls_to_visit.popleft()
            queued_urls.discard(current_url)

            if current_url in visited_urls:
                continue

            print(f"Crawling: {current_url}")

            print(f"Queue size: {len(urls_to_visit)}")
            print(f"Visited pages: {len(visited_urls)}")

            try:
                response = self.session.get(current_url, timeout=10)

                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                pages[current_url] = self._extract_page_text(soup)

                visited_urls.add(current_url)

                for full_url in self._discover_links(soup, visited_urls, queued_urls):
                    urls_to_visit.append(full_url)
                    queued_urls.add(full_url)

                if self.delay:
                    time.sleep(self.delay)

            except requests.RequestException as error:
                print(f"HTTP error crawling {current_url}: {error}")
            except CrawlerParseError as error:
                print(f"Parse error crawling {current_url}: {error}")
            except Exception as error:
                print(f"Unexpected error crawling {current_url}: {error}")

        elapsed_time = format_elapsed_time(time.perf_counter() - start_time)

        print("\nCRAWLING COMPLETE")
        print(f"{len(visited_urls)} pages crawled in {elapsed_time}")

        return pages
