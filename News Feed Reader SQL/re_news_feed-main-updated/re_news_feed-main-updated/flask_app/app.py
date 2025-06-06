# from flask import Flask, jsonify, render_template, request
# import pymysql
# import os
# from datetime import datetime
# from dotenv import load_dotenv
# import time

# app = Flask(__name__, static_folder='static')

# # Load environment variables
# load_dotenv()

# # Configure MySQL connection parameters
# MYSQL_CONFIG = {
#     'host': os.getenv('MYSQL_HOST', 'localhost'),
#     'database': os.getenv('MYSQL_DB', 'TimelyFeeds'),
#     'user': os.getenv('MYSQL_USER', 'root'),
#     'password': os.getenv('MYSQL_PASSWORD', ''),
#     'port': int(os.getenv('MYSQL_PORT', 3306)),
#     'cursorclass': pymysql.cursors.DictCursor,
#     'autocommit': True
# }

# def get_mysql_connection(max_retries=3, retry_delay=2):
#     """Create MySQL database connection with retry logic using PyMySQL"""
#     for attempt in range(max_retries):
#         try:
#             connection = pymysql.connect(**MYSQL_CONFIG)
#             print(f"Successfully connected to MySQL database (attempt {attempt + 1})")
#             return connection
#         except pymysql.Error as e:
#             print(f"MySQL connection attempt {attempt + 1} failed: {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(retry_delay)
#                 continue
#             print("Max connection retries reached")
#             return None

# @app.route('/')
# def index():
#     connection = None
#     try:
#         connection = get_mysql_connection()
#         if connection is None:
#             return render_template('error.html', error="Failed to connect to database after multiple attempts")
        
#         with connection.cursor() as cursor:
#             query = """
#             SELECT 
#                 fe.id, fe.link_id, fe.site_name, fe.sub_site_name, 
#                 fe.link_date, ca.title, ca.link_url, 
#                 ca.classification, ca.explanation, ca.useful
#             FROM fact_feed_table fe
#             JOIN classified_articles ca ON fe.id = ca.feed_entry_id
#             WHERE ca.classification = TRUE
#             ORDER BY fe.link_date DESC
#             LIMIT 1000
#             """
            
#             cursor.execute(query)
#             articles = cursor.fetchall()
            
#             # Format dates and ensure useful field exists
#             for article in articles:
#                 if article['link_date'] and isinstance(article['link_date'], datetime):
#                     article['link_date'] = article['link_date'].strftime('%Y-%m-%d %H:%M:%S')
#                 article['useful'] = bool(article.get('useful', False))
            
#             return render_template('index.html', articles=articles)
    
#     except Exception as e:
#         print(f"Error in index route: {str(e)}")
#         return render_template('error.html', error=f"Server error: {str(e)}")
#     finally:
#         if connection:
#             connection.close()

# @app.route('/update_useful', methods=['POST'])
# def update_useful():
#     connection = None
#     try:
#         data = request.get_json()
#         if not data or 'link_id' not in data or 'useful' not in data:
#             return jsonify({'success': False, 'error': 'Invalid request data'}), 400
        
#         connection = get_mysql_connection()
#         if connection is None:
#             return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
#         with connection.cursor() as cursor:
#             update_query = """
#             UPDATE classified_articles ca
#             JOIN fact_feed_table fe ON ca.feed_entry_id = fe.id
#             SET ca.useful = %s
#             WHERE fe.link_id = %s
#             """
            
#             cursor.execute(update_query, (bool(data['useful']), data['link_id']))
        
#         return jsonify({'success': True})
    
#     except Exception as e:
#         print(f"Error updating useful status: {str(e)}")
#         return jsonify({'success': False, 'error': str(e)}), 500
#     finally:
#         if connection:
#             connection.close()

# @app.route('/api/stats')
# def get_stats():
#     connection = None
#     try:
#         connection = get_mysql_connection()
#         if connection is None:
#             return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
#         with connection.cursor() as cursor:
#             # Get counts
#             cursor.execute("""
#                 SELECT 
#                     COUNT(*) as total,
#                     SUM(CASE WHEN useful = TRUE THEN 1 ELSE 0 END) as useful,
#                     SUM(CASE WHEN link_date >= DATE_SUB(NOW(), INTERVAL 24 HOUR) THEN 1 ELSE 0 END) as recent
#                 FROM classified_articles ca
#                 JOIN fact_feed_table fe ON ca.feed_entry_id = fe.id
#                 WHERE ca.classification = TRUE
#             """)
#             counts = cursor.fetchone()
            
#             # Get articles by site
#             cursor.execute("""
#                 SELECT fe.site_name, COUNT(*) as count 
#                 FROM fact_feed_table fe 
#                 JOIN classified_articles ca ON fe.id = ca.feed_entry_id 
#                 WHERE ca.classification = TRUE 
#                 GROUP BY fe.site_name
#                 ORDER BY count DESC
#             """)
#             by_site = cursor.fetchall()
            
#             return jsonify({
#                 'success': True,
#                 'stats': {
#                     'total_articles': counts['total'],
#                     'useful_articles': counts['useful'],
#                     'recent_articles': counts['recent'],
#                     'by_site': by_site
#                 }
#             })
            
#     except Exception as e:
#         print(f"Error fetching stats: {str(e)}")
#         return jsonify({'success': False, 'error': str(e)}), 500
#     finally:
#         if connection:
#             connection.close()

# @app.route('/api/search')
# def search_articles():
#     connection = None
#     try:
#         query = request.args.get('q', '').strip()
#         site = request.args.get('site', '').strip()
#         useful_only = request.args.get('useful_only', 'false').lower() == 'true'
        
#         if not query and not site:
#             return jsonify({'success': False, 'error': 'Search query or site filter required'}), 400
        
#         connection = get_mysql_connection()
#         if connection is None:
#             return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
#         with connection.cursor() as cursor:
#             search_query = """
#             SELECT 
#                 fe.id, fe.link_id, fe.site_name, fe.sub_site_name, 
#                 fe.link_date, ca.title, ca.link_url, 
#                 ca.classification, ca.explanation, ca.useful
#             FROM fact_feed_table fe
#             JOIN classified_articles ca ON fe.id = ca.feed_entry_id
#             WHERE ca.classification = TRUE
#             """
            
#             params = []
            
#             if query:
#                 search_query += " AND ca.title LIKE %s"
#                 params.append(f"%{query}%")
            
#             if site:
#                 search_query += " AND fe.site_name = %s"
#                 params.append(site)
            
#             if useful_only:
#                 search_query += " AND ca.useful = TRUE"
            
#             search_query += " ORDER BY fe.link_date DESC LIMIT 500"
            
#             cursor.execute(search_query, params)
#             articles = cursor.fetchall()
            
#             # Format dates
#             for article in articles:
#                 if article['link_date'] and isinstance(article['link_date'], datetime):
#                     article['link_date'] = article['link_date'].strftime('%Y-%m-%d %H:%M:%S')
            
#             return jsonify({'success': True, 'articles': articles})
            
#     except Exception as e:
#         print(f"Error searching articles: {str(e)}")
#         return jsonify({'success': False, 'error': str(e)}), 500
#     finally:
#         if connection:
#             connection.close()

# @app.route('/health')
# def health_check():
#     """Endpoint for health checks"""
#     try:
#         connection = get_mysql_connection()
#         if connection:
#             connection.close()
#             return jsonify({
#                 'status': 'healthy',
#                 'database': 'connected',
#                 'timestamp': datetime.now().isoformat()
#             })
#         return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500
#     except Exception as e:
#         return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# if __name__ == '__main__':
#     try:
#         print("Starting Flask application...")
#         print(f"MySQL Configuration: { {k: v for k, v in MYSQL_CONFIG.items() if k != 'password'} }")
        
#         app.run(
#             host='0.0.0.0',
#             port=5001,
#             debug=True,
#             use_reloader=False
#         )
#     except Exception as e:
#         print(f"Failed to start Flask application: {str(e)}")


from flask import Flask, jsonify, render_template, request
import pymysql
import os
from datetime import datetime
from dotenv import load_dotenv
import time

app = Flask(__name__, static_folder='static')

# Load environment variables
load_dotenv()

# Configure MySQL connection parameters
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'database': os.getenv('MYSQL_DB', 'TimelyFeeds'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True,
    'charset': 'utf8mb4'  # Added for better text encoding
}

def get_mysql_connection(max_retries=3, retry_delay=2):
    """Create MySQL database connection with retry logic using PyMySQL"""
    for attempt in range(max_retries):
        try:
            connection = pymysql.connect(**MYSQL_CONFIG)
            print(f"Successfully connected to MySQL database (attempt {attempt + 1})")
            return connection
        except pymysql.Error as e:
            print(f"MySQL connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            print("Max connection retries reached")
            return None

def format_date_for_display(date_obj):
    """Format date object for display in the UI"""
    if date_obj is None:
        return "No date"
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(date_obj, str):
        try:
            # Try to parse string date
            parsed_date = datetime.strptime(date_obj, '%Y-%m-%d %H:%M:%S')
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return date_obj
    else:
        return str(date_obj)

@app.route('/')
def index():
    connection = None
    try:
        connection = get_mysql_connection()
        if connection is None:
            return render_template('error.html', error="Failed to connect to database after multiple attempts")
        
        with connection.cursor() as cursor:
            query = """
            SELECT 
                fe.id, fe.link_id, fe.site_name, fe.sub_site_name, 
                fe.link_date, fe.created_at,
                ca.title, ca.link_url, 
                ca.classification, ca.explanation, ca.useful
            FROM fact_feed_table fe
            JOIN classified_articles ca ON fe.id = ca.feed_entry_id
            WHERE ca.classification = TRUE
            ORDER BY fe.created_at DESC, fe.link_date DESC
            LIMIT 1000
            """
            
            cursor.execute(query)
            articles = cursor.fetchall()
            
            # Format dates and ensure useful field exists
            for article in articles:
                # Handle link_date
                article['link_date'] = format_date_for_display(article.get('link_date'))
                
                # Handle created_at
                article['created_at'] = format_date_for_display(article.get('created_at'))
                
                # Ensure useful field is boolean
                article['useful'] = bool(article.get('useful', False))
                
                # Clean up title if needed
                if not article.get('title'):
                    article['title'] = "No title available"
            
            print(f"Found {len(articles)} articles to display")
            return render_template('index.html', articles=articles)
    
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('error.html', error=f"Server error: {str(e)}")
    finally:
        if connection:
            connection.close()

@app.route('/update_useful', methods=['POST'])
def update_useful():
    connection = None
    try:
        data = request.get_json()
        if not data or 'link_id' not in data or 'useful' not in data:
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400
        
        connection = get_mysql_connection()
        if connection is None:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        with connection.cursor() as cursor:
            # First check if the record exists
            check_query = """
            SELECT ca.id FROM classified_articles ca
            JOIN fact_feed_table fe ON ca.feed_entry_id = fe.id
            WHERE fe.link_id = %s
            """
            cursor.execute(check_query, (data['link_id'],))
            
            if not cursor.fetchone():
                return jsonify({'success': False, 'error': 'Article not found'}), 404
            
            # Update the useful status
            update_query = """
            UPDATE classified_articles ca
            JOIN fact_feed_table fe ON ca.feed_entry_id = fe.id
            SET ca.useful = %s
            WHERE fe.link_id = %s
            """
            
            cursor.execute(update_query, (bool(data['useful']), data['link_id']))
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'error': 'No rows updated'}), 404
        
        return jsonify({'success': True, 'message': f'Updated useful status to {data["useful"]}'})
    
    except Exception as e:
        print(f"Error updating useful status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/stats')
def get_stats():
    connection = None
    try:
        connection = get_mysql_connection()
        if connection is None:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        with connection.cursor() as cursor:
            # Get counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN useful = TRUE THEN 1 ELSE 0 END) as useful,
                    SUM(CASE WHEN fe.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR) THEN 1 ELSE 0 END) as recent
                FROM classified_articles ca
                JOIN fact_feed_table fe ON ca.feed_entry_id = fe.id
                WHERE ca.classification = TRUE
            """)
            counts = cursor.fetchone()
            
            # Get articles by site
            cursor.execute("""
                SELECT fe.site_name, COUNT(*) as count 
                FROM fact_feed_table fe 
                JOIN classified_articles ca ON fe.id = ca.feed_entry_id 
                WHERE ca.classification = TRUE 
                GROUP BY fe.site_name
                ORDER BY count DESC
            """)
            by_site = cursor.fetchall()
            
            # Get recent activity
            cursor.execute("""
                SELECT 
                    DATE(fe.created_at) as date,
                    COUNT(*) as count
                FROM fact_feed_table fe 
                JOIN classified_articles ca ON fe.id = ca.feed_entry_id 
                WHERE ca.classification = TRUE 
                AND fe.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(fe.created_at)
                ORDER BY date DESC
            """)
            recent_activity = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_articles': counts.get('total', 0),
                    'useful_articles': counts.get('useful', 0),
                    'recent_articles': counts.get('recent', 0),
                    'by_site': by_site,
                    'recent_activity': recent_activity
                }
            })
            
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/search')
def search_articles():
    connection = None
    try:
        query = request.args.get('q', '').strip()
        site = request.args.get('site', '').strip()
        useful_only = request.args.get('useful_only', 'false').lower() == 'true'
        
        if not query and not site:
            return jsonify({'success': False, 'error': 'Search query or site filter required'}), 400
        
        connection = get_mysql_connection()
        if connection is None:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        with connection.cursor() as cursor:
            search_query = """
            SELECT 
                fe.id, fe.link_id, fe.site_name, fe.sub_site_name, 
                fe.link_date, fe.created_at,
                ca.title, ca.link_url, 
                ca.classification, ca.explanation, ca.useful
            FROM fact_feed_table fe
            JOIN classified_articles ca ON fe.id = ca.feed_entry_id
            WHERE ca.classification = TRUE
            """
            
            params = []
            
            if query:
                search_query += " AND (ca.title LIKE %s OR ca.explanation LIKE %s)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if site:
                search_query += " AND fe.site_name = %s"
                params.append(site)
            
            if useful_only:
                search_query += " AND ca.useful = TRUE"
            
            search_query += " ORDER BY fe.created_at DESC, fe.link_date DESC LIMIT 500"
            
            cursor.execute(search_query, params)
            articles = cursor.fetchall()
            
            # Format dates
            for article in articles:
                article['link_date'] = format_date_for_display(article.get('link_date'))
                article['created_at'] = format_date_for_display(article.get('created_at'))
                article['useful'] = bool(article.get('useful', False))
            
            return jsonify({'success': True, 'articles': articles, 'count': len(articles)})
            
    except Exception as e:
        print(f"Error searching articles: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/debug')
def debug_data():
    """Debug endpoint to check data quality"""
    connection = None
    try:
        connection = get_mysql_connection()
        if connection is None:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        with connection.cursor() as cursor:
            # Check feed table
            cursor.execute("SELECT COUNT(*) as count FROM fact_feed_table")
            feed_count = cursor.fetchone()
            
            # Check classified articles
            cursor.execute("SELECT COUNT(*) as count FROM classified_articles")
            classified_count = cursor.fetchone()
            
            # Check date issues
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN link_date IS NULL THEN 1 ELSE 0 END) as null_dates,
                    SUM(CASE WHEN link_date = '0000-00-00 00:00:00' THEN 1 ELSE 0 END) as zero_dates
                FROM fact_feed_table
            """)
            date_stats = cursor.fetchone()
            
            # Sample data
            cursor.execute("""
                SELECT fe.link_id, fe.link_date, fe.created_at, ca.title
                FROM fact_feed_table fe
                LEFT JOIN classified_articles ca ON fe.id = ca.feed_entry_id
                ORDER BY fe.id DESC
                LIMIT 5
            """)
            sample_data = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'debug_info': {
                    'feed_entries': feed_count.get('count', 0),
                    'classified_articles': classified_count.get('count', 0),
                    'date_stats': date_stats,
                    'sample_data': sample_data
                }
            })
            
    except Exception as e:
        print(f"Error in debug endpoint: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/health')
def health_check():
    """Endpoint for health checks"""
    try:
        connection = get_mysql_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            connection.close()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    try:
        print("Starting Flask application...")
        print(f"MySQL Configuration: {dict((k, v) for k, v in MYSQL_CONFIG.items() if k != 'password')}")
        
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            use_reloader=False
        )
    except Exception as e:
        print(f"Failed to start Flask application: {str(e)}")