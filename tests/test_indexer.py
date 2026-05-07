import sys
import os

sys.path.append(os.path.abspath("src"))

from indexer import Indexer


def test_build_index():
    pages = {
        "page1": "hello world hello"
    }

    indexer = Indexer()

    indexer.build_index(pages)

    assert "hello" in indexer.index

    assert indexer.index["hello"]["page1"]["frequency"] == 2

def test_case_insensitive():

    pages = {
        "page1": "Hello hello HELLO"
    }

    indexer = Indexer()

    indexer.build_index(pages)

    assert indexer.index["hello"]["page1"]["frequency"] == 3 