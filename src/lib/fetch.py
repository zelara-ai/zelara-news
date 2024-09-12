import requests
from bs4 import BeautifulSoup
import re

# Fetch HTML content from a URL
def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTP errors if occurred
        return response.text
    except requests.RequestException as e:
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
    # Simple summary by truncating the text to the specified character limit
    if len(text) > limit:
        return text[:limit].rsplit(' ', 1)[0] + '...'  # Truncate the text at the last complete word
    return text

# Parse the HTML content and extract articles with plant-related keywords
def parse_news(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    articles = []

    # Look for article tags and extract relevant news headers and links
    for tag in soup.find_all('a', href=True):
        header = tag.get_text(strip=True)
        link = tag['href']
        
        # Only consider valid URLs and filter by plant-related keywords
        if re.search(r'plant|botany|green|nature', header, re.IGNORECASE):
            if not link.startswith('http'):
                link = url + link  # Handle relative URLs
            
            # Fetch the article content
            article_html = fetch_html(link)
            if article_html:
                article_text = extract_article_text(article_html)  # Get the first two paragraphs
                if article_text:
                    summary = summarize_article(article_text)  # Generate a human-readable summary
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

# Function to scrape news from multiple websites
def scrape_news():
    all_articles = []
    for site in NEWS_SITES:
        print(f"Scraping {site}...")
        html = fetch_html(site)
        if html:
            articles = parse_news(html, site)
            all_articles.extend(articles)
    
    return all_articles
