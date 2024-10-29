import scrapy
from mySpider.items import CoinHistoryCMC
import json
from datetime import datetime

def iso8601_to_timestamp(date_string):
        # 尝试第一种格式
    try:
        # 对于不包含毫秒的时间字符串
        dt = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        # 尝试第二种格式，包含毫秒和Z指示的UTC时间
        try:
            dt = datetime.strptime(date_string.rstrip('Z'), "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            # 如果都不匹配，抛出异常
            raise ValueError("时间格式不符合预期")
    return int(dt.timestamp())

    return timestamp

class CryptoHistoryDaySpider(scrapy.Spider):
    # 爬取CMC的价格数据 1D间隔
    name = 'cryptohistoryday'
    allowed_domains = ['api.coinmarketcap.com']
    gap_time = 86400 * 120
    custom_settings = {
        'ITEM_PIPELINES': {'mySpider.pipelines.MyMongoDBPipeline': 300}
    }

    def start_requests(self):
        arg1 = int(getattr(self, 'fromstart', 0))  # 控制参数 是否从头开始 还是从近5天
        print('##### arg fromstart is ', arg1)
        arg2 = int(getattr(self, 'days', 5))  # 控制参数 是否从头开始 还是从近5天
        print('##### arg days is ', arg2)
        self.gap_time = 86400 * arg2
        with open('/data/mySpider/mySpider/conf/api_symbol_map_filtered_v2.json') as f:
            coin_list = json.load(f)
        # coin list 排序 提前部分coin
        value_cryptos = [
            {"symbol": 1, "name": "BTC"},
            {"symbol": 1027, "name": "ETH"},
            {"symbol": 1839, "name": "BNB"},
            {"symbol": 3897, "name": "OKB"},
            {"symbol": 1831, "name": "BCH"},
            {"symbol": 1765, "name": "EOS"},
            {"symbol": 52, "name": "XRP"},
            {"symbol": 2, "name": "LTC"},
            {"symbol": 1975, "name": "LINK"},
            {"symbol": 5426, "name": "SOL"},
            {"symbol": 74, "name": "DOGE"},
            {"symbol": 2010, "name": "ADA"},
            {"symbol": 5994, "name": "SHIB"},
            {"symbol": 1958, "name": "TRX"},
            {"symbol": 6636, "name": "DOT"},
            {"symbol": 5805, "name": "AVAX"},
            {"symbol": 11419, "name": "TON"},
            {"symbol": 7083, "name": "UNI"},
            {"symbol": 5690, "name": "RNDR"},
            {"symbol": 3890, "name": "MATIC"}
        ]
        symbol_set = {item['symbol'] for item in value_cryptos}
        coin_list = sorted(coin_list, key=lambda item: (item['id'] not in symbol_set, item['id']))

        # 1. 循环coin list  2. 根据日期循环
        urls = []
        for coin in coin_list:
            # 从最近开始，用于跑批
            timeStart = iso8601_to_timestamp(datetime.utcnow().isoformat()) - self.gap_time
            if arg1 == 1:
                # 从头开始
                timeStart = iso8601_to_timestamp(coin.get('first_historical_data', '2023-01-01T00:00:00.000Z'))
            timeEnd = timeStart + self.gap_time

            # 默认爬到下一个timegap
            while timeEnd < iso8601_to_timestamp(datetime.utcnow().isoformat()) + self.gap_time:
                urls.append(
                    'https://api.coinmarketcap.com/data-api/v3.1/cryptocurrency/historical?id={}&convertId=2781&timeStart={}&timeEnd={}&interval=1d'.format(
                        coin['id'], timeStart, timeEnd))
                timeStart = timeEnd
                timeEnd = timeStart + self.gap_time

        for url in urls:
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
