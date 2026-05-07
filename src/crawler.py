import requests
from bs4 import BeautifulSoup
import time

from requests.compat import quote


class Crawler:
    def __init__(self):
        self.base_url = "https://quotes.toscrape.com"

    def crawl(self):

        urls_to_visit = [self.base_url]
        visited_urls = set()

        pages = {}

        while urls_to_visit:

            current_url = urls_to_visit.pop(0)

            if current_url in visited_urls:
                continue

            print(f"Crawling: {current_url}")

            try:
                response = requests.get(current_url)

                soup = BeautifulSoup(response.text, "html.parser")

                quotes = soup.find_all("div", class_="quote")

                page_text = ""

                for quote in quotes:

                    quote_text = quote.find("span", class_="text").get_text()

                    author = quote.find("small", class_="author").get_text()

                    tags = quote.find_all("a", class_="tag")

                    tag_text = " ".join(tag.get_text() for tag in tags)

                    page_text += f"{quote_text} {author} {tag_text} "

                pages[current_url] = page_text

                visited_urls.add(current_url)

                links = soup.find_all("a")

                for link in links:

                    href = link.get("href")

                    if href:

                        full_url = requests.compat.urljoin(
                            self.base_url,
                            href
                        )

                        if (
                            full_url.startswith(self.base_url)
                            and full_url not in visited_urls
                            and full_url not in urls_to_visit
                        ):
                            urls_to_visit.append(full_url)

                time.sleep(1)

            except Exception as e:
                print(f"Error crawling {current_url}: {e}")

        return pages