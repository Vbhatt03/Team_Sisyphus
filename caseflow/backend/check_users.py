import sqlite3

conn = sqlite3.connect('caseflow.db')
cursor = conn.cursor()
cursor.execute('SELECT id, username FROM user')
users = cursor.fetchall()
print(f"Found {len(users)} users:")
for user in users:
    print(f"ID: {user[0]}, Username: {user[1]}")
conn.close()