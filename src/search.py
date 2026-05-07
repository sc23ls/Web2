from bisect import bisect_left
import difflib
import math
import re

from nltk.stem import PorterStemmer

TOKEN_RE = re.compile(r"\b\w+\b")
QUERY_TOKEN_RE = re.compile(r'"[^"]+"|\bAND\b|\bOR\b|\bNOT\b|\b\w+\b', re.I)


class Search:
    STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "to",
        "with",
    }
    OPERATORS = {"AND", "OR", "NOT"}
    OPERATOR_PRECEDENCE = {"OR": 1, "AND": 2, "NOT": 3}

    def __init__(self, index):
        self.index = index
        self.stemmer = PorterStemmer()
        self.documents = {
            page
            for postings in self.index.values()
            for page in postings
        }
        self.total_documents = len(self.documents)
        self.vocabulary = sorted(self.index)
        self.posting_pages = {
            word: set(postings)
            for word, postings in self.index.items()
        }
        self.document_frequencies = {
            word: len(postings)
            for word, postings in self.index.items()
        }
        self.idf_cache = {
            word: math.log((self.total_documents + 1) / (frequency + 1)) + 1
            for word, frequency in self.document_frequencies.items()
        }
        self.phrase_cache = {}

    def normalize_terms(self, text, remove_stop_words=True):
        terms = TOKEN_RE.findall(text.lower())

        if remove_stop_words:
            terms = [term for term in terms if term not in self.STOP_WORDS]

        return [self.stemmer.stem(term) for term in terms]

    def autocomplete(self, prefix, limit=5):
        normalized = self.normalize_terms(prefix, remove_stop_words=False)

        if not normalized:
            return []

        prefix = normalized[-1]
        start = bisect_left(self.vocabulary, prefix)
        suggestions = []

        for word in self.vocabulary[start:]:
            if not word.startswith(prefix) or len(suggestions) >= limit:
                break

            suggestions.append(word)

        return suggestions

    def suggest_corrections(self, query, limit=5):
        suggestions = []

        for word in self.normalize_terms(query):
            if word in self.index:
                continue

            suggestions.extend(
                match
                for match in difflib.get_close_matches(
                    word,
                    self.vocabulary,
                    n=limit,
                    cutoff=0.72,
                )
                if match not in suggestions
            )

            if len(suggestions) >= limit:
                break

        return suggestions[:limit]

    def inverse_document_frequency(self, word):
        if word not in self.idf_cache:
            document_frequency = self.document_frequencies.get(word, 0)
            self.idf_cache[word] = (
                math.log((self.total_documents + 1) / (document_frequency + 1)) + 1
            )

        return self.idf_cache[word]

    def tf_idf_score(self, page, words):
        score = 0

        for word in words:
            frequency = self.index[word][page]["frequency"]
            score += frequency * self.inverse_document_frequency(word)

        return score

    def pages_for_phrase(self, phrase):
        words = self.normalize_terms(phrase)

        cache_key = tuple(words)

        if cache_key in self.phrase_cache:
            return self.phrase_cache[cache_key].copy()

        if not words or any(word not in self.index for word in words):
            self.phrase_cache[cache_key] = set()
            return set()

        candidate_pages = self.intersect_postings(words)
        matching_pages = set()

        for page in candidate_pages:
            first_positions = self.index[words[0]][page]["positions"]
            other_positions = [
                set(self.index[word][page]["positions"])
                for word in words[1:]
            ]

            for position in first_positions:
                if all(
                    position + offset + 1 in positions
                    for offset, positions in enumerate(other_positions)
                ):
                    matching_pages.add(page)
                    break

        self.phrase_cache[cache_key] = matching_pages
        return matching_pages.copy()

    def phrase_search(self, phrase):
        words = self.normalize_terms(phrase)
        results = self.pages_for_phrase(phrase)
        ranked_results = self.rank_pages(results, words)

        if ranked_results:
            print(f"\nPhrase: \"{phrase}\"")
            print(f"Matching pages: {len(ranked_results)}\n")
            print("Found in pages:")

            for page, score in ranked_results:
                print(f"{page} (score: {score:.4f})")
        else:
            print("No matching pages.")

        return ranked_results

    def tokenize_query(self, query):
        raw_tokens = QUERY_TOKEN_RE.findall(query)
        tokens = []

        for token in raw_tokens:
            upper_token = token.upper()

            if upper_token in self.OPERATORS:
                tokens.append(upper_token)
            elif token.startswith('"') and token.endswith('"'):
                phrase = token[1:-1]

                if self.normalize_terms(phrase):
                    tokens.append(("PHRASE", phrase))
            else:
                words = self.normalize_terms(token)

                if words:
                    tokens.append(("TERM", words[0]))

        return tokens

    def to_postfix(self, tokens):
        output = []
        operators = []

        for token in tokens:
            if isinstance(token, tuple):
                output.append(token)
                continue

            while (
                operators
                and self.OPERATOR_PRECEDENCE[operators[-1]] >= self.OPERATOR_PRECEDENCE[token]
            ):
                output.append(operators.pop())

            operators.append(token)

        output.extend(reversed(operators))
        return output

    def evaluate_postfix(self, postfix):
        stack = []

        for token in postfix:
            if isinstance(token, tuple):
                kind, value = token

                if kind == "TERM":
                    stack.append(self.posting_pages.get(value, set()).copy())
                else:
                    stack.append(self.pages_for_phrase(value))

                continue

            if token == "NOT":
                if not stack:
                    return set()

                stack.append(self.documents - stack.pop())
                continue

            if len(stack) < 2:
                return set()

            right = stack.pop()
            left = stack.pop()

            if token == "AND":
                stack.append(left & right)
            elif token == "OR":
                stack.append(left | right)

        if len(stack) != 1:
            return set()

        return stack[0]

    def positive_query_terms(self, tokens):
        words = []
        negated = False

        for token in tokens:
            if token == "NOT":
                negated = True
                continue

            if token in {"AND", "OR"}:
                continue

            if not negated:
                kind, value = token
                words.extend([value] if kind == "TERM" else self.normalize_terms(value))

            negated = False

        return [word for word in words if word in self.index]

    def intersect_postings(self, words):
        if not words:
            return set()

        ordered_words = sorted(words, key=lambda word: self.document_frequencies[word])
        results = self.posting_pages[ordered_words[0]].copy()

        for word in ordered_words[1:]:
            results.intersection_update(self.posting_pages[word])

            if not results:
                break

        return results

    def rank_pages(self, pages, words):
        ranked_results = [
            (page, self.tf_idf_score(page, [word for word in words if page in self.index[word]]))
            for page in pages
        ]
        ranked_results.sort(key=lambda x: (-x[1], x[0]))
        return ranked_results

    def score_page_for_tokens(self, page, tokens, phrase_matches=None):
        phrase_matches = phrase_matches or {}
        score = 0
        negated = False

        for token in tokens:
            if token == "NOT":
                negated = True
                continue

            if token in {"AND", "OR"}:
                continue

            if negated:
                negated = False
                continue

            kind, value = token

            if kind == "TERM":
                if page in self.index.get(value, {}):
                    score += self.tf_idf_score(page, [value])
            elif page in phrase_matches.get(value, set()):
                score += self.tf_idf_score(page, self.normalize_terms(value))

        return score

    def rank_pages_for_tokens(self, pages, tokens):
        phrase_matches = {
            token[1]: self.pages_for_phrase(token[1])
            for token in tokens
            if isinstance(token, tuple) and token[0] == "PHRASE"
        }
        ranked_results = [
            (page, self.score_page_for_tokens(page, tokens, phrase_matches))
            for page in pages
        ]
        ranked_results.sort(key=lambda x: (-x[1], x[0]))
        return ranked_results

    def print_word(self, word):
        word = word.lower()

        word = self.stemmer.stem(word)

        if word not in self.index:
            print("Word not found.")
            return

        postings = self.index[word]

        print(f"\nWord: '{word}'")
        print(f"Appears on {len(postings)} pages.\n")

        total_frequency = 0

        for page, stats in postings.items():

            frequency = stats["frequency"]

            total_frequency += frequency

            print(f"{page}")
            print(f"  Frequency: {frequency}")
            print(f"  Positions: {stats['positions']}")
            print()

        print(f"Total occurrences across all pages: {total_frequency}")

    def find(self, query):
        tokens = self.tokenize_query(query)

        if not tokens:
            print("No results found.")
            return []

        has_boolean_operator = any(token in self.OPERATORS for token in tokens)

        if not has_boolean_operator and len(tokens) == 1 and tokens[0][0] == "PHRASE":
            return self.phrase_search(tokens[0][1])

        if has_boolean_operator:
            words = self.positive_query_terms(tokens)

            if not words:
                print("No results found.")
                return []

            results = self.evaluate_postfix(self.to_postfix(tokens))
            ranked_results = self.rank_pages_for_tokens(results, tokens)
        else:
            words = [token[1] for token in tokens]

            missing_words = [word for word in words if word not in self.index]

            if missing_words:
                suggestions = self.suggest_corrections(query)
                print("No results found.")

                if suggestions:
                    print(f"Did you mean: {', '.join(suggestions)}?")

                return []

            results = self.intersect_postings(words)
            ranked_results = self.rank_pages(results, words)

        if results:

            print(f"\nQuery: '{query}'")
            print(f"Matching pages: {len(results)}\n")

            print("Found in pages:")

            for page, score in ranked_results:
                print(f"{page} (score: {score:.4f})")

            return ranked_results

        else:
            print("No matching pages.")
            return []
