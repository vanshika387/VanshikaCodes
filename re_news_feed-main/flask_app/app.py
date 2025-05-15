from flask import Flask, render_template
import mysql.connector
import sys
import os
import pandas
sys.path.append(os.path.abspath('/home/ubuntu/news_feed/re_news_feed/'))
import ipynb.fs.full.database_operations as database
#from waitress import serve   Not impressed with waitress

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    conn = database.mysql_Database('timely_feeds')
    articles = conn.execute_a_query('SELECT * FROM fact_classified_articles ORDER BY link_date DESC')
    articles_html = articles.to_dict(orient='records')
    conn.extinguish_connection()
    return render_template('index.html', articles=articles_html)

if __name__ == '__main__':
    #app.run(ssl_context=('/etc/letsencrypt/live/www.vishalvivek.com/fullchain.pem', '/etc/letsencrypt/live/www.vishalvivek.com/privkey.pem'), host='0.0.0.0', debug=True)
    #app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', debug=True)
    app.run(host='0.0.0.0', debug=True)
    #serve(app=app, url_scheme='https', host='0.0.0.0', port=5000) #, debug=True) Waitress is quite useless