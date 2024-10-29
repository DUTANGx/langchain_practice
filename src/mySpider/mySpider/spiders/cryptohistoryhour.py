import scrapy
from mySpider.items import CoinHistoryCMC
import json
from datetime import datetime

def iso8601_to_timestamp(date_string):
    dt = datetime.strptime(date_string.rstrip('Z'), "%Y-%m-%dT%H:%M:%S.%f")
    timestamp = int(dt.timestamp())

    return timestamp

class CryptoHistoryHourSpider(scrapy.Spider):
    # 爬取CMC的价格数据 1H间隔
    name = 'cryptohistoryhour'
    allowed_domains = ['api.coinmarketcap.com']
    gap_time = 86400 * 5 # 小时级按5天取数
    custom_settings = {
        'ITEM_PIPELINES': {'mySpider.pipelines.MyMongoDBPipeline': 300}
    }

    def start_requests(self):
        arg1 = int(getattr(self, 'fromstart', 0))  # 控制参数 是否从头开始 还是从近5天
        print('##### arg fromstart is ', arg1)
        arg2 = float(getattr(self, 'days', 5))  # 控制参数 是否从头开始 还是从近5天
        print('##### arg days is ', arg2)
        self.gap_time = int(86400 * arg2)
        with open('/data/mySpider/mySpider/conf/api_symbol_map_filtered_v2_for_hour.json') as f:
            coin_list = json.load(f)
        # 1. 循环coin list  2. 根据日期循环
        urls = []
        for coin in coin_list:
            # 从最近5天开始，用于跑批
            timeStart = iso8601_to_timestamp(datetime.utcnow().isoformat()) - self.gap_time
            if arg1 == 1 and 'first_historical_data' in coin.keys():
                # 从头开始
                timeStart = iso8601_to_timestamp(coin['first_historical_data'])
            timeEnd = timeStart + self.gap_time

            # 爬到下一个timegap
            while timeEnd <= iso8601_to_timestamp(datetime.utcnow().isoformat()) + self.gap_time:
                urls.append(
                    'https://api.coinmarketcap.com/data-api/v3.1/cryptocurrency/historical?id={}&convertId=2781&timeStart={}&timeEnd={}&interval=1h'.format(
                        coin['id'], timeStart, timeEnd))
                timeStart = timeEnd
                timeEnd = timeStart + self.gap_time


        for url in urls:
            print(url)
            yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):
        rs = json.loads(response.text)
        history_lists = rs['data']['quotes']

        rs_id = rs['data']['id']
        rs_name = rs['data']['name']
        rs_symbol = rs['data']['symbol']

        for i in history_lists:
            item = CoinHistoryCMC()
            item['cmcId'] = rs_id
            item['name'] = rs_name
            item['symbol'] = rs_symbol
            item['date'] = i['quote']['timestamp'][:10]
            item['timeOpen'] = i['timeOpen']
            item['timeClose'] = i['timeClose']
            item['timeHigh'] = i['timeHigh']
            item['timeLow'] = i['timeLow']
            item['open'] = i['quote']['open']
            item['high'] = i['quote']['high']
            item['low'] = i['quote']['low']
            item['close'] = i['quote']['close']
            item['volume'] = i['quote']['volume']
            item['marketCap'] = i['quote']['marketCap']
            item['timestamp'] = iso8601_to_timestamp(i['quote']['timestamp'])
            yield item

        pass
