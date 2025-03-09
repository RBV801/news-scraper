"""
News Scraper - A flexible and robust web scraper for news articles
"""

from .news_scraper import (
    NewsArticle,
    NewsScraper,
    NYTimesScraper,
    BBCScraper
)

__version__ = '0.1.0'
__all__ = ['NewsArticle', 'NewsScraper', 'NYTimesScraper', 'BBCScraper'] 