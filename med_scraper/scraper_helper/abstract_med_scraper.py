from abc import ABC, abstractmethod

# Define the interface for Scrapers
class Scraper(ABC):
    @abstractmethod
    def scrape_data(self, drug_name):
        pass

    @abstractmethod
    def scrape_multiple_data(self, drug_names):
        pass
