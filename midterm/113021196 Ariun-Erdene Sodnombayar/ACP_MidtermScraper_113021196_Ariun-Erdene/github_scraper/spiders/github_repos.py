import scrapy


class GithubSpider(scrapy.Spider):
    name = "github"
    start_urls = ["https://github.com/Ariun-E?tab=repositories"]

    # Feed Exporter configuration for XML output
    custom_settings = {
        "FEEDS": {
            "repos.xml": {
                "format": "xml",
                "encoding": "utf-8",
                "fields": ["url", "about", "last_updated", "languages", "commits"],
                "store_empty": False,
                "indent": 4
            }
        },
    }

    def parse(self, response):
        for repo in response.css('li[itemprop="owns"]'):
            relative_url = repo.css('a::attr(href)').get()
            full_url = response.urljoin(relative_url)
            about = repo.css('p::text').get(default='').strip()
            last_updated = repo.css('relative-time::attr(datetime)').get()

            repo_data = {
                "url": full_url,
                "about": about if about else relative_url.strip('/').split('/')[-1],
                "last_updated": last_updated,
                "languages": None,
                "commits": None
            }

            yield scrapy.Request(full_url, meta={"repo_data": repo_data}, callback=self.parse_repo)

        # Handle pagination
        next_page = response.css('a.next_page::attr(href)').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_repo(self, response):
        repo_data = response.meta["repo_data"]

        # Check if the repository is empty
        is_empty = response.css('div.Blankslate').get() is not None

        if is_empty:
            repo_data["languages"] = "None"
            repo_data["commits"] = "None"
        else:
            # Extract languages
            language_names = response.css('a[href$="languages"] span::text').getall()
            repo_data["languages"] = ', '.join([lang.strip() for lang in language_names if lang.strip()]) or "None"

            # Extract number of commits
            commit_count = response.css('li a[href$="commits"] span::text').re_first(r'\d[\d,]*')
            repo_data["commits"] = commit_count.replace(',', '') if commit_count else "None"

        yield repo_data