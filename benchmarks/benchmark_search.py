import argparse
import contextlib
import io
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from src.indexer import Indexer
from src.search import Search


def generate_pages(page_count, words_per_page, vocabulary_size):
    vocabulary = [f"term{i}" for i in range(vocabulary_size)]
    pages = {}

    for page_number in range(page_count):
        words = []

        for position in range(words_per_page):
            words.append(vocabulary[(page_number * 17 + position * 31) % vocabulary_size])

        if page_number % 10 == 0 and words_per_page >= 2:
            words[0] = "alpha"
            words[1] = "beta"

        if page_number % 15 == 0:
            words[-1] = "gamma"

        pages[f"page-{page_number}"] = " ".join(words)

    return pages


def time_call(repeat, function, *args):
    timings = []

    for _ in range(repeat):
        start = time.perf_counter()
        function(*args)
        timings.append(time.perf_counter() - start)

    return {
        "min": min(timings),
        "mean": statistics.mean(timings),
        "max": max(timings),
    }


def quiet_call(function, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args)


def print_result(name, timings):
    print(
        f"{name:<28} "
        f"min={timings['min']:.6f}s "
        f"mean={timings['mean']:.6f}s "
        f"max={timings['max']:.6f}s"
    )


def main():
    parser = argparse.ArgumentParser(description="Benchmark crawler search algorithms.")
    parser.add_argument("--pages", type=int, default=5000)
    parser.add_argument("--words-per-page", type=int, default=80)
    parser.add_argument("--vocabulary", type=int, default=2000)
    parser.add_argument("--repeat", type=int, default=5)
    args = parser.parse_args()

    pages = generate_pages(args.pages, args.words_per_page, args.vocabulary)
    indexer = Indexer()

    print(
        "Dataset: "
        f"{args.pages} pages, "
        f"{args.words_per_page} words/page, "
        f"{args.vocabulary} vocabulary terms"
    )

    print_result(
        "build_index",
        time_call(1, quiet_call, indexer.build_index, pages),
    )

    search = Search(indexer.index)

    benchmarks = [
        ("plain AND query", quiet_call, search.find, "alpha beta"),
        ("boolean query", quiet_call, search.find, "alpha AND NOT gamma"),
        ("phrase query", quiet_call, search.find, '"alpha beta"'),
        ("autocomplete", search.autocomplete, "term1"),
        ("suggestions", search.suggest_corrections, "trm100"),
    ]

    for name, function, *function_args in benchmarks:
        print_result(
            name,
            time_call(args.repeat, function, *function_args),
        )


if __name__ == "__main__":
    main()
