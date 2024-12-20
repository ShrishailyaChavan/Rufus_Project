import asyncio
from playwright.async_api import async_playwright
import json
from urllib.parse import urlparse, urljoin
from sentence_transformers import SentenceTransformer, util

# Load the model once at the start
model = SentenceTransformer('all-MiniLM-L6-v2')

class Document:
    def __init__(self, data, metadata):
        self.data = data
        self.metadata = metadata
    #Hello this si project Rufus
class ChromiumLoader:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.visited_urls = set()

    async def scrape_page(self, browser, url: str, depth=0, max_depth=10) -> dict:
        normalized_url = url.rstrip('/')
        if normalized_url in self.visited_urls:
            return {}
        self.visited_urls.add(normalized_url)

        page = await browser.new_page()
        content_data = {}
        try:
            await page.goto(url, wait_until="networkidle")
            content_data = {
                'url': url,
                'title': await page.title(),
                'content': await page.evaluate("() => document.body.innerText"),
                'links': []
            }

            if depth < max_depth:
                links = await page.evaluate("() => Array.from(document.querySelectorAll('a'), a => a.href)")
                for link in links:
                    link = urljoin(url, link)
                    if urlparse(link).netloc == urlparse(url).netloc:
                        nested_data = await self.scrape_page(browser, link, depth + 1, max_depth)
                        if nested_data:
                            content_data['links'].append(nested_data)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        finally:
            await page.close()

        return content_data

    async def scrape_urls(self, urls: list, max_depth=3) -> list:
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            for url in urls:
                result = await self.scrape_page(browser, url, max_depth=max_depth)
                if result:
                    results.append(result)
            await browser.close()
        return results

    def save_to_json(self, data, filename='output.json'):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

async def main():
    # Input from user
    urls = input("Enter the URLs to scrape, separated by commas: ").split(',')
    prompt = input("Enter the prompt to filter the content: ")

    loader = ChromiumLoader(headless=True)
    documents = await loader.scrape_urls(urls, max_depth=3)
    loader.save_to_json(documents, 'scraped_data_4.json')

    # Load the data back from the file
    with open('scraped_data_4.json', 'r') as f:
        data = json.load(f)

    filtered_documents = filter_data_based_on_prompt(data, prompt)
    print(json.dumps(filtered_documents, indent=4))

def filter_data_based_on_prompt(data, prompt):
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)
    relevant_data = []
    for item in flatten_data(data):
        content_embedding = model.encode(item['content'], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(prompt_embedding, content_embedding)
        if similarity.item() > 0.5:
            item['similarity'] = similarity.item()
            relevant_data.append(item)
    return relevant_data

def flatten_data(data):
    """ Flatten nested data into a list of documents for easier processing """
    flat_list = []
    def recurse_items(item):
        if 'content' in item:
            flat_list.append(item)
        for link in item.get('links', []):
            recurse_items(link)
    for item in data:
        recurse_items(item)
    return flat_list

if __name__ == "__main__":
    asyncio.run(main())
