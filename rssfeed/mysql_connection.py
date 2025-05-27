import mysql.connector

try:
    # Establish the connection
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="avinashjha1912",  # Use appropriate password if needed
        database="timely_feeds"
    )

    mycursor = mydb.cursor()
    
    # Prepare the SQL query
    sql = "INSERT INTO fact_feed_table (name, address) VALUES (%s, %s)"
    val = ("John", "Highway 21")
    
    # Execute the query
    mycursor.execute(sql, val)
    
    # Commit the transaction to the database
    mydb.commit()
    print("Record inserted successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Properly close cursor and connection if they were established
    if 'mycursor' in locals():
        mycursor.close()
    if 'mydb' in locals() and mydb.is_connected():
        mydb.close()
