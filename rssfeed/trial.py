import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        port=3306
    )
    print("Successfully connected to MySQL server!")
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    for db in cursor:
        print(db[0])
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")