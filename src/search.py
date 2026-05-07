import math

from nltk.stem import PorterStemmer


class Search:
    def __init__(self, index):
        self.index = index
        self.stemmer = PorterStemmer()
        self.total_documents = len(
            {
                page
                for postings in self.index.values()
                for page in postings
            }
        )

    def inverse_document_frequency(self, word):
        document_frequency = len(self.index.get(word, {}))
        return math.log((self.total_documents + 1) / (document_frequency + 1)) + 1

    def tf_idf_score(self, page, words):
        score = 0

        for word in words:
            frequency = self.index[word][page]["frequency"]
            score += frequency * self.inverse_document_frequency(word)

        return score

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
        words = [
            self.stemmer.stem(word)
            for word in query.lower().split()
        ]

        if not words:
            print("No results found.")
            return []

        page_sets = []

        for word in words:
            if word in self.index:
                page_sets.append(set(self.index[word].keys()))
            else:
                print("No results found.")
                return []

        results = set.intersection(*page_sets)

        if results:

            print(f"\nQuery: '{query}'")
            print(f"Matching pages: {len(results)}\n")

            ranked_results = []

            for page in results:
                ranked_results.append((page, self.tf_idf_score(page, words)))

            ranked_results.sort(
                key=lambda x: (-x[1], x[0])
            )

            print("Found in pages:")

            for page, score in ranked_results:
                print(f"{page} (score: {score:.4f})")

            return ranked_results

        else:
            print("No matching pages.")
            return []
