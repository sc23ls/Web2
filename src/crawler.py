import requests
from bs4 import BeautifulSoup
import time

from requests.compat import quote


class Crawler:
    def __init__(self):
        self.base_url = "https://quotes.toscrape.com"

    def crawl(self):

        urls_to_visit = [self.base_url.rstrip("/")]
        visited_urls = set()

        pages = {}

        while urls_to_visit:

            current_url = urls_to_visit.pop(0)

            if current_url in visited_urls:
                continue

            print(f"Crawling: {current_url}")

            print(f"Queue size: {len(urls_to_visit)}")
            print(f"Visited pages: {len(visited_urls)}")

            try:
                response = requests.get(current_url)

                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                text = soup.get_text(separator=" ", strip=True)

                pages[current_url] = text

                visited_urls.add(current_url)

                links = soup.find_all("a")

                for link in links:

                    href = link.get("href")

                    if href:

                        full_url = requests.compat.urljoin(
                            self.base_url,
                            href
                        )

                        full_url + full_url.rstrip("/")

                        if (
                            full_url.startswith(self.base_url)
                            and "#" not in full_url
                             and full_url not in visited_urls
                            and full_url not in urls_to_visit
                        ):
                            urls_to_visit.append(full_url)

                time.sleep(1)

            except Exception as e:
                print(f"Error crawling {current_url}: {e}")


        print(f"\nTotal pages crawled: {len(pages)}")

        print("\nCRAWLING COMPLETE")
        print(f"Total pages crawled: {len(visited_urls)}")

        return pages