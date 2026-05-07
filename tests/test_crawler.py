from src.crawler import Crawler


def test_crawl():
    crawler = Crawler()

    pages = crawler.crawl()

    assert len(pages) > 0