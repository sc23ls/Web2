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

## Automation

GitHub Actions runs the test suite on Python 3.10, 3.11, and 3.12 for pushes,
pull requests, and manual workflow dispatches.
