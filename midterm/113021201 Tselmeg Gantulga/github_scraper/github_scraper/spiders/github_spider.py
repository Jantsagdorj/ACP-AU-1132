import scrapy
import json

class GithubSpider(scrapy.Spider):
    name = "github_spider"
    start_urls = ["https://api.github.com/users/113021201/repos"]

    def parse(self, response):
        repos = json.loads(response.text)

        for repo in repos:
            repo_name = repo.get("name")
            html_url = repo.get("html_url")
            about = repo.get("description")
            updated_at = repo.get("updated_at")
            is_empty = repo.get("size", 0) == 0

            # If about is empty but repo is not, use repo name as about
            if not about and not is_empty:
                about = repo_name

            item = {
                "name": repo_name,
                "url": html_url,
                "about": about if about else "None",
                "last_updated": updated_at,
                "languages": None,
                "commits": None,
            }

            if not is_empty:
                languages_url = f"https://api.github.com/repos/113021201/{repo_name}/languages"
                commits_url = f"https://api.github.com/repos/113021201/{repo_name}/commits"

                request = scrapy.Request(
                    url=languages_url,
                    callback=self.parse_languages,
                    meta={"item": item, "commits_url": commits_url}
                )
                yield request
            else:
                yield item

    def parse_languages(self, response):
        item = response.meta["item"]
        commits_url = response.meta["commits_url"]

        languages = list(json.loads(response.text).keys())
        item["languages"] = ", ".join(languages) if languages else "None"

        yield scrapy.Request(
            url=commits_url,
            callback=self.parse_commits,
            meta={"item": item}
        )

    def parse_commits(self, response):
        item = response.meta["item"]
        commits = json.loads(response.text)
        item["commits"] = len(commits) if isinstance(commits, list) else "None"
        yield item