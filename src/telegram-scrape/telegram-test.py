from pymongo import MongoClient, UpdateOne
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

# mongo args
mongo_client = MongoClient('mongodb://admin:Qwe123!!!@43.134.11.45:27017/?authSource=admin')
mongo_db = mongo_client['scrapy']
mongo_collection = mongo_db['telegram']

# telethon args
api_id = '29558706'
api_hash = '5bf57f11f2592f7b49166e90a03f4683'
phone_number = '+8618627185071'
client = TelegramClient('session_name', api_id, api_hash)

async def get_channel_id(username):
    await client.start(phone=phone_number)
    entity = await client.get_entity(username)
    print(f'Channel ID: {entity.id}')
    print(f'Channel Username: {entity.username}')

async def get_latest_messages(channel_name, n_messages):
    await client.start(phone=phone_number)
    
    # Get the entity for the given channel name
    entity = await client.get_entity(channel_name)
    print(f'Channel ID: {entity.id}')
    print(f'Channel Username: {entity.username}')
    
    messages = client.iter_messages(
                entity,
                limit=n_messages
                # min_id=your_post_id,
                # reverse=True
            )

    async for message in messages:
        data = {
            'ID'            : f'{entity.id}-{message.id}',
            'date'          : message.date.strftime('%Y-%m-%d'),
            'timestamp'     : int(message.date.timestamp()),
            'views'         : message.views,
            'forwards'      : message.forwards,
            'message'       : message.text
        }

        mongo_collection.update_one(
            {"ID": data["ID"]},  
            {"$set": data},  
            upsert=True  
        )
        print(f'successfully inserted ID: {data["ID"]}')


if __name__ == '__main__':
    # Example usage
    with client:  
        n_messages = 10  # Number of latest messages to fetch
        client.loop.run_until_complete(get_latest_messages('Cryptoy', n_messages))
        client.loop.run_until_complete(get_latest_messages('CryptoVIPsignalTA', n_messages))
        client.loop.run_until_complete(get_latest_messages('cryptoclubpump', n_messages))
        client.loop.run_until_complete(get_latest_messages('bitcoin_industry', n_messages))
        client.loop.run_until_complete(get_latest_messages('megafutures', n_messages))
        client.loop.run_until_complete(get_latest_messages('crypto_miami', n_messages))
        client.loop.run_until_complete(get_latest_messages('chainlinkofficial', 100))
        