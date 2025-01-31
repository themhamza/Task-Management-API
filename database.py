import mysql.connector
from mysql.connector import Error

# Database connection
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="hamza",
        database="task_management"
    )
    cursor = db.cursor(dictionary=True)
except Error as e:
    print("Error connecting to MySQL:", e)
    raise