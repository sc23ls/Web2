import sys
import os

sys.path.append(os.path.abspath("src"))

from search import Search


def test_find():
    index = {
        "hello": {
            "page1": {
                "frequency": 1,
                "positions": [0]
            }
        }
    }

    search = Search(index)

    assert "hello" in search.index

def test_missing_word():

    index = {}

    search = Search(index)

    assert "missing" not in search.index