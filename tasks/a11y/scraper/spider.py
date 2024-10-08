import logging
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor, IGNORED_EXTENSIONS
from scrapy.spiders import CrawlSpider, Rule
from .user_agent import USER_AGENT


class A11ySpider(CrawlSpider):
    name = "a11yspider"

    def __init__(self, target=None, data=[]):
        super(A11ySpider, self).__init__(target)
        self.start_urls = [target]
        self.rules = (
            Rule(
                LinkExtractor(
                    allow=f'{target}*',
                    deny_extensions=[*IGNORED_EXTENSIONS, 'xml', 'pdf'],
                    canonicalize=True,
                    unique=True,
                    ),
                callback='parse_item',
                follow=True
            ),
        )
        self.data = data

        # recompile rules:
        # https://stackoverflow.com/questions/27509489/how-to-dynamically-set-scrapy-rules
        super(A11ySpider, self)._compile_rules()

    def parse_item(self, response):
        self.data.append(response.url)


settings = dict(
    BOT_NAME="cloudgovpagescrawler",
    USER_AGENT=USER_AGENT,
    ROBOTSTXT_OBEY=True,
    CONCURRENT_REQUESTS_PER_DOMAIN=16,
    REQUEST_FINGERPRINTER_IMPLEMENTATION="2.7",
    TWISTED_REACTOR="twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    FEED_EXPORT_ENCODING="utf-8",
    LOG_LEVEL=logging.INFO,
)

process = CrawlerProcess(settings)
