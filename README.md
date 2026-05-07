## Web crawler

A small Python crawler, indexer, and search utility for pages from
`quotes.toscrape.com`.

## Testing

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the deterministic local test suite:

```bash
pytest
```

Run the same coverage gate used by CI:

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

The crawler tests use mocked HTTP responses, so they do not depend on live
network access or the availability of the target site.

See `docs/testing_strategy.md` for the documented testing strategy, including
test types, mocked crawler testing, covered edge cases, coverage policy, CI, and
the distinction between tests and benchmarks.

## Search features

Search supports TF-IDF ranking, stop-word filtering, stemming, quoted phrase
queries, Boolean operators, autocomplete, and spelling suggestions from indexed
terms.

Example queries:

```text
life wisdom
"oscar wilde"
life AND wisdom
life OR humor
life AND NOT death
```

## Performance

The crawler and search engine use optimised data structures for their hot paths:
`deque` queueing for crawls, set-based URL and posting-list operations, cached
IDF values, smallest-first posting intersections, phrase-result caching, and
binary-search autocomplete.

Run repeatable synthetic benchmarks:

```bash
python benchmarks/benchmark_search.py --pages 5000 --words-per-page 80 --vocabulary 2000 --repeat 5
```

See `docs/complexity.md` for Big-O complexity analysis of crawling, indexing,
query evaluation, phrase search, TF-IDF ranking, autocomplete, and suggestions.

## Automation

GitHub Actions runs the test suite on Python 3.10, 3.11, and 3.12 for pushes,
pull requests, and manual workflow dispatches.
