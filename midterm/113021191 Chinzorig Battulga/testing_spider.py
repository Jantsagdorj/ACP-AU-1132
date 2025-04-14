import scrapy
import requests
from testing.items import GithubScraperItem

class GithubSpider(scrapy.Spider):
    name = "testing"
    allowed_domains = ["github.com"]
    start_urls = ["https://github.com/Mimikooo?tab=repositories"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
            })

    def parse(self, response):
        repo_links = response.css('h3 a::attr(href)').getall()
        for link in repo_links:
            repo_url = response.urljoin(link)
            yield scrapy.Request(url=repo_url, callback=self.parse_repo, headers={
                'User-Agent': 'Mozilla/5.0'
            })

    def parse_repo(self, response):
        item = GithubScraperItem()
        item['url'] = response.url

        about = response.css('p.f4::text, p.f4 span::text').get()
        about = about.strip() if about else None
        is_empty = response.css('.blankslate').get() is not None

        repo_name = response.url.split('/')[-1]
        owner = response.url.split('/')[-2]
        item['about'] = about if about else (None if is_empty else repo_name)

        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Mozilla/5.0',
        }

        # 1. Get repo details from API
        repo_api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        repo_data = requests.get(repo_api_url, headers=headers).json()

        # 2. last_updated
        item['last_updated'] = repo_data.get('updated_at')

        # 3. languages
        lang_url = f"https://api.github.com/repos/{owner}/{repo_name}/languages"
        lang_data = requests.get(lang_url, headers=headers).json()
        item['languages'] = list(lang_data.keys()) if lang_data else None

        # 4. commits (via pagination)
        commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=1"
        response_api = requests.get(commits_url, headers=headers)

        if 'Link' in response_api.headers:
            links = response_api.headers['Link']
            for link in links.split(','):
                if 'rel="last"' in link:
                    last_url = link[link.find('<')+1:link.find('>')]
                    page_number = int(last_url.split('page=')[-1])
                    item['commits'] = page_number
                    break
            else:
                item['commits'] = 1
        else:
            item['commits'] = len(response_api.json())

        yield item
