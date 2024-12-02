import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('blog_db')
cursor = conn.cursor()

username = 'Tester1'
password = '<Password1>'

hashed_password = generate_password_hash(password)

cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, hashed_password))
conn.commit()
conn.close()

print(f"User '{username}' added successfully")