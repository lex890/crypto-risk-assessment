import scrapy
from scrapy.http import Request
from datetime import datetime, timedelta
import logging

class CryptoNewsSpider(scrapy.Spider):
    name = 'crypto_news'
    allowed_domains = ['coindesk.com', 'cointelegraph.com']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2.0,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2
    }

    def __init__(self, symbol=None, crypto_name=None, callback=None, *args, **kwargs):
        super(CryptoNewsSpider, self).__init__(*args, **kwargs)
        self.symbol = symbol.lower() if symbol else ''
        self.crypto_name = crypto_name.lower() if crypto_name else ''
        self.callback = callback
        self.start_urls = [
            f'https://www.coindesk.com/search?s={self.crypto_name}',
            f'https://cointelegraph.com/search?query={self.crypto_name}'
        ]
        self.cutoff_date = datetime.now() - timedelta(days=30)  # Limit to last 30 days

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, meta={'dont_redirect': True})

    def parse(self, response):
        if 'coindesk.com' in response.url:
            articles = response.css('article.card')
            for article in articles:
                date_str = article.css('time::attr(datetime)').get()
                if date_str:
                    try:
                        article_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                        if article_date < self.cutoff_date:
                            continue
                    except ValueError:
                        continue
                title = article.css('h6.card-title a::text').get(default='').lower()
                if self.crypto_name in title or self.symbol in title:
                    item = {'title': title, 'url': response.urljoin(article.css('h6.card-title a::attr(href)').get())}
                    if self.callback:
                        self.callback(item, response, self)
                    yield item

        elif 'cointelegraph.com' in response.url:
            articles = response.css('article.post-card')
            for article in articles:
                date_str = article.css('time::attr(datetime)').get()
                if date_str:
                    try:
                        article_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                        if article_date < self.cutoff_date:
                            continue
                    except ValueError:
                        continue
                title = article.css('h2.post-card__title a::text').get(default='').lower()
                if self.crypto_name in title or self.symbol in title:
                    item = {'title': title, 'url': response.urljoin(article.css('h2.post-card__title a::attr(href)').get())}
                    if self.callback:
                        self.callback(item, response, self)
                    yield item