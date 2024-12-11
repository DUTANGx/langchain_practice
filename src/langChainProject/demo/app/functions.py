import os
import requests
import json

from langchain_community.utilities import GoogleSerperAPIWrapper

os.environ["TAVILY_API_KEY"] = "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"
os.environ["SERPER_API_KEY"] = "575447666cc1aeeb781162501a327aca29467b31"

sector_list = ['a16z Portfolio', 'Ethereum Ecosystem', 'Oracles', 'AI & Big Data', 
                'Fantom Ecosystem', 'Play To Earn', 'Arbitrum Ecosystem', 'Gaming', 
                'Polkadot Ecosystem', 'Avalanche Ecosystem', 'Generative AI', 
                'Polygon Ecosystem', 'Binance Launchpad', 'Identity', 'Privacy', 
                'Bitcoin Ecosystem', 'Injective Ecosystem', 'Real World Assets', 
                'BNB Chain Ecosystem', 'Interoperability', 'Restaking', 'BRC-20', 
                'Layer 1', 'Rollups', 'Cardano Ecosystem', 'Layer 2', 'Scaling', 
                'Centralized Exchange (CEX) Token', 'Marketplace', 'Smart Contracts', 
                'Cosmos Ecosystem', 'Memes', 'Solana Ecosystem', 'Data Availability', 
                'Metaverse', 'Storage', 'Decentralized Exchange (DEX) Token', 
                'Modular Blockchain', 'Telegram Bot', 'DeFi 2.0', 'Moonriver Ecosystem', 
                'VRAR', 'DeFi', 'Near Protocol Ecosystem', 'Zero Knowledge Proofs', 
                'DePIN', 'NFTs & Collectibles', 'DeSci', 'Optimism Ecosystem']

search = GoogleSerperAPIWrapper()

with open("api_symbol_map_filtered_v2_for_hour.json", "r") as f:
    symbol_map_json = json.load(f)
    symbol_map = {x['symbol']:str(x['id']) for x in symbol_map_json}

def current_price(symbol: str):
    '''get latest price and other statistics of given symbol'''
    if symbol not in symbol_map:
        # todo add log
        _err = "ERROR: symbol {} not in list.".format(symbol)
        print(_err)
        return _err
    symbol_id = symbol_map.get(symbol)
    req_format = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/?id={}"
    req = req_format.format(symbol_id)
    res = requests.get(url=req).json()
    utc_time = res["status"]["timestamp"]
    statistics = res["data"]["statistics"]
    ret = {"current_timestamp": utc_time,
           "current_price(USD)": statistics["price"],
           "current_priceChangePercentage1h": statistics["priceChangePercentage1h"],
           "current_priceChangePercentage24h": statistics["priceChangePercentage24h"],
           "current_priceChangePercentage7d": statistics["priceChangePercentage7d"],
           "highAllTime_price(USD)": statistics["highAllTime"],
           "highAllTime_timestamp": statistics["highAllTimeTimestamp"],
           "highAllTime_ChangePercentage": statistics["highAllTimeChangePercentage"],
           "lowAllTime_price(USD)": statistics["lowAllTime"],
           "lowAllTime_timestamp": statistics["lowAllTimeTimestamp"],
           "lowAllTime_ChangePercentage": statistics["lowAllTimeChangePercentage"]
           }
    return json.dumps(ret)

def sentiment_indicator(symbol:str):
    '''get sentiment score of given symbol, can be cryptocoin or sector'''
    if symbol in symbol_map:
        # cryptocoin
        req_format = "https://www.alphabrain.app/api/getCryptoData?symbol={}&dataType=crypto&fullHistory=true"
        req = req_format.format(symbol)
        res = requests.get(url=req).json()["data"][-7:]
        return json.dumps(res)

    if symbol in sector_list:
        # cryptocoin sector
        req_format = "https://www.alphabrain.app/api/getCryptoData?symbol={}&dataType=category"
        req = req_format.format(symbol)
        res = requests.get(url=req).json()["data"][-7:]
        return json.dumps(res)

    # if not in coin list or sector list
    # todo add log
    _err = "ERROR: symbol {} not in service list.".format(symbol)
    print(_err)
    return _err