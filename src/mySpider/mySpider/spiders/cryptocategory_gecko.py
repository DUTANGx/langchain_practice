import scrapy
from mySpider.items import CoinCategory
import json
from datetime import datetime

headers = {
    'Referer': 'https://www.coingecko.com/en/categories/layer-1',
    'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

class CryptoCategoryCGSpider(scrapy.Spider):
    # 爬取coingecko的coin分类数据
    name = 'cryptocategorycg'
    allowed_domains = ['coingecko.com']
    start_urls = ['https://www.coingecko.com/en/categories']
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    custom_settings = {
        'ITEM_PIPELINES': {'mySpider.pipelines.MyMongoDBPipeline': 300}
    }

    first_level_page = 1

    def parse(self, response):
        # 解析一级目录页面获取所有类别的链接
        '''/html/body/div[3]/main/div[2]/div/div/div[1]/table/tbody/tr[1]/td[2]/b/a'''
        categories = response.xpath('/html/body/div[3]/main/div[2]/div/div/div[1]/table/tbody/tr')
        for category in categories:
            category_name = category.xpath('td[2]/b/a/text()').get().strip()
            category_url = response.urljoin(category.xpath('td[2]/b/a/@href').get())

            # 对每个类别的第一页发起请求
            yield scrapy.Request(category_url, callback=self.parse_category_page, meta={'category_name': category_name, 'page_number': 1})

        if self.first_level_page < 3:
            self.first_level_page += 1
            yield scrapy.Request(f'https://www.coingecko.com/en/categories?page={self.first_level_page}', headers=headers, callback=self.parse)

    def parse_category_page(self, response):
        # 目录末尾
        if response.status != 200 or "The page you're looking for could not be found" in response.get():
            returns
        # 解析二级目录页面获取所有加密货币的名称
        category_name = response.meta['category_name']
        page_number = response.meta['page_number']
        cryptos = response.xpath('/html/body/div[3]/main/div/div[4]/div[1]/div/table/tbody/tr')
        for crypto in cryptos:
            crypto_symbol = crypto.xpath('td[3]/div/a/span[2]/text()').get()
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
        yield scrapy.Request(next_page_url, headers=headers, callback=self.parse_category_page, meta={'category_name': category_name, 'page_number': next_page_number})