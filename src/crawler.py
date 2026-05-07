import requests
from bs4 import BeautifulSoup
import time


class Crawler:
    def __init__(self):
        self.base_url = "https://quotes.toscrape.com"

    def crawl(self):
        current_url = self.base_url
        pages = {}

        while current_url:
            print(f"Crawling: {current_url}")

            response = requests.get(current_url)
            soup = BeautifulSoup(response.text, "html.parser")

            quotes = soup.find_all("span", class_="text")

            page_text = ""

            for quote in quotes:
                page_text += quote.get_text() + " "

            pages[current_url] = page_text

            next_button = soup.find("li", class_="next")

            if next_button:
                next_link = next_button.find("a")["href"]
                current_url = self.base_url + next_link
            else:
                current_url = None

            time.sleep(6)

        return pages