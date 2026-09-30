import sqlite3

connection = sqlite3.connect("guardianai.db")
cursor = connection.cursor()

# Remove old test audit records
cursor.execute("DELETE FROM audit_logs")

# Remove old approval requests
cursor.execute("DELETE FROM approval_requests")

connection.commit()
connection.close()

print("Old audit logs and approval requests cleared successfully.")