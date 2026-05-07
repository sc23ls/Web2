import sys
import os

sys.path.append(os.path.abspath("src"))

from crawler import Crawler


def test_crawl():
    crawler = Crawler()

    pages = crawler.crawl()

    assert len(pages) > 0