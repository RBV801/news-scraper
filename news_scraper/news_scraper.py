"""
news_scraper.py - A flexible and robust web scraper for news articles

This module provides classes for scraping news articles from various sources.
It includes a base scraper class that can be extended for specific news sites.

Features:
- Fetch individual articles by URL
- Fetch latest articles from a news source
- Extract article metadata (title, content, author, date)
- Handle errors gracefully
- User-agent rotation to avoid blocking
- Rate limiting to be respectful to servers
- Proxy support (optional)

Dependencies:
- beautifulsoup4
- requests
- python-dateutil
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
from datetime import datetime
import time
import random
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('news_scraper')

class NewsArticle:
    """
    Represents a news article with its metadata.
    
    Attributes:
        title (str): The title of the article
        content (str): The main content of the article
        url (str): The URL of the article
        source (str): The source/publisher of the article
        author (str, optional): The author of the article
        date (datetime, optional): The publication date
        summary (str, optional): A short summary of the article
        categories (List[str], optional): Categories or tags for the article
    """
    def __init__(self, 
                 title: str, 
                 content: str, 
                 url: str, 
                 source: str, 
                 author: Optional[str] = None, 
                 date: Optional[datetime] = None,
                 summary: Optional[str] = None,
                 categories: Optional[List[str]] = None):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.author = author
        self.date = date
        self.summary = summary
        self.categories = categories or []

    def to_dict(self) -> Dict:
        """Convert the article to a dictionary representation."""
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'author': self.author,
            'date': self.date.isoformat() if self.date else None,
            'summary': self.summary,
            'categories': self.categories
        }
    
    def __str__(self) -> str:
        """String representation of the article."""
        return f"{self.title} - {self.source} - {self.date}"

class NewsScraper:
    """
    Base class for news scrapers.
    
    This class provides common functionality for scraping news articles.
    It should be subclassed for specific news sources.
    
    Attributes:
        base_url (str): The base URL of the news source
        headers (Dict[str, str]): HTTP headers to use for requests
        user_agents (List[str]): List of user agents to rotate through
        proxies (Dict[str, str], optional): Proxy configuration for requests
        rate_limit (float): Minimum time between requests in seconds
    """
    def __init__(self, 
                 base_url: str, 
                 user_agents: Optional[List[str]] = None,
                 proxies: Optional[Dict[str, str]] = None,
                 rate_limit: float = 1.0):
        self.base_url = base_url
        self.last_request_time = 0
        self.rate_limit = rate_limit
        
        # Default user agents to rotate through
        self.user_agents = user_agents or [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
        ]
        
        # Set initial headers with a random user agent
        self.headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Proxy configuration (optional)
        self.proxies = proxies
        
        # Domain for rate limiting
        self.domain = urlparse(base_url).netloc
        
        logger.info(f"Initialized scraper for {self.domain}")

    def _rotate_user_agent(self):
        """Rotate the user agent to avoid detection."""
        self.headers['User-Agent'] = random.choice(self.user_agents)
        
    def _respect_rate_limit(self):
        """Ensure we respect the rate limit for the domain."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()

    def _make_request(self, url: str) -> requests.Response:
        """
        Make an HTTP request with rate limiting and user agent rotation.
        
        Args:
            url: The URL to request
            
        Returns:
            Response object from requests
            
        Raises:
            requests.RequestException: If the request fails
        """
        self._respect_rate_limit()
        self._rotate_user_agent()
        
        logger.debug(f"Making request to {url}")
        response = requests.get(
            url, 
            headers=self.headers, 
            proxies=self.proxies
        )
        response.raise_for_status()
        
        return response

    def fetch_article(self, url: str) -> Optional[NewsArticle]:
        """
        Fetch and parse a single article.
        
        Args:
            url: The URL of the article to fetch
            
        Returns:
            NewsArticle object or None if fetching fails
        """
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # These selectors should be overridden in subclasses for specific sites
            title = self._extract_title(soup)
            content = self._extract_content(soup)
            author = self._extract_author(soup)
            date = self._extract_date(soup)
            summary = self._extract_summary(soup)
            categories = self._extract_categories(soup)
            
            return NewsArticle(
                title=title,
                content=content,
                url=url,
                source=self.domain,
                author=author,
                date=date,
                summary=summary,
                categories=categories
            )
        except Exception as e:
            logger.error(f"Error fetching article {url}: {str(e)}")
            return None

    def fetch_latest_articles(self, limit: int = 10) -> List[NewsArticle]:
        """
        Fetch latest articles from the news source.
        
        Args:
            limit: Maximum number of articles to fetch
            
        Returns:
            List of NewsArticle objects
        """
        try:
            article_urls = self._get_article_urls(limit)
            articles = []
            
            for url in article_urls:
                article = self.fetch_article(url)
                if article:
                    articles.append(article)
                    
                    # Check if we've reached the limit
                    if len(articles) >= limit:
                        break
                        
            return articles
        except Exception as e:
            logger.error(f"Error fetching latest articles: {str(e)}")
            return []
    
    # Methods to be implemented by subclasses
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the title from the article HTML."""
        title_tag = soup.find('h1')
        return title_tag.text.strip() if title_tag else "Unknown Title"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the content from the article HTML."""
        paragraphs = soup.find_all('p')
        return ' '.join([p.text.strip() for p in paragraphs])
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the author from the article HTML."""
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract the publication date from the article HTML."""
        return None
    
    def _extract_summary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the summary from the article HTML."""
        return None
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract the categories from the article HTML."""
        return []
    
    def _get_article_urls(self, limit: int) -> List[str]:
        """
        Get URLs of the latest articles.
        
        This method should be implemented by subclasses.
        
        Args:
            limit: Maximum number of URLs to return
            
        Returns:
            List of article URLs
        """
        # This is a placeholder implementation
        # Subclasses should override this method
        return []

class NYTimesScraper(NewsScraper):
    """
    Scraper for The New York Times.
    
    This class implements the specific scraping logic for nytimes.com.
    """
    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        super().__init__('https://www.nytimes.com', proxies=proxies)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the title from NYTimes article."""
        title_tag = soup.find('h1', {'data-testid': 'headline'})
        if not title_tag:
            title_tag = soup.find('h1')
        return title_tag.text.strip() if title_tag else "Unknown Title"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the content from NYTimes article."""
        article_section = soup.find('section', {'name': 'articleBody'})
        if article_section:
            paragraphs = article_section.find_all('p')
        else:
            paragraphs = soup.find_all('p', {'class': 'css-axufdj'})
        
        return ' '.join([p.text.strip() for p in paragraphs])
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the author from NYTimes article."""
        author_tag = soup.find('span', {'itemprop': 'name'})
        if not author_tag:
            author_tag = soup.find('span', {'class': 'byline-author'})
        return author_tag.text.strip() if author_tag else None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract the publication date from NYTimes article."""
        try:
            date_tag = soup.find('time')
            if date_tag and date_tag.get('datetime'):
                return datetime.fromisoformat(date_tag['datetime'].replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Error parsing date: {str(e)}")
        return None
    
    def _extract_summary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the summary from NYTimes article."""
        summary_tag = soup.find('p', {'id': 'article-summary'})
        if not summary_tag:
            summary_tag = soup.find('p', {'class': 'css-w6ymp8'})
        return summary_tag.text.strip() if summary_tag else None
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract the categories from NYTimes article."""
        categories = []
        section_tag = soup.find('meta', {'property': 'article:section'})
        if section_tag and section_tag.get('content'):
            categories.append(section_tag['content'])
        
        # Look for keywords
        keyword_tags = soup.find_all('meta', {'property': 'article:tag'})
        for tag in keyword_tags:
            if tag.get('content'):
                categories.append(tag['content'])
                
        return categories
    
    def _get_article_urls(self, limit: int) -> List[str]:
        """Get URLs of the latest NYTimes articles."""
        try:
            response = self._make_request(self.base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            article_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Check if it's an article link
                if href.startswith('/'):
                    if '/2023/' in href or '/2024/' in href:  # Year in URL indicates article
                        full_url = f"{self.base_url}{href}"
                        if full_url not in article_links:
                            article_links.append(full_url)
                            
                            if len(article_links) >= limit:
                                break
            
            return article_links
        except Exception as e:
            logger.error(f"Error getting article URLs: {str(e)}")
            return []

class BBCScraper(NewsScraper):
    """
    Scraper for BBC News.
    
    This class implements the specific scraping logic for bbc.com/news.
    """
    def __init__(self, proxies: Optional[Dict[str, str]] = None):
        super().__init__('https://www.bbc.com/news', proxies=proxies)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the title from BBC article."""
        title_tag = soup.find('h1', {'id': 'main-heading'})
        return title_tag.text.strip() if title_tag else "Unknown Title"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract the content from BBC article."""
        article_body = soup.find('article')
        if article_body:
            paragraphs = article_body.find_all('p')
            return ' '.join([p.text.strip() for p in paragraphs])
        return ""
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the author from BBC article."""
        author_tag = soup.find('div', {'class': 'ssrcss-68pt20-Text-TextContributorName'})
        return author_tag.text.strip() if author_tag else None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract the publication date from BBC article."""
        try:
            time_tag = soup.find('time')
            if time_tag and time_tag.get('datetime'):
                return datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Error parsing date: {str(e)}")
        return None
    
    def _get_article_urls(self, limit: int) -> List[str]:
        """Get URLs of the latest BBC articles."""
        try:
            response = self._make_request(self.base_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            article_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Check if it's an article link
                if href.startswith('/news/') and '-' in href:
                    # BBC article URLs typically have a format like /news/world-europe-12345678
                    if href not in article_links:
                        if not href.startswith('http'):
                            href = f"https://www.bbc.com{href}"
                        article_links.append(href)
                        
                        if len(article_links) >= limit:
                            break
            
            return article_links
        except Exception as e:
            logger.error(f"Error getting article URLs: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    # Example with NYTimes
    nyt_scraper = NYTimesScraper()
    print("Fetching latest NYTimes articles...")
    nyt_articles = nyt_scraper.fetch_latest_articles(limit=3)
    
    for i, article in enumerate(nyt_articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article.title}")
        print(f"Author: {article.author}")
        print(f"Date: {article.date}")
        print(f"URL: {article.url}")
        print(f"Summary: {article.summary}")
        print(f"Categories: {', '.join(article.categories)}")
        print(f"Content preview: {article.content[:150]}...")
    
    # Example with BBC
    bbc_scraper = BBCScraper()
    print("\nFetching latest BBC articles...")
    bbc_articles = bbc_scraper.fetch_latest_articles(limit=3)
    
    for i, article in enumerate(bbc_articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article.title}")
        print(f"Author: {article.author}")
        print(f"Date: {article.date}")
        print(f"URL: {article.url}")
        print(f"Content preview: {article.content[:150]}...") 