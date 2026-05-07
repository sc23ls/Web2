# Complexity Analysis

This project is a compact information retrieval system: crawl pages, build an
inverted index, and answer ranked queries. The notes below describe the main
algorithmic costs after the current optimisations.

## Symbols

- `n`: number of crawled pages
- `l`: number of discovered links
- `t`: total number of indexed tokens
- `v`: vocabulary size, or number of unique indexed terms
- `d`: number of indexed documents
- `k`: number of query terms
- `p_i`: posting-list size for query term `i`
- `r`: number of matched result pages
- `m`: phrase length in terms
- `s`: number of returned suggestions

## Crawler

The crawler uses a `deque` for the URL frontier and sets for visited and queued
URLs.

- Queue pop: `O(1)`
- Duplicate queued/visited checks: average `O(1)`
- Link processing: `O(l)`
- Overall crawl bookkeeping: `O(n + l)`, ignoring network latency and HTML
  parsing cost

The previous list-based frontier used `pop(0)`, which is `O(q)` for queue size
`q` because every remaining item has to shift left.

## Indexing

The indexer tokenises each page once and appends term positions into an inverted
index.

- Tokenisation: `O(t)`
- Stemming and insertion: average `O(t)`
- Space usage: `O(t)` because every token occurrence contributes one stored
  position

The token regex is compiled once, avoiding repeated regex compilation.

## Search Initialisation

`Search` precomputes reusable metadata:

- Document set: `O(v + total_postings)`
- Posting page sets: `O(total_postings)`
- Document frequencies: `O(v)`
- IDF cache: `O(v)`
- Sorted vocabulary: `O(v log v)`

This moves repeated query-time work into one setup pass.

## Plain AND Queries

Plain multi-term queries use posting-list intersection. Posting lists are
intersected from smallest to largest.

- Worst-case intersection: `O(p_1 + p_2 + ... + p_k)`
- Practical improvement: starting with the smallest posting list quickly shrinks
  the candidate set
- Ranking: `O(r * k)`

## Boolean Queries

Boolean queries are tokenised, converted to postfix notation, then evaluated
with set operations.

- Tokenisation: `O(query length)`
- Shunting-yard conversion: `O(k)`
- Evaluation: proportional to the posting sets touched, usually
  `O(p_1 + p_2 + ... + p_k)`
- Ranking: `O(r * k)` over positive, non-negated terms and phrases

## Phrase Queries

Phrase search first intersects the terms' posting lists to find candidate pages,
then checks adjacent positions.

- Candidate discovery: `O(p_1 + p_2 + ... + p_m)`
- Position checking: `O(c * a * m)`, where `c` is candidate pages and `a` is the
  number of positions for the first phrase term on a candidate page
- Phrase results are cached by normalised phrase terms, so repeated phrase
  queries are `O(1)` for candidate retrieval plus result copying.

## TF-IDF Ranking

IDF values are cached during `Search` initialisation.

- Single IDF lookup: average `O(1)`
- Score one page for `k` terms: `O(k)`
- Rank `r` pages: `O(r * k + r log r)`

The `r log r` term comes from sorting by score.

## Autocomplete

The vocabulary is sorted once. Autocomplete uses binary search to jump to the
first possible prefix match.

- Prefix lookup: `O(log v + s)`
- Space: `O(v)` for the sorted vocabulary

This replaces scanning every vocabulary term, which is `O(v)`.

## Spelling Suggestions

Suggestions use Python's `difflib.get_close_matches` against the vocabulary.

- Current cost: roughly `O(v * word_length)` per misspelled query term
- This is acceptable for the current project size, but a BK-tree or trigram
  index would be a better next optimisation for very large vocabularies.

## Benchmarking

The benchmark runner in `benchmarks/benchmark_search.py` generates repeatable
synthetic data and measures:

- index construction
- plain AND search
- Boolean search
- phrase search
- autocomplete
- spelling suggestions

Example:

```bash
python benchmarks/benchmark_search.py --pages 5000 --words-per-page 80 --vocabulary 2000 --repeat 5
```

Synthetic data is used so dataset size and term distribution are controlled and
benchmarks are repeatable without live network access.
