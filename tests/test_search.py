import math

from search import Search


def test_find_returns_tfidf_ranked_intersection_results_and_prints_summary(capsys):
    index = {
        "hello": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 3, "positions": [0, 2, 4]},
            "page3": {"frequency": 1, "positions": [0]},
        },
        "world": {
            "page1": {"frequency": 4, "positions": [1, 3, 5, 7]},
            "page2": {"frequency": 1, "positions": [1]},
        },
    }
    search = Search(index)

    results = search.find("hello world")

    hello_idf = math.log((3 + 1) / (3 + 1)) + 1
    world_idf = math.log((3 + 1) / (2 + 1)) + 1
    assert results == [
        ("page1", 1 * hello_idf + 4 * world_idf),
        ("page2", 3 * hello_idf + 1 * world_idf),
    ]
    output = capsys.readouterr().out
    assert "Query: 'hello world'" in output
    assert "Matching pages: 2" in output
    assert "page1 (score: 6.1507)" in output


def test_find_stems_query_terms_before_lookup():
    index = {
        "run": {
            "page1": {"frequency": 2, "positions": [0, 3]},
        }
    }
    search = Search(index)

    assert search.find("running") == [("page1", 2.0)]


def test_inverse_document_frequency_uses_smoothed_document_count():
    search = Search(
        {
            "common": {
                "page1": {"frequency": 1, "positions": [0]},
                "page2": {"frequency": 1, "positions": [0]},
            },
            "rare": {
                "page1": {"frequency": 1, "positions": [1]},
            },
        }
    )

    assert search.inverse_document_frequency("common") == math.log(3 / 3) + 1
    assert search.inverse_document_frequency("rare") == math.log(3 / 2) + 1


def test_tfidf_score_sums_each_query_terms_weighted_frequency():
    search = Search(
        {
            "common": {
                "page1": {"frequency": 3, "positions": [0, 2, 4]},
                "page2": {"frequency": 1, "positions": [0]},
            },
            "rare": {
                "page1": {"frequency": 2, "positions": [1, 3]},
            },
        }
    )

    expected = (
        3 * search.inverse_document_frequency("common")
        + 2 * search.inverse_document_frequency("rare")
    )
    assert search.tf_idf_score("page1", ["common", "rare"]) == expected


def test_find_returns_empty_list_when_any_word_is_missing(capsys):
    search = Search({"hello": {"page1": {"frequency": 1, "positions": [0]}}})

    results = search.find("hello missing")

    assert results == []
    assert "No results found." in capsys.readouterr().out


def test_find_returns_empty_list_when_terms_do_not_overlap(capsys):
    search = Search(
        {
            "hello": {"page1": {"frequency": 1, "positions": [0]}},
            "world": {"page2": {"frequency": 1, "positions": [0]}},
        }
    )

    results = search.find("hello world")

    assert results == []
    assert "No matching pages." in capsys.readouterr().out


def test_find_handles_empty_query(capsys):
    search = Search({"hello": {"page1": {"frequency": 1, "positions": [0]}}})

    results = search.find("")

    assert results == []
    assert "No results found." in capsys.readouterr().out


def test_print_word_reports_stemmed_postings(capsys):
    search = Search(
        {
            "run": {
                "page1": {"frequency": 2, "positions": [0, 2]},
                "page2": {"frequency": 1, "positions": [4]},
            }
        }
    )

    search.print_word("running")

    output = capsys.readouterr().out
    assert "Word: 'run'" in output
    assert "Appears on 2 pages." in output
    assert "Total occurrences across all pages: 3" in output


def test_print_word_reports_missing_terms(capsys):
    search = Search({})

    search.print_word("missing")

    assert "Word not found." in capsys.readouterr().out
