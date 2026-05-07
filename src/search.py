class Search:
    def __init__(self, index):
        self.index = index

    def print_word(self, word):
        word = word.lower()

        if word in self.index:
            print(self.index[word])
        else:
            print("Word not found.")

    def find(self, query):
        words = query.lower().split()

        page_sets = []

        for word in words:
            if word in self.index:
                page_sets.append(set(self.index[word].keys()))
            else:
                print("No results found.")
                return

        results = set.intersection(*page_sets)

        if results:

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