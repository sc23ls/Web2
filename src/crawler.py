import requests
from bs4 import BeautifulSoup
import time


class Crawler:
    def __init__(
        self,
        base_url="https://quotes.toscrape.com",
        session=None,
        delay=1,
        max_pages=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests
        self.delay = delay
        self.max_pages = max_pages

    def crawl(self):

        urls_to_visit = [self.base_url]
        visited_urls = set()

        pages = {}

        while urls_to_visit:
            if self.max_pages is not None and len(visited_urls) >= self.max_pages:
                break

            current_url = urls_to_visit.pop(0)

            if current_url in visited_urls:
                continue

            print(f"Crawling: {current_url}")

            print(f"Queue size: {len(urls_to_visit)}")
            print(f"Visited pages: {len(visited_urls)}")

            try:
                response = self.session.get(current_url, timeout=10)

                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                page_text = ""

                quotes = soup.find_all("div", class_="quote")

                for quote in quotes:

                    quote_text = quote.find("span", class_="text").get_text()

                    author = quote.find("small", class_="author").get_text()

                    tags = quote.find_all("a", class_="tag")

                    tag_text = " ".join(tag.get_text() for tag in tags)

                    page_text += f"{quote_text} {author} {tag_text} "

                author_details = soup.find("div", class_="author-details")

                if author_details:
                    page_text += author_details.get_text(separator=" ", strip=True)

                pages[current_url] = page_text

                visited_urls.add(current_url)

                links = soup.find_all("a")

                for link in links:

                    href = link.get("href")

                    if href:

                        full_url = requests.compat.urljoin(
                            self.base_url,
                            href
                        ).rstrip("/")

                        if (
                            full_url.startswith(self.base_url)
                            and "#" not in full_url
                            and full_url not in visited_urls
                            and full_url not in urls_to_visit
                        ):
                            urls_to_visit.append(full_url)

                if self.delay:
                    time.sleep(self.delay)

            except Exception as e:
                print(f"Error crawling {current_url}: {e}")


        print(f"\nTotal pages crawled: {len(pages)}")

        print("\nCRAWLING COMPLETE")
        print(f"Total pages crawled: {len(visited_urls)}")

        return pages
