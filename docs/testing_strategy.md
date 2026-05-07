# Testing Strategy

This project uses automated tests to verify the crawler, indexer, search engine,
query processing, and command-line workflow. The goal is to catch regressions
without relying on live websites, network access, or manually inspected output.

## Test Goals

The test suite is designed to prove that:

- crawling extracts the expected page text
- crawler failures are handled without crashing the application
- indexing records frequencies and positions correctly
- indexes can be saved and loaded safely
- search ranking is deterministic and based on TF-IDF
- advanced query processing behaves correctly
- terminal output remains useful for users
- the command-line workflow can build, load, print, and search an index

## Test Types

### Unit Tests

Unit tests cover individual behaviours in isolation:

- `Indexer.build_index`
- `Indexer.save_index`
- `Indexer.load_index`
- `Search.find`
- `Search.print_word`
- TF-IDF scoring
- Boolean query evaluation
- phrase matching
- autocomplete
- spelling suggestions
- elapsed-time formatting

These tests use small, explicit inputs so expected results are easy to inspect.

### Mocked Crawler Tests

Crawler tests use fake HTTP sessions and fake responses instead of calling the
real `quotes.toscrape.com` website.

This is intentional because live-network tests are brittle:

- DNS or internet access may fail
- the remote website may be slow or unavailable
- external content can change
- CI environments may restrict network access

Mocked responses make crawler tests deterministic and fast while still covering
HTML parsing, link discovery, duplicate URL handling, error handling, crawl
limits, and elapsed-time output.

### CLI Workflow Tests

The command-line entry point is tested by patching `input()` and replacing the
crawler, indexer, and search classes with fakes.

This verifies command handling without performing real crawls or filesystem
writes.

## Edge Cases Covered

The suite covers:

- request timeouts
- malformed quote markup
- external links
- duplicate links with and without trailing slashes
- URL fragments
- maximum crawl page limits
- mixed-case input
- punctuation in indexed text
- stemming behaviour
- repeated terms
- missing query terms
- empty queries
- terms that do not overlap across pages
- quoted phrases with adjacent and non-adjacent positions
- Boolean `AND`, `OR`, and `NOT`
- Boolean queries containing phrases
- stop-word filtering
- spelling suggestions for misspelled terms
- autocomplete from indexed vocabulary

## Coverage Policy

The project enforces coverage with:

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

The minimum accepted coverage is 90%. The current suite is above that threshold,
which gives confidence that the main crawler, indexer, search, and CLI paths are
covered.

Coverage is useful, but it is not the only goal. Tests are written around
important behaviour and edge cases rather than only chasing line coverage.

## Continuous Integration

GitHub Actions runs the test suite on:

- Python 3.10
- Python 3.11
- Python 3.12

The CI workflow runs on pushes, pull requests, and manual dispatch. This means
changes must pass the automated suite and the coverage gate before they can be
treated as safe.

## Tests vs Benchmarks

Tests check correctness. They should be deterministic and have clear pass/fail
results.

Benchmarks measure performance. They are not used to prove correctness, and
their timings can vary depending on the machine.

This project keeps benchmarks in `benchmarks/` and documents algorithmic
complexity in `docs/complexity.md`.

## Running Tests

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the standard suite:

```bash
pytest
```

Run the full coverage gate:

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```
