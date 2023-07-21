from main import QuoteScraper

if __name__ == "__main__":
    scraper = QuoteScraper()
    scraper.scrape_quotes()
    scraper.save_to_jsonl()
