from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="news-scraper",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A flexible and robust web scraper for news articles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/news-scraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    python_requires=">=3.8",
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "requests>=2.25.0",
        "python-dateutil>=2.8.0",
    ],
) 