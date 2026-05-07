from src.indexer import Indexer


def test_build_index():
    pages = {
        "page1": "hello world hello"
    }

    indexer = Indexer()

    indexer.build_index(pages)

    assert "hello" in indexer.index

    assert indexer.index["hello"]["page1"]["frequency"] == 2