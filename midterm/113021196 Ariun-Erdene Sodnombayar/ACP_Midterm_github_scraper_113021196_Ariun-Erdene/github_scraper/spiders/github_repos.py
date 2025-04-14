import scrapy

class GithubSpider(scrapy.Spider):
    name = "github_repos"
    start_urls = ["https://github.com/Ariun-E?tab=repositories"]

    def parse(self, response):
        for repo in response.css('li[itemprop="owns"]'):
            relative_url = repo.css('a[itemprop="name codeRepository"]::attr(href)').get()
            full_url = response.urljoin(relative_url)

            name = relative_url.strip("/").split("/")[-1]

            # Extract initial about text (may be updated later)
            about = repo.css('p[itemprop="description"]::text').get(default='').strip()

            last_updated = repo.css('relative-time::attr(datetime)').get()

            repo_data = {
                "name": name,
                "url": full_url,
                "about": about,  # Use "about" instead of "description"
                "last_updated": last_updated,
                "languages": None,
                "commits": None
            }

            yield scrapy.Request(full_url, callback=self.parse_repo, meta={'repo_data': repo_data})

        next_page = response.css('a.next_page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_repo(self, response):
        repo_data = response.meta['repo_data']

        is_empty = response.css('div.Blankslate').get() is not None

        if not repo_data["about"]:
            if not is_empty:
                repo_data["about"] = repo_data["name"]
            else:
                repo_data["about"] = "No description"

        if is_empty:
            repo_data["languages"] = "None"
            repo_data["commits"] = "None"
        else:
            language_names = response.css('a[href$="languages"] span::text').getall()
            languages = [lang.strip() for lang in language_names if lang.strip()]
            repo_data["languages"] = ', '.join(languages) if languages else "None"

            commits_text = response.css('li a[href$="/commits"] span::text').re_first(r'[\d,]+')
            repo_data["commits"] = commits_text.replace(',', '') if commits_text else "None"

        yield repo_data
