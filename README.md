# Web Crawler Search Engine

A small, testable Python search engine that crawls
[`quotes.toscrape.com`](https://quotes.toscrape.com), builds an inverted index,
and supports ranked search with TF-IDF, Boolean queries, phrase matching,
autocomplete, and spelling suggestions.

The project is designed as a compact information-retrieval system rather than a
single script: crawler, indexer, search, tests, benchmarks, and documentation are
kept separate and covered by automated checks.

## Features

- Breadth-first crawler scoped to a configured base URL
- URL de-duplication for visited and queued pages
- Human-readable crawl timing summary
- Inverted index with term frequency and token positions
- TF-IDF ranked search results
- Stop-word filtering and stemming
- Quoted phrase search using positional indexes
- Boolean query processing with `AND`, `OR`, and `NOT`
- Autocomplete from indexed vocabulary
- Spelling suggestions for misspelled query terms
- Deterministic test suite with mocked crawler responses
- GitHub Actions CI with coverage enforcement
- Benchmark runner and Big-O complexity documentation

## Project Structure

```text
.
├── benchmarks/
│   └── benchmark_search.py
├── data/
│   └── index.json
├── docs/
│   ├── complexity.md
│   └── testing_strategy.md
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── main.py
│   └── search.py
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   ├── test_main.py
│   └── test_search.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Installation

Requirements:

- Python 3.10+
- `pip`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Quick Start

Run the interactive command-line application:

```bash
python src/main.py
```

Available commands:

```text
build             Crawl pages, build the index, and save it to data/index.json
load              Load the saved index
print <word>      Show index statistics for one word
find <query>      Search the loaded index
exit              Quit the prompt
```

Example session:

```text
> build
CRAWLING COMPLETE
215 pages crawled in 22 minutes
Indexed 4574 unique words.
Index built and saved.

> load
Index loaded.

> find life AND wisdom
Found in pages:
https://quotes.toscrape.com/page/1 (score: 4.2187)
```

## Query Examples

Plain multi-word queries require all terms to appear:

```text
life wisdom
```

Phrase queries require adjacent terms in the indexed positions:

```text
"oscar wilde"
```

Boolean queries support `AND`, `OR`, and `NOT`:

```text
life AND wisdom
life OR humor
life AND NOT death
"oscar wilde" OR wisdom
```

Autocomplete and suggestions are available through the `Search` class:

```python
from search import Search

search = Search(index)
search.autocomplete("insp")
search.suggest_corrections("philosofy")
```

## Architecture

The system has three main runtime components:

- `Crawler`: fetches pages, extracts quote text, discovers internal links, and
  returns a mapping of URL to page text.
- `Indexer`: tokenises text, stems terms, and builds an inverted index containing
  frequency and position metadata.
- `Search`: parses queries, evaluates Boolean and phrase expressions, ranks
  matches with TF-IDF, and provides suggestions.

The inverted index has this shape:

```python
{
    "term": {
        "page-url": {
            "frequency": 3,
            "positions": [4, 18, 27],
        }
    }
}
```

## Code Quality

The source code is structured for readability, testing, and extension:

- module docstrings
- class and method docstrings
- type hints on public APIs and helper methods
- explicit `TypedDict` contracts for index data
- focused methods for crawling, parsing, ranking, and phrase matching
- deterministic sorting for stable search results

## Testing

Run the deterministic local suite:

```bash
pytest
```

Run the same coverage gate used by CI:

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

The crawler tests use mocked HTTP responses, so tests do not depend on live
network access or the availability of the target website.

The suite covers crawler success and failure paths, indexing, persistence,
TF-IDF ranking, phrase search, Boolean queries, autocomplete, suggestions,
elapsed-time output, and the CLI workflow.

See [docs/testing_strategy.md](docs/testing_strategy.md) for the full testing
strategy.

## Performance and Complexity

The hot paths use appropriate data structures and cached metadata:

- `deque` for O(1) crawler frontier pops
- sets for URL and posting-list membership checks
- cached document frequencies and IDF values
- smallest-first posting-list intersections
- phrase-result caching
- binary-search autocomplete over sorted vocabulary

See [docs/complexity.md](docs/complexity.md) for Big-O analysis of crawling,
indexing, query evaluation, phrase search, TF-IDF ranking, autocomplete, and
suggestions.

## Benchmarks

Run repeatable synthetic benchmarks:

```bash
python benchmarks/benchmark_search.py --pages 5000 --words-per-page 80 --vocabulary 2000 --repeat 5
```

The benchmark runner measures index construction, plain search, Boolean search,
phrase search, autocomplete, and spelling suggestions.

## Continuous Integration

GitHub Actions runs the test suite on Python 3.10, 3.11, and 3.12 for pushes,
pull requests, and manual workflow dispatches. The CI workflow enforces the same
90% coverage gate shown above.

## Notes

This crawler is intentionally scoped to `quotes.toscrape.com` and extracts text
from that site's quote-oriented HTML structure. For a broader web crawler, the
parser and crawl policy would need to be generalised.
