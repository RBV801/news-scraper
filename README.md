# News Scraper

A flexible and robust web scraper for news articles from various sources.

## Features

- Fetch individual articles by URL
- Fetch latest articles from a news source
- Extract article metadata (title, content, author, date, summary, categories)
- Handle errors gracefully
- User-agent rotation to avoid blocking
- Rate limiting to be respectful to servers
- Proxy support (optional)
- Extensible architecture for adding new news sources

## Included Scrapers

- **NYTimesScraper**: Scraper for The New York Times (nytimes.com)
- **BBCScraper**: Scraper for BBC News (bbc.com/news)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/news-scraper.git
cd news-scraper
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from news_scraper import NYTimesScraper, BBCScraper

# Create a scraper for The New York Times
nyt_scraper = NYTimesScraper()

# Fetch the latest articles (default limit is 10)
articles = nyt_scraper.fetch_latest_articles(limit=5)

# Process the articles
for article in articles:
    print(f"Title: {article.title}")
    print(f"Author: {article.author}")
    print(f"Date: {article.date}")
    print(f"URL: {article.url}")
    print(f"Content preview: {article.content[:150]}...")
    print("---")

# Fetch a specific article by URL
article = nyt_scraper.fetch_article("https://www.nytimes.com/2024/03/09/world/europe/example-article.html")
if article:
    print(f"Title: {article.title}")
    print(f"Content: {article.content}")
```

### Using Proxies

```python
from news_scraper import NYTimesScraper

# Configure proxies
proxies = {
    'http': 'http://your-proxy-server:port',
    'https': 'https://your-proxy-server:port'
}

# Create a scraper with proxy support
scraper = NYTimesScraper(proxies=proxies)

# Use the scraper as normal
articles = scraper.fetch_latest_articles(limit=3)
```

### Creating a Custom Scraper

You can create a custom scraper for any news source by extending the `NewsScraper` base class:

```python
from news_scraper import NewsScraper
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional

class CustomNewsScraper(NewsScraper):
    def __init__(self, proxies=None):
        super().__init__('https://www.example-news.com', proxies=proxies)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        # Implement title extraction logic for your news source
        title_tag = soup.find('h1', {'class': 'article-title'})
        return title_tag.text.strip() if title_tag else "Unknown Title"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        # Implement content extraction logic for your news source
        article_div = soup.find('div', {'class': 'article-content'})
        if article_div:
            paragraphs = article_div.find_all('p')
            return ' '.join([p.text.strip() for p in paragraphs])
        return ""
    
    # Implement other extraction methods as needed
    
    def _get_article_urls(self, limit: int) -> List[str]:
        # Implement logic to get latest article URLs
        try:
            response = self._make_request(self.base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            article_links = []
            # Find and collect article links
            # ...
            
            return article_links[:limit]
        except Exception as e:
            self.logger.error(f"Error getting article URLs: {str(e)}")
            return []
```

## Best Practices

1. **Respect Rate Limits**: The scraper includes built-in rate limiting, but be considerate and don't overload websites with requests.

2. **Check Terms of Service**: Always check a website's terms of service and robots.txt before scraping.

3. **Use Proxies**: For extensive scraping, consider using proxies to distribute requests.

4. **Handle Errors Gracefully**: The scraper includes error handling, but be prepared to handle site-specific issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for educational and research purposes only. Always respect website terms of service and robots.txt files. The authors are not responsible for any misuse of this tool. 