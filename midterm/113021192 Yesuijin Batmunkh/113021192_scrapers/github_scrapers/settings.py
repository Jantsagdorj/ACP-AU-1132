SPIDER_MODULES = ["github_scrapers.spiders"]
NEWSPIDER_MODULE = "github_scrapers.spiders"

ROBOTSTXT_OBEY = False

FEEDS = {
    'github_repos.xml': {
        'format': 'xml',
        'encoding': 'utf-8',
    },
}

LOG_LEVEL = 'ERROR'






