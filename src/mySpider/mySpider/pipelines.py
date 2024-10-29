# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from itemadapter import ItemAdapter
from influxdb import InfluxDBClient
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

class CoinHistoryCMCPipeline:
    def __init__(self):
        settings = get_project_settings()
        self.influxdb_host = settings.get('INFLUXDB_HOST', 'localhost')
        self.influxdb_port = settings.get('INFLUXDB_PORT', 8086)
        self.influxdb_database = settings.get('INFLUXDB_DATABASE')
        # self.influxdb_username = settings.get('INFLUXDB_USERNAME')
        # self.influxdb_password = settings.get('INFLUXDB_PASSWORD')
        # self.influxdb_measurement = spider.name
        # Initialize InfluxDB client
        self.client = InfluxDBClient(
            host=self.influxdb_host,
            port=self.influxdb_port,
            # username=self.influxdb_username,
            # password=self.influxdb_password,
            database=self.influxdb_database
        )

        # Ensure database exists
        if self.influxdb_database not in [db['name'] for db in self.client.get_list_database()]:
            self.client.create_database(self.influxdb_database)

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_item(self, item, spider):
        json_body = [
            {
                "measurement": spider.name,
                "tags": {
                    "cmcId": item['cmcId'],
                    "name": item['name'],
                    "symbol": item['symbol']
                },
                "time": item['timestamp'],
                "fields": {
                    "date": item['date'],
                    "timeOpen": item['timeOpen'],
                    "timeClose": item['timeClose'],
                    "timeHigh": item['timeHigh'],
                    "timeLow": item['timeLow'],
                    "open": item['open'],
                    "high": item['high'],
                    "low": item['low'],
                    "close": item['close'],
                    "volume": item['volume'],
                    "marketCap": item['marketCap'],
                    "timestamp": item['timestamp']
                }
            }
        ]

        try:
            self.client.write_points(json_body)
            return item
        except Exception as e:
            raise DropItem(f"Failed to write item to InfluxDB: {e}")

class CoinHistory5minCMCPipeline:
    def __init__(self):
        settings = get_project_settings()
        self.influxdb_host = settings.get('INFLUXDB_HOST', 'localhost')
        self.influxdb_port = settings.get('INFLUXDB_PORT', 8086)
        self.influxdb_database = settings.get('INFLUXDB_DATABASE')
        self.client = InfluxDBClient(
            host=self.influxdb_host,
            port=self.influxdb_port,
            database=self.influxdb_database
        )

        # Ensure database exists
        if self.influxdb_database not in [db['name'] for db in self.client.get_list_database()]:
            self.client.create_database(self.influxdb_database)

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_item(self, item, spider):
        json_body = [
            {
                "measurement": spider.name,
                "tags": {
                    "cmcId": item['cmcId'],
                    "name": item['name'],
                    "symbol": item['symbol']
                },
                "time": item['timestamp'],
                "fields": {
                    "date": item['date'],
                    "close": item['price'],
                    "volume": item['volume24h'],
                    "marketCap": item['marketCap'],
                    "timestamp": item['timestamp']
                }
            }
        ]

        try:
            self.client.write_points(json_body)
            return item
        except Exception as e:
            raise DropItem(f"Failed to write item to InfluxDB: {e}")


class MyspiderPipeline:
    def process_item(self, item, spider):
        return item


class MyMongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DATABASE', 'scrapy')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        try:
            collection.insert_one(dict(item))
        except pymongo.errors.DuplicateKeyError:
            # 处理重复记录的逻辑
            print("WARNING: DUPLICATE DATA!")
            pass
        return item
