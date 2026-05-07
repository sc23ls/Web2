import json

import pytest

from indexer import Indexer, IndexPersistenceError


def test_build_index_tracks_frequency_positions_and_multiple_pages():
    pages = {
        "page1": "hello world hello",
        "page2": "world hello",
    }
    indexer = Indexer()

    indexer.build_index(pages)

    assert indexer.index["hello"]["page1"] == {
        "frequency": 2,
        "positions": [0, 2],
    }
    assert indexer.index["hello"]["page2"] == {
        "frequency": 1,
        "positions": [1],
    }
    assert indexer.index["world"]["page1"]["positions"] == [1]


def test_build_index_is_case_insensitive_and_strips_punctuation():
    pages = {"page1": "Hello, hello! HELLO? world-class"}
    indexer = Indexer()

    indexer.build_index(pages)

    assert indexer.index["hello"]["page1"]["frequency"] == 3
    assert indexer.index["world"]["page1"]["positions"] == [3]
    assert indexer.index["class"]["page1"]["positions"] == [4]


def test_build_index_stems_related_words_to_same_term():
    pages = {"page1": "running runs runner"}
    indexer = Indexer()

    indexer.build_index(pages)

    assert indexer.index["run"]["page1"] == {
        "frequency": 2,
        "positions": [0, 1],
    }
    assert indexer.index["runner"]["page1"] == {
        "frequency": 1,
        "positions": [2],
    }


def test_build_index_accumulates_when_called_multiple_times():
    indexer = Indexer()

    indexer.build_index({"page1": "alpha"})
    indexer.build_index({"page2": "alpha beta"})

    assert set(indexer.index["alpha"]) == {"page1", "page2"}
    assert indexer.index["beta"]["page2"]["frequency"] == 1


def test_save_and_load_index_round_trip(tmp_path):
    index_file = tmp_path / "index.json"
    indexer = Indexer()
    indexer.build_index({"page1": "hello hello"})

    indexer.save_index(index_file)

    assert json.loads(index_file.read_text()) == indexer.index

    loaded = Indexer()
    result = loaded.load_index(index_file)

    assert result == indexer.index
    assert loaded.index == indexer.index


def test_load_index_reports_missing_file(tmp_path):
    indexer = Indexer()

    with pytest.raises(IndexPersistenceError, match="Index file not found"):
        indexer.load_index(tmp_path / "missing.json")


def test_load_index_reports_invalid_json(tmp_path):
    index_file = tmp_path / "index.json"
    index_file.write_text("{not json")
    indexer = Indexer()

    with pytest.raises(IndexPersistenceError, match="not valid JSON"):
        indexer.load_index(index_file)


def test_load_index_rejects_invalid_index_shape(tmp_path):
    index_file = tmp_path / "index.json"
    index_file.write_text(json.dumps({"hello": {"page1": {"frequency": "many"}}}))
    indexer = Indexer()

    with pytest.raises(IndexPersistenceError, match="Posting stats"):
        indexer.load_index(index_file)
