import scrapy

class GithubSpider(scrapy.Spider):
    name = "github_spider"
    start_urls = ["https://github.com/113021192?tab=repositories"]

    def parse(self, response):
        repo_links = response.css('h3 a::attr(href)').getall()
        for link in repo_links:
            repo_url = response.urljoin(link)
            yield scrapy.Request(
                url=repo_url,
                callback=self.parse_repo,
                meta={'repo_url': repo_url}
            )

    def parse_repo(self, response):
        repo_url = response.meta['repo_url']
        about = response.css('p.f4.my-3::text, p.f4.mt-3::text').get()
        if not about:
            if response.css('div.repository-content').get():
                about = response.css('strong[itemprop="name"] a::text').get()
            else:
                about = response.url.split('/')[-1]  # Use repository name as About
        else:
            about = about.strip()

        last_updated = response.css('relative-time::attr(datetime)').get()
        languages = response.css('span[itemprop="programmingLanguage"]::text').getall()
        num_commits = response.css('li.commits span strong::text').re_first(r'\d+')

        if not response.css('div.repository-content').get():
            languages = None
            num_commits = None

        yield {
            'repo_url': repo_url,
            'about': about,
            'last_updated': last_updated,
            'languages': languages,
            'num_commits': num_commits
        }
