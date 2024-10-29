import scrapy
from mySpider.items import CoinHistory5MinCMC
import json
from datetime import datetime

def iso8601_to_timestamp(date_string):
    dt = datetime.strptime(date_string.rstrip('Z'), "%Y-%m-%dT%H:%M:%S.%f")
    timestamp = int(dt.timestamp())

    return timestamp

class CryptoHistory5MinSpider(scrapy.Spider):
    # 爬取CMC的价格数据 5min间隔
    name = 'cryptohistory5min'
    allowed_domains = ['api.coinmarketcap.com']
    
    custom_settings = {
        'ITEM_PIPELINES': {'mySpider.pipelines.CoinHistory5minCMCPipeline': 300}
    }

    def start_requests(self):
        with open('/data/scraper_v0/mySpider/mySpider/conf/api_symbol_map_filtered.json') as f:
            coin_list = json.load(f)
        url_template = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id={}&range=1D"
        for coin in coin_list:
            url = url_template.format(coin['id'])
            yield scrapy.Request(url, callback=self.parse, meta=coin)


    def parse(self, response):
        rs = json.loads(response.text)
        history_lists = rs['data']['points']

        rs_id = response.meta.get('id')
        rs_name = response.meta.get('name')
        rs_symbol = response.meta.get('symbol')

        for k, v in history_lists.items():
            if 'c' not in v: # 去掉最后一个时间戳
                continue
            item = CoinHistory5MinCMC()
            item['cmcId'] = rs_id
            item['name'] = rs_name
            item['symbol'] = rs_symbol
            item['date'] = datetime.utcnow().isoformat()[:10]
            item['price'] = v['c'][0]
            item['volume24h'] = v['c'][1]
            item['marketCap'] = v['c'][2]
            item['timestamp'] = int(k)
            yield item

        pass
