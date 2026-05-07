"""Command-line interface for building and querying the local search index."""

from crawler import Crawler, CrawlerError
from indexer import Indexer, IndexPersistenceError
from search import Search, SearchError


def main() -> None:
    """Run the interactive crawler/search prompt."""

    crawler = Crawler()
    indexer = Indexer()

    loaded = False

    while True:
        try:
            command = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if command == "build":

            try:
                pages = crawler.crawl()

                indexer.build_index(pages)

                indexer.save_index()

                print("Index built and saved.")
            except (CrawlerError, IndexPersistenceError) as error:
                print(f"Build failed: {error}")

        elif command == "load":

            try:
                indexer.load_index()
            except IndexPersistenceError as error:
                print(f"Load failed: {error}")
                continue

            loaded = True

            print("Index loaded.")

        elif command.startswith("print "):

            if not loaded:
                print("Please load the index first.")
                continue

            word = command[6:]

            search = Search(indexer.index)

            try:
                search.print_word(word)
            except SearchError as error:
                print(f"Search failed: {error}")

        elif command.startswith("find "):

            if not loaded:
                print("Please load the index first.")
                continue

            query = command[5:]

            search = Search(indexer.index)

            try:
                search.find(query)
            except SearchError as error:
                print(f"Search failed: {error}")

        elif command == "exit":
            break

        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()
