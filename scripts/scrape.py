"""
Scrape Employment Appeal Tribunal decision pdfs from the gov.uk website

https://www.gov.uk/employment-appeal-tribunal-decisions
"""

import scrapy
from scrapy.http import Request
from scrapy.crawler import CrawlerProcess
from pathlib import Path

data_dir = Path("data/raw")
data_dir.mkdir(parents=True, exist_ok=True)


class EmploymentAppealTribunalSpider(scrapy.Spider):
    name = "employment_appeal_tribunal"
    start_urls = ["https://www.gov.uk/employment-appeal-tribunal-decisions"]

    def parse(self, response):
        for decision in response.css(
            "ul.gem-c-document-list li.gem-c-document-list__item"
        ):
            decision_page = decision.css("a::attr(href)").get()
            yield response.follow(decision_page, self.parse_decision)

        next_page = response.css("a[rel='next']::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_decision(self, response):
        pdf_link = response.css("a[href$='.pdf']::attr(href)").get()
        yield Request(pdf_link, callback=self.save_pdf)

    def save_pdf(self, response):
        pdf_name = response.url.split("/")[-1]
        with open(data_dir / pdf_name, "wb") as f:
            f.write(response.body)
        self.logger.info(f"Saved {pdf_name}")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(EmploymentAppealTribunalSpider)
    process.start()
