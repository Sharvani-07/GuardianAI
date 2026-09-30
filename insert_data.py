import sqlite3

connection = sqlite3.connect("guardianai.db")

cursor = connection.cursor()

agents = [

("Email Assistant","Active","Medium"),

("Database Agent","Active","High"),

("Report Generator","Inactive","Low"),

("Finance Bot","Active","Medium")

]

cursor.executemany(

"INSERT INTO agents(name,status,risk) VALUES(?,?,?)",

agents

)

connection.commit()

connection.close()

print("Sample Data Added!")