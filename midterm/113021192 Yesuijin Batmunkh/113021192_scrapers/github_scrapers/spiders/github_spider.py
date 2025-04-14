import scrapy
import json
import re


class GitHubSpider(scrapy.Spider):
    name = "github_spider"
    allowed_domains = ["github.com", "api.github.com"]
    start_urls = ["https://github.com/113021192?tab=repositories"]
    github_api_user = "113021192"

    def parse(self, response):
        repo_links = response.css('h3 a::attr(href)').getall()
        for link in repo_links:
            repo_name = link.split("/")[-1]
            repo_url = response.urljoin(link)

            yield scrapy.Request(
                url=repo_url,
                callback=self.parse_html_repo,
                meta={"repo_name": repo_name, "repo_url": repo_url}
            )

    def parse_html_repo(self, response):
        repo_name = response.meta["repo_name"]
        repo_url = response.meta["repo_url"]

        # Extract about section
        about = response.css('p.f4.my-3::text, p.f4.mt-3::text').get()
        if not about:
            if response.css('div.repository-content').get():
                about = response.css('strong[itemprop="name"] a::text').get()
            else:
                about = repo_name  # fallback
        else:
            about = about.strip()

        # Extract languages
        languages = response.css('li.d-inline span::text').getall()
        languages = [lang.strip() for lang in languages if lang.strip()]
        languages = ', '.join(languages) if languages else "None"

        # Request commit count using GitHub API (pagination trick)
        commits_api_url = f"https://api.github.com/repos/{self.github_api_user}/{repo_name}/commits?per_page=1"

        meta_data = {
            "repo_url": repo_url,
            "about": about,
            "languages": languages,
            "repo_name": repo_name
        }

        yield scrapy.Request(
            url=commits_api_url,
            callback=self.parse_commits_count,
            meta=meta_data
        )

    def parse_commits_count(self, response):
        # Use pagination headers to estimate total commits
        link_header = response.headers.get('Link')
        if link_header:
            link_header = link_header.decode()
            match = re.search(r'&page=(\d+)>; rel="last"', link_header)
            if match:
                num_commits = match.group(1)
            else:
                num_commits = "1"
        else:
            num_commits = "1"  # If only one commit or no pagination

        # Fetch last updated date
        api_url = f"https://api.github.com/repos/{self.github_api_user}/{response.meta['repo_name']}"

        meta_data = {
            "repo_url": response.meta["repo_url"],
            "about": response.meta["about"],
            "languages": response.meta["languages"],
            "num_commits": num_commits
        }

        yield scrapy.Request(
            url=api_url,
            callback=self.parse_api_repo,
            meta=meta_data
        )

    def parse_api_repo(self, response):
        data = json.loads(response.text)
        last_updated = data.get("updated_at", "Not available")

        yield {
            "repo_url": response.meta["repo_url"],
            "about": response.meta["about"],
            "last_updated": last_updated,
            "languages": response.meta["languages"],
            "num_commits": response.meta["num_commits"]
        }
