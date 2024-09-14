import aiohttp
import asyncio
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Fetch HTML content from a URL
async def fetch_html(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        print(f"Error fetching {url}: {e}")
        return None

# Extract article text (up to num_paragraphs)
def extract_article_text(html, num_paragraphs=2):
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('p', limit=num_paragraphs)
    article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
    return article_text

# Generate an article summary by condensing the first few paragraphs
def summarize_article(text, limit=300):
    if len(text) > limit:
        return text[:limit].rsplit(' ', 1)[0] + '...'  # Truncate the text at the last complete word
    return text

# Parse the HTML content and extract articles with plant-related keywords
async def parse_news(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    articles = []
    
    # Find all <a> tags with href attributes
    links = soup.find_all('a', href=True)

    # Prepare a list to hold URLs and headers for later processing
    tasks = []
    headers = []

    for tag in links:
        header = tag.get_text(strip=True)
        link = tag['href']
        
        # Check if the header contains plant-related keywords
        if re.search(r'plant|botany|green|nature', header, re.IGNORECASE):
            # Convert relative URLs to absolute URLs
            full_url = urljoin(base_url, link)
            headers.append(header)
            tasks.append(fetch_html(full_url))
    
    # Gather results from all fetch tasks
    results = await asyncio.gather(*tasks)
    
    # Process the fetched articles and generate summaries
    for result, header, link in zip(results, headers, [urljoin(base_url, tag['href']) for tag in links if re.search(r'plant|botany|green|nature', tag.get_text(strip=True), re.IGNORECASE)]):
        if result:
            article_text = extract_article_text(result)
            if article_text:
                summary = summarize_article(article_text)
                articles.append({
                    "title": header,
                    "summary": summary,
                    "link": link
                })

    return articles

# List of news websites to scrape
NEWS_SITES = [
    'https://www.greentechmedia.com/',
    'https://www.euronews.com/tag/plants',
    'https://www.sciencenews.org/topic/plants'
]

# Asynchronous function to scrape news from multiple websites
async def scrape_news():
    all_articles = []
    
    # Define the tasks for concurrent fetching of multiple websites
    tasks = [fetch_html(site) for site in NEWS_SITES]
    
    # Gather all tasks (fetch HTML concurrently)
    results = await asyncio.gather(*tasks)
    
    # Process the HTML content and parse articles for each site
    for i, html in enumerate(results):
        if html:
            articles = await parse_news(html, NEWS_SITES[i])
            all_articles.extend(articles)
    
    return all_articles

# To call the async scrape_news function from a non-async context
def get_news_for_client():
    return asyncio.run(scrape_news())

