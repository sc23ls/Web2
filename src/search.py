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
            print("Found in pages:")

            for page in results:
                print(page)

        else:
            print("No matching pages.")