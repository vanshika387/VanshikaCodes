
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# uri = "mongodb+srv://vanshika:vanshika1912@rssfeeds.8fabwtf.mongodb.net/?retryWrites=true&w=majority&appName=RSSFeeds"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)




























from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://vanshika:vanshika1912@rssfeeds.8fabwtf.mongodb.net/?retryWrites=true&w=majority&appName=RSSFeeds"


client = MongoClient(uri, server_api=ServerApi('1'))


try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    
    db = client['RSSFeeds']  
    collection = db['your_collection_name']  

    # Example data to insert into the collection
    data_list = [
    {
        "title": "First RSS Feed",
        "link": "https://example.com/feed1",
        "description": "First feed description",
        "published_at": "2025-05-15T12:00:00Z"
    },
    {
        "title": "Second RSS Feed",
        "link": "https://example.com/feed2",
        "description": "Second feed description",
        "published_at": "2025-05-16T12:00:00Z"
    },
    {
        "title": "Third RSS Feed",
        "link": "https://example.com/feed3",
        "description": "Third feed description",
        "published_at": "2025-05-17T12:00:00Z"
    },
    {
        "title": "Fourth RSS Feed",
        "link": "https://example.com/feed4",
        "description": "Fourth feed description",
        "published_at": "2025-05-18T12:00:00Z"
    },
    {
        "title": "Fifth RSS Feed",
        "link": "https://example.com/feed5",
        "description": "Fifth feed description",
        "published_at": "2025-05-19T12:00:00Z"
    },
    {
        "title": "Sixth RSS Feed",
        "link": "https://example.com/feed6",
        "description": "Sixth feed description",
        "published_at": "2025-05-20T12:00:00Z"
    },
    {
        "title": "Seventh RSS Feed",
        "link": "https://example.com/feed7",
        "description": "Seventh feed description",
        "published_at": "2025-05-21T12:00:00Z"
    },
    {
        "title": "Eighth RSS Feed",
        "link": "https://example.com/feed8",
        "description": "Eighth feed description",
        "published_at": "2025-05-22T12:00:00Z"
    }
]
    result = collection.insert_many(data_list)
    print(f"Documents inserted with _ids: {result.inserted_ids}")
    
except Exception as e:
    print(e)

finally:
    client.close()
    print("Connection closed.")
