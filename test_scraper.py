#!/usr/bin/env python3
"""
Simple tests for the news scraper.
"""
import unittest
from unittest.mock import patch, MagicMock
from news_scraper import NewsArticle, NewsScraper, NYTimesScraper

class TestNewsArticle(unittest.TestCase):
    def test_article_creation(self):
        """Test creating a NewsArticle object."""
        article = NewsArticle(
            title="Test Title",
            content="Test content",
            url="https://example.com/article",
            source="example.com"
        )
        
        self.assertEqual(article.title, "Test Title")
        self.assertEqual(article.content, "Test content")
        self.assertEqual(article.url, "https://example.com/article")
        self.assertEqual(article.source, "example.com")
        self.assertIsNone(article.author)
        self.assertIsNone(article.date)
        
    def test_to_dict(self):
        """Test converting a NewsArticle to a dictionary."""
        article = NewsArticle(
            title="Test Title",
            content="Test content",
            url="https://example.com/article",
            source="example.com",
            author="Test Author",
            categories=["news", "test"]
        )
        
        article_dict = article.to_dict()
        self.assertEqual(article_dict["title"], "Test Title")
        self.assertEqual(article_dict["content"], "Test content")
        self.assertEqual(article_dict["url"], "https://example.com/article")
        self.assertEqual(article_dict["source"], "example.com")
        self.assertEqual(article_dict["author"], "Test Author")
        self.assertIsNone(article_dict["date"])
        self.assertEqual(article_dict["categories"], ["news", "test"])

class TestNewsScraper(unittest.TestCase):
    def setUp(self):
        """Set up a test scraper."""
        self.scraper = NewsScraper("https://example.com")
    
    def test_initialization(self):
        """Test scraper initialization."""
        self.assertEqual(self.scraper.base_url, "https://example.com")
        self.assertEqual(self.scraper.domain, "example.com")
        self.assertIsNotNone(self.scraper.headers)
        self.assertIsNotNone(self.scraper.user_agents)
        
    @patch('requests.get')
    def test_make_request(self, mock_get):
        """Test making a request."""
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_get.return_value = mock_response
        
        response = self.scraper._make_request("https://example.com/test")
        
        mock_get.assert_called_once()
        self.assertEqual(response, mock_response)

class TestNYTimesScraper(unittest.TestCase):
    def setUp(self):
        """Set up a test NYTimes scraper."""
        self.scraper = NYTimesScraper()
    
    def test_initialization(self):
        """Test NYTimes scraper initialization."""
        self.assertEqual(self.scraper.base_url, "https://www.nytimes.com")
        self.assertEqual(self.scraper.domain, "www.nytimes.com")
        
    @patch('news_scraper.NYTimesScraper._make_request')
    def test_extract_title(self, mock_make_request):
        """Test extracting title from NYTimes article."""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <h1 data-testid="headline">Test Headline</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        title = self.scraper._extract_title(soup)
        self.assertEqual(title, "Test Headline")

if __name__ == "__main__":
    unittest.main() 