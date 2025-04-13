# Scrapy settings for github_scraper project

BOT_NAME = "github_scraper"

SPIDER_MODULES = ["github_scraper.spiders"]
NEWSPIDER_MODULE = "github_scraper.spiders"

# Don't obey robots.txt (GitHub blocks scrapers by default)
ROBOTSTXT_OBEY = False

# Set headers to simulate a browser visit
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Delay to prevent GitHub from blocking you
DOWNLOAD_DELAY = 1

# Enable Feed export (XML output)
FEEDS = {
    'repos.xml': {
        'format': 'xml',
        'encoding': 'utf8',
        'fields': ['name', 'url', 'description', 'last_updated', 'languages', 'commits'],
        'indent': 4,
        "xml_declaration": True,
    }
}