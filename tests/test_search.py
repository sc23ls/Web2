from src.search import Search


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