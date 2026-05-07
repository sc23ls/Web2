import json
import re
from nltk.stem import PorterStemmer

TOKEN_RE = re.compile(r"\b\w+\b")


class Indexer:
    def __init__(self):
        self.index = {}
        self.stemmer = PorterStemmer()

    def build_index(self, pages):
        for url, text in pages.items():

            words = TOKEN_RE.findall(text.lower())

            for position, word in enumerate(words):

                word = self.stemmer.stem(word)

                if word not in self.index:
                    self.index[word] = {}

                if url not in self.index[word]:
                    self.index[word][url] = {
                        "frequency": 0,
                        "positions": []
                    }

                self.index[word][url]["frequency"] += 1
                self.index[word][url]["positions"].append(position)
        print(f"Indexed {len(self.index)} unique words.")

    def save_index(self, filename="data/index.json"):
        with open(filename, "w") as f:
            json.dump(self.index, f, indent=4)

    def load_index(self, filename="data/index.json"):
        with open(filename, "r") as f:
            self.index = json.load(f)

        return self.index
    
