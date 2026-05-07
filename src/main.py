from crawler import Crawler
from indexer import Indexer
from search import Search


def main():
    crawler = Crawler()
    indexer = Indexer()

    loaded = False

    while True:
        command = input("> ").strip()

        if command == "build":

            pages = crawler.crawl()

            indexer.build_index(pages)

            indexer.save_index()

            print("Index built and saved.")

        elif command == "load":

            indexer.load_index()

            loaded = True

            print("Index loaded.")

        elif command.startswith("print "):

            if not loaded:
                print("Please load the index first.")
                continue

            word = command[6:]

            search = Search(indexer.index)

            search.print_word(word)

        elif command.startswith("find "):

            if not loaded:
                print("Please load the index first.")
                continue

            query = command[5:]

            search = Search(indexer.index)

            search.find(query)

        elif command == "exit":
            break

        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()