# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CryptoRankItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    alias = scrapy.Field()
    market_cap = scrapy.Field()
    link = scrapy.Field()

class CoinHistoryCMC(scrapy.Item):
    cmcId = scrapy.Field()
    name = scrapy.Field()
    symbol = scrapy.Field()
    date = scrapy.Field()
    timeOpen = scrapy.Field()
    timeClose = scrapy.Field()
    timeHigh = scrapy.Field()
    timeLow = scrapy.Field()
    open = scrapy.Field()
    high = scrapy.Field()
    low = scrapy.Field()
    close = scrapy.Field()
    volume = scrapy.Field()
    marketCap = scrapy.Field()
    timestamp = scrapy.Field()
    
class CoinHistory5MinCMC(scrapy.Item):
    cmcId = scrapy.Field()
    name = scrapy.Field()
    symbol = scrapy.Field()
    date = scrapy.Field()
    price = scrapy.Field()
    volume24h = scrapy.Field()
    marketCap = scrapy.Field()
    timestamp = scrapy.Field()

class CoinCategory(scrapy.Item):
    category = scrapy.Field()
    crypto_symbol = scrapy.Field()
    date = scrapy.Field()