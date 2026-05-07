import sys
import os

sys.path.append(os.path.abspath("src"))

from crawler import Crawler


def test_crawl():
    crawler = Crawler()

    pages = crawler.crawl()

    assert len(pages) > 0

def test_pages_are_strings():

    crawler = Crawler()

    pages = crawler.crawl()

    for text in pages.values():
        assert isinstance(text, str)