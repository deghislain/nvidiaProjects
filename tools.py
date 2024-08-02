from crewai_tools import BaseTool
from crewai_tools import ScrapeWebsiteTool
from typing import TypeAlias

Vector: TypeAlias = list[str]
websites_content = ""


class CustomWebScraperTool(BaseTool):
    name: str = "WebsiteScraper"
    description: str = "Takes a list of websites then scrap and combine their respective content"

    def _run(self, vector: Vector) -> Vector:
        global websites_content
        for link in vector:
            try:
                s_tool = ScrapeWebsiteTool(website_url=link)
                websites_content = websites_content + s_tool.run()
            except Exception as ex:
                print("Error while parsing a link")

        return websites_content
