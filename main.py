import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import re
import os
from dotenv import load_dotenv

# loading environment variables from .env file
load_dotenv()


# class responsible for scraping quotes from the website
class QuoteScraper:
    def __init__(self):
        self.base_url = 'http://quotes.toscrape.com'
        self.url = os.getenv("INPUT_URL")   # get URL from the .env file
        self.proxy = os.getenv("PROXY")     # get proxy information from the .env file
        self.driver = self.get_webdriver_with_proxy()
        self.quotes_data = []

    def get_webdriver_with_proxy(self):
        # proxy configuration
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = self.proxy
        proxy.ssl_proxy = self.proxy

        # configuring the webdriver to use the proxy
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server={}'.format(self.proxy))

        # creating a webdriver
        driver = webdriver.Chrome()

        return driver

    def scrape_quotes(self):
        self.driver.get(self.url)

        while True:
            # looking up for the value of 'delayInMilliseconds' variable from the JavaScript code
            # in order to set up the proper delay time
            javascript_content = self.driver.page_source
            found_delay = re.findall(r'delayInMilliseconds\s*=\s*(\d+)', javascript_content)

            if found_delay:
                delay_in_milliseconds = int(found_delay[0])
            else:
                delay_in_milliseconds = 10000

            # converting to seconds
            delay = delay_in_milliseconds / 1000

            time.sleep(delay)

            # searching for all div elements containing 'quote' class - using BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            quotes = soup.find_all('div', class_='quote')

            # saving information about the text, author and tags to 'quotes_data' list
            for quote in quotes:
                quote_text = quote.find('span', class_='text').text.replace('\u201c', '').replace('\u201d', '')
                quote_author = quote.find('small', class_='author').text
                quote_tags = [tag.text for tag in quote.find_all('a', class_='tag')]

                scraped_data = {
                    "text": quote_text,
                    "by": quote_author,
                    "tags": quote_tags
                }

                self.quotes_data.append(scraped_data)

            # if 'Next' button exists scrape another quotes from the next page
            # if there is no 'Next' button (no more quotes to scrape) close the browser
            next_btn = soup.find('li', class_='next')

            if next_btn:
                next_url = self.base_url + next_btn.a['href']
                self.driver.get(next_url)
            else:
                break

        self.driver.quit()

    # saving data to JSONL file
    def save_to_jsonl(self):
        output_file = os.getenv("OUTPUT_FILE")  # get file name from the .env file
        with open(output_file, 'w', encoding='utf-8') as jsonl_file:
            for quote in self.quotes_data:
                json.dump(quote, jsonl_file, ensure_ascii=False)
                jsonl_file.write('\n')

        print("Scraped data has been saved to JSONL file.")
