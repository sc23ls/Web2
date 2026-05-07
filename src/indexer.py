"""Inverted-index construction and persistence.

The index maps each stemmed term to the pages where it appears, including term
frequency and token positions. Search uses those positions for phrase queries
and the frequencies for TF-IDF ranking.
"""

import json
from json import JSONDecodeError
import re
from pathlib import Path
from typing import Any
from typing import TypedDict

from nltk.stem import PorterStemmer

TOKEN_RE = re.compile(r"\b\w+\b")


class PostingStats(TypedDict):
    """Frequency and positional metadata for one term on one page."""

    frequency: int
    positions: list[int]


InvertedIndex = dict[str, dict[str, PostingStats]]


class IndexerError(Exception):
    """Base class for indexer-specific failures."""


class IndexPersistenceError(IndexerError):
    """Raised when an index cannot be saved or loaded safely."""


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

    @staticmethod
    def _validate_index(data: Any) -> InvertedIndex:
        """Validate loaded JSON before accepting it as an inverted index."""

        if not isinstance(data, dict):
            raise IndexPersistenceError("Index file must contain a JSON object.")

        for term, postings in data.items():
            if not isinstance(term, str) or not isinstance(postings, dict):
                raise IndexPersistenceError("Index terms must map to page postings.")

            for page, stats in postings.items():
                if not isinstance(page, str) or not isinstance(stats, dict):
                    raise IndexPersistenceError("Index postings must map pages to stats.")

                frequency = stats.get("frequency")
                positions = stats.get("positions")

                if not isinstance(frequency, int) or not isinstance(positions, list):
                    raise IndexPersistenceError(
                        "Posting stats must include integer frequency and positions list."
                    )

                if not all(isinstance(position, int) for position in positions):
                    raise IndexPersistenceError("Posting positions must be integers.")

        return data

    def save_index(self, filename: str | Path = "data/index.json") -> None:
        """Persist the current index as formatted JSON."""

        path = Path(filename)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w") as f:
                json.dump(self.index, f, indent=4)
        except OSError as error:
            raise IndexPersistenceError(f"Could not save index to {path}: {error}") from error

    def load_index(self, filename: str | Path = "data/index.json") -> InvertedIndex:
        """Load an index from JSON and return it."""

        path = Path(filename)

        try:
            with open(path, "r") as f:
                loaded_index = json.load(f)
        except FileNotFoundError as error:
            raise IndexPersistenceError(f"Index file not found: {path}") from error
        except JSONDecodeError as error:
            raise IndexPersistenceError(f"Index file is not valid JSON: {path}") from error
        except OSError as error:
            raise IndexPersistenceError(f"Could not load index from {path}: {error}") from error

        self.index = self._validate_index(loaded_index)

        return self.index
