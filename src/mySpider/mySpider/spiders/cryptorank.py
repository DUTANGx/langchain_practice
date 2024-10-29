import scrapy
import re
from mySpider.items import CryptoRankItem

# //*[@id="react-white-paper"]/div/div[3]/table/tbody/tr[1]/td[1]/a
# //*[@id="react-white-paper"]/div/div[3]/table/tbody/tr[1]/td[2]/div
# /html/body/div[1]/main/div/div[2]/div/div[4]/div[1]/div/a[7]
# //*[@id="react-white-paper"]/div/div[4]/div[1]/div/a[7]

class CryptorankSpider(scrapy.Spider):
    # 爬取白皮书链接
    name = "cryptorank"
    allowed_domains = ["bitscreener.com"]
    start_urls = ["https://bitscreener.com/whitepaper?p=1"]
    tmp_index = 1
    pattern = r'(.+)\s+\((.+)\)\s+(.+)'
    url_template = 'https://files.bitscreener.com/whitepaper/{}-whitepaper.pdf'

    custom_settings = {
        'ITEM_PIPELINES': {'mySpider.pipelines.MyMongoDBPipeline': 300}
    }

    def parse(self, response):
        
        context = response.xpath('//*[@id="react-white-paper"]/div/div[3]/table/tbody/tr')
        
        for i in context:
            full_name = i.xpath('td[1]/a/text()').extract()[1].strip()
            market_cap = i.xpath('td[2]/div/text()').get().strip()
            print(market_cap)
            matches = re.match(self.pattern, full_name)
            if matches:
                item = CryptoRankItem()
                name = matches.group(1)
                item['name'] = name
                item['alias'] = matches.group(2)
                item['market_cap'] = market_cap.replace('$', '').replace(',', '')
                item['link'] = self.url_template.format(name.lower().replace(' ', '-'))
                yield item
            else:
                print('RE MATCH FAIL: ', full_name)
            
        if self.tmp_index < 6:
            self.tmp_index += 1
            url = 'https://bitscreener.com/whitepaper?p={}'.format(self.tmp_index)
            print('next page: ', url)
            yield scrapy.Request(url=url, method="GET", callback=self.parse)
        