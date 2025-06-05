from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')

# Load environment variables
load_dotenv()

# MongoDB Atlas connection setup
def get_mongo_connection(db_name='TimelyFeeds'):
    try:
        uri = os.getenv("MONGODB_URI") or "mongodb+srv://vanshika:vanshika1912@rssfeeds.8fabwtf.mongodb.net/TimelyFeeds?retryWrites=true&w=majority&appName=RSSFeeds"
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')  # Test connection
        return client[db_name]
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        raise

# @app.route('/')
# def index():
#     try:
#         db = get_mongo_connection()
#         collection = db['fact_classified_articles']  # Updated collection name
        
#         # Query MongoDB - get only classified real estate articles, sorted by date
#         articles = list(collection.find(
#             {"classification": True},  # Only show real estate articles
#             {'_id': 0}  # Exclude MongoDB _id field
#         ).sort('link_date', -1).limit(100))  # Limit to 100 most recent
        
#         # Format dates
#         for article in articles:
#             if 'link_date' in article and isinstance(article['link_date'], datetime):
#                 article['link_date'] = article['link_date'].strftime('%Y-%m-%d %H:%M:%S')
        
#         return render_template('index.html', articles=articles)
    
#     except Exception as e:
#         print(f"Error fetching articles: {e}")
#         return render_template('error.html', error=str(e))


# @app.route('/')
# def index():
#     try:
#         db = get_mongo_connection()
#         collection = db['fact_classified_articles']
        
#         # Query MongoDB - get only classified real estate articles, sorted by date
#         articles = list(collection.find(
#             # More flexible query:
#             {"classification": {"$in": [True, "True"]}},  # Only show real estate articles
#             {'_id': 0}  # Exclude MongoDB _id field
#         ).sort('_id', -1).limit(1000))  # Limit to 100 most recent
        
#         # Format dates and ensure useful field exists
#         for article in articles:
#             if 'link_date' in article and isinstance(article['link_date'], datetime):
#                 article['link_date'] = article['link_date'].strftime('%Y-%m-%d %H:%M:%S')
#             if 'useful' not in article:
#                 article['useful'] = False
        
#         return render_template('index.html', articles=articles)
@app.route('/')
def index():
    try:
        db = get_mongo_connection()
        collection = db['fact_classified_articles']
        
        articles = list(collection.find(
            {"classification": {"$in": [True, "True"]}},
            {'_id': 0}  # This will include all fields except _id
        ).sort('_id', -1).limit(1000))
        
        # This part is already correct
        for article in articles:
            if 'link_date' in article and isinstance(article['link_date'], datetime):
                article['link_date'] = article['link_date'].strftime('%Y-%m-%d %H:%M:%S')
            if 'useful' not in article:
                article['useful'] = False
        
        return render_template('index.html', articles=articles)
    # ... rest of the code
    
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return render_template('error.html', error=str(e))

# Add new endpoint for updating useful status
@app.route('/update_useful', methods=['POST'])
def update_useful():
    try:
        data = request.get_json()
        link_id = data['link_id']
        useful = data['useful']
        
        db = get_mongo_connection()
        collection = db['fact_classified_articles']
        
        collection.update_one(
            {'link_id': link_id},
            {'$set': {'useful': useful}},
            upsert=False
        )
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating useful status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)