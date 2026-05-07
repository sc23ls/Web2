from unittest.mock import Mock
import requests

from crawler import Crawler, format_elapsed_time


class FakeResponse:
    def __init__(self, text, status_error=None):
        self.text = text
        self.status_error = status_error

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error


class FakeSession:
    def __init__(self, pages):
        self.pages = pages
        self.requests = []

    def get(self, url, timeout):
        self.requests.append((url, timeout))
        response = self.pages[url]
        if isinstance(response, Exception):
            raise response
        return response


def quote_page(*, quote="Be yourself.", author="Oscar Wilde", links=""):
    return f"""
    <html>
      <body>
        <div class="quote">
          <span class="text">{quote}</span>
          <small class="author">{author}</small>
          <a class="tag">inspirational</a>
          <a class="tag">life</a>
        </div>
        {links}
      </body>
    </html>
    """


def test_crawl_extracts_quote_author_tags_and_author_details():
    session = FakeSession(
        {
            "https://example.test": FakeResponse(
                quote_page()
                + """
                <div class="author-details">
                  <span class="author-born-date">October 16, 1854</span>
                  <span class="author-description">Irish poet and playwright.</span>
                </div>
                """
            )
        }
    )
    crawler = Crawler(base_url="https://example.test/", session=session, delay=0)

    pages = crawler.crawl()

    assert pages == {
        "https://example.test": (
            "Be yourself. Oscar Wilde inspirational life "
            "October 16, 1854 Irish poet and playwright."
        )
    }
    assert session.requests == [("https://example.test", 10)]


def test_crawl_follows_internal_links_once_and_ignores_external_fragment_and_duplicates():
    session = FakeSession(
        {
            "https://example.test": FakeResponse(
                quote_page(
                    links="""
                    <a href="/page/2/">Next</a>
                    <a href="https://other.test/page">External</a>
                    <a href="/page/2">Duplicate without slash</a>
                    <a href="/tags#popular">Fragment</a>
                    """
                )
            ),
            "https://example.test/page/2": FakeResponse(
                quote_page(quote="Second page.", author="Jane Austen")
            ),
        }
    )
    crawler = Crawler(base_url="https://example.test", session=session, delay=0)

    pages = crawler.crawl()

    assert list(pages) == ["https://example.test", "https://example.test/page/2"]
    assert session.requests == [
        ("https://example.test", 10),
        ("https://example.test/page/2", 10),
    ]


def test_crawl_respects_max_pages_limit():
    session = FakeSession(
        {
            "https://example.test": FakeResponse(
                quote_page(links='<a href="/page/2/">Next</a>')
            ),
            "https://example.test/page/2": FakeResponse(quote_page(quote="Second page.")),
        }
    )
    crawler = Crawler(
        base_url="https://example.test",
        session=session,
        delay=0,
        max_pages=1,
    )

    pages = crawler.crawl()

    assert list(pages) == ["https://example.test"]
    assert session.requests == [("https://example.test", 10)]


def test_crawl_logs_request_errors_and_continues_without_raising(capsys):
    session = FakeSession(
        {
            "https://example.test": requests.Timeout("request timed out"),
        }
    )
    crawler = Crawler(base_url="https://example.test", session=session, delay=0)

    pages = crawler.crawl()

    assert pages == {}
    output = capsys.readouterr().out
    assert "HTTP error crawling https://example.test: request timed out" in output


def test_crawl_uses_configured_delay(monkeypatch):
    sleep = Mock()
    monkeypatch.setattr("crawler.time.sleep", sleep)
    session = FakeSession({"https://example.test": FakeResponse(quote_page())})
    crawler = Crawler(base_url="https://example.test", session=session, delay=0.25)

    crawler.crawl()

    sleep.assert_called_once_with(0.25)


def test_crawl_prints_elapsed_time_summary(monkeypatch, capsys):
    monkeypatch.setattr("crawler.time.perf_counter", Mock(side_effect=[10, 1330]))
    session = FakeSession({"https://example.test": FakeResponse(quote_page())})
    crawler = Crawler(base_url="https://example.test", session=session, delay=0)

    crawler.crawl()

    output = capsys.readouterr().out
    assert "CRAWLING COMPLETE" in output
    assert "1 pages crawled in 22 minutes" in output


def test_format_elapsed_time_handles_seconds_minutes_and_hours():
    assert format_elapsed_time(1) == "1 second"
    assert format_elapsed_time(62) == "1 minute 2 seconds"
    assert format_elapsed_time(7320) == "2 hours 2 minutes"


def test_crawl_propagates_malformed_quote_markup_as_logged_error(capsys):
    session = FakeSession(
        {
            "https://example.test": FakeResponse(
                '<div class="quote"><small class="author">Missing text span</small></div>'
            )
        }
    )
    crawler = Crawler(base_url="https://example.test", session=session, delay=0)

    pages = crawler.crawl()

    assert pages == {}
    assert "Parse error crawling https://example.test:" in capsys.readouterr().out
