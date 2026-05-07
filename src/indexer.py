"""Inverted-index construction and persistence.

The index maps each stemmed term to the pages where it appears, including term
frequency and token positions. Search uses those positions for phrase queries
and the frequencies for TF-IDF ranking.
"""

import json
import re
from pathlib import Path
from typing import TypedDict

from nltk.stem import PorterStemmer

TOKEN_RE = re.compile(r"\b\w+\b")


class PostingStats(TypedDict):
    """Frequency and positional metadata for one term on one page."""

    frequency: int
    positions: list[int]


InvertedIndex = dict[str, dict[str, PostingStats]]


class Indexer:
    """Build, save, and load an inverted index."""

    def __init__(self) -> None:
        self.index: InvertedIndex = {}
        self.stemmer = PorterStemmer()

    def build_index(self, pages: dict[str, str]) -> None:
        """Add pages to the inverted index.

        Args:
            pages: Mapping of page URL or identifier to extracted page text.

        Existing index contents are preserved, so repeated calls accumulate
        terms from additional pages.
        """

        for url, text in pages.items():

            words = TOKEN_RE.findall(text.lower())

            for position, word in enumerate(words):

                word = self.stemmer.stem(word)

                if word not in self.index:
                    self.index[word] = {}

                if url not in self.index[word]:
                    self.index[word][url] = {
                        "frequency": 0,
                        "positions": [],
                    }

                self.index[word][url]["frequency"] += 1
                self.index[word][url]["positions"].append(position)
        print(f"Indexed {len(self.index)} unique words.")

    def save_index(self, filename: str | Path = "data/index.json") -> None:
        """Persist the current index as formatted JSON."""

        with open(filename, "w") as f:
            json.dump(self.index, f, indent=4)

    def load_index(self, filename: str | Path = "data/index.json") -> InvertedIndex:
        """Load an index from JSON and return it."""

        with open(filename, "r") as f:
            self.index = json.load(f)

        return self.index
