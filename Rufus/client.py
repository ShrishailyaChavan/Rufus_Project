# client.py
from .scraper import ChromiumLoader
import asyncio

class RufusClient:
    def __init__(self, headless=True):
        self.loader = ChromiumLoader(headless=headless)

    async def scrape(self, urls, prompt, max_depth=3):
        documents = await self.loader.scrape_urls(urls, max_depth=max_depth)
        filtered_documents = self.filter_data_based_on_prompt(documents, prompt)
        return filtered_documents

    @staticmethod
    def filter_data_based_on_prompt(data, prompt):
        # Add filtering logic here as described previously
        pass  # Placeholder for actual filtering code

# Example function to handle asynchronous operation
def fetch_data(urls, prompt):
    client = RufusClient(headless=True)
    return asyncio.run(client.scrape(urls, prompt))
