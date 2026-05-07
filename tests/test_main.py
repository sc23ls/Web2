import builtins

import main


class FakeCrawler:
    def __init__(self):
        self.pages = {"page1": "hello world"}

    def crawl(self):
        return self.pages


class FakeIndexer:
    instances = []

    def __init__(self):
        self.index = {"hello": {"page1": {"frequency": 1, "positions": [0]}}}
        self.built_pages = None
        self.saved = False
        self.loaded = False
        FakeIndexer.instances.append(self)

    def build_index(self, pages):
        self.built_pages = pages

    def save_index(self):
        self.saved = True

    def load_index(self):
        self.loaded = True


class FakeSearch:
    instances = []

    def __init__(self, index):
        self.index = index
        self.printed_words = []
        self.queries = []
        FakeSearch.instances.append(self)

    def print_word(self, word):
        self.printed_words.append(word)

    def find(self, query):
        self.queries.append(query)


def run_main_with_commands(monkeypatch, commands):
    inputs = iter(commands)
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    monkeypatch.setattr(main, "Crawler", FakeCrawler)
    monkeypatch.setattr(main, "Indexer", FakeIndexer)
    monkeypatch.setattr(main, "Search", FakeSearch)
    FakeIndexer.instances = []
    FakeSearch.instances = []

    main.main()


def test_main_builds_and_saves_index(monkeypatch, capsys):
    run_main_with_commands(monkeypatch, ["build", "exit"])

    indexer = FakeIndexer.instances[0]
    assert indexer.built_pages == {"page1": "hello world"}
    assert indexer.saved is True
    assert "Index built and saved." in capsys.readouterr().out


def test_main_loads_index_then_prints_and_finds(monkeypatch, capsys):
    run_main_with_commands(monkeypatch, ["load", "print hello", "find hello world", "exit"])

    indexer = FakeIndexer.instances[0]
    assert indexer.loaded is True
    assert FakeSearch.instances[0].printed_words == ["hello"]
    assert FakeSearch.instances[1].queries == ["hello world"]
    assert "Index loaded." in capsys.readouterr().out


def test_main_requires_loaded_index_for_search_commands(monkeypatch, capsys):
    run_main_with_commands(monkeypatch, ["print hello", "find hello", "exit"])

    assert FakeSearch.instances == []
    assert capsys.readouterr().out.count("Please load the index first.") == 2


def test_main_reports_unknown_command(monkeypatch, capsys):
    run_main_with_commands(monkeypatch, ["wat", "exit"])

    assert "Unknown command." in capsys.readouterr().out
