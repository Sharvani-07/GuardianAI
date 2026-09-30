import sqlite3

connection = sqlite3.connect("guardianai.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS agents(

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT NOT NULL,

status TEXT NOT NULL,

risk TEXT NOT NULL

)
""")

connection.commit()

connection.close()

print("Database Created Successfully!")