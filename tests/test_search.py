from search import Search


def test_find_returns_ranked_intersection_results_and_prints_summary(capsys):
    index = {
        "hello": {
            "page1": {"frequency": 1, "positions": [0]},
            "page2": {"frequency": 3, "positions": [0, 2, 4]},
        },
        "world": {
            "page1": {"frequency": 4, "positions": [1, 3, 5, 7]},
            "page2": {"frequency": 1, "positions": [1]},
        },
    }
    search = Search(index)

    results = search.find("hello world")

    assert results == [("page1", 5), ("page2", 4)]
    output = capsys.readouterr().out
    assert "Query: 'hello world'" in output
    assert "Matching pages: 2" in output
    assert "page1 (score: 5)" in output


def test_find_stems_query_terms_before_lookup():
    index = {
        "run": {
            "page1": {"frequency": 2, "positions": [0, 3]},
        }
    }
    search = Search(index)

    assert search.find("running") == [("page1", 2)]


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
