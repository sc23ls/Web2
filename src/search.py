from nltk.stem import PorterStemmer


class Search:
    def __init__(self, index):
        self.index = index
        self.stemmer = PorterStemmer()

    def print_word(self, word):
        word = word.lower()

        if word in self.index:
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
        else:
            print("Word not found.")

    def find(self, query):
        words = [
            self.stemmer.stem(word)
            for word in query.lower().split()
        ]

        page_sets = []

        for word in words:
            if word in self.index:
                page_sets.append(set(self.index[word].keys()))
            else:
                print("No results found.")
                return

        results = set.intersection(*page_sets)

        if results:

            print(f"\nQuery: '{query}'")
            print(f"Matching pages: {len(results)}\n")

            ranked_results = []

            for page in results:

                total_frequency = 0

                for word in words:
                    total_frequency += self.index[word][page]["frequency"]

                ranked_results.append((page, total_frequency))

            ranked_results.sort(
                key=lambda x: x[1],
                reverse=True
            )

            print("Found in pages:")

            for page, score in ranked_results:
                print(f"{page} (score: {score})")

        else:
            print("No matching pages.")