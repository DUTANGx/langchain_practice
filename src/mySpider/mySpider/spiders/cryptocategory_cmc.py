import scrapy
from mySpider.items import CoinCategory
import json
from datetime import datetime

class CryptoCategoryCMCSpider(scrapy.Spider):
    # 爬取CMC的coin分类数据
    name = 'cryptocategorycmc'
    allowed_domains = ['coinmarketcap.com']
    start_urls = ['https://coinmarketcap.com/cryptocurrency-category/']
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    custom_settings = {
        'ITEM_PIPELINES': {'mySpider.pipelines.MyMongoDBPipeline': 300}
    }

    def parse(self, response):
        # 解析一级目录页面获取所有类别的链接
        '''//*[@id="__next"]/div[2]/div[1]/div[2]/div/div[1]/div[2]/table/tbody/tr[xxx]/td[2]/a/p'''
        categories = response.xpath('//*[@id="__next"]/div[2]/div[1]/div[2]/div/div[1]/div[2]/table/tbody/tr')
        for category in categories:
            category_name = category.xpath('td[2]/a/p/text()').get().strip()
            category_url = response.urljoin(category.xpath('td[2]/a/@href').get())

            # 对每个类别的第一页发起请求
            yield scrapy.Request(category_url, callback=self.parse_category_page, meta={'category_name': category_name, 'page_number': 1})

    def parse_category_page(self, response):
        # 目录末尾
        if response.status != 200 or "No data is available now" in response.xpath(
            '//*[@id="__next"]/div[2]/div[1]/div[2]/div/div[1]/div[2]/table/tbody/tr').get():
            return
        # 解析二级目录页面获取所有加密货币的名称
        category_name = response.meta['category_name']
        page_number = response.meta['page_number']
        cryptos = response.xpath('//*[@id="__next"]/div[2]/div[1]/div[2]/div/div[1]/div[2]/table/tbody/tr')
        for crypto in cryptos:
            # format 1
            crypto_symbol = crypto.xpath('td[3]/div/a/div/div/div/div/p/text()').get()
            if crypto_symbol == None:
                # format 2
                crypto_symbol = crypto.xpath('td[3]/a/span[3]/text()').get()
                if crypto_symbol == None:
                    self.logger.error(f"unhandled xpath: {crypto.get()}")
                    continue

            item = CoinCategory()
            item['category'] = category_name
            item['crypto_symbol'] = crypto_symbol
            item['date'] = self.today_date
            yield item
            

        # 继续发起请求
        next_page_number = page_number + 1
        next_page_url = f"{response.url.split('?')[0]}?page={next_page_number}"
        yield scrapy.Request(next_page_url, callback=self.parse_category_page, meta={'category_name': category_name, 'page_number': next_page_number})