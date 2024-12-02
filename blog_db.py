import sqlite3

conn = sqlite3.connect('blog_db')
cursor = conn.cursor()

with open('schema.sql', 'r') as f:
    sql_script = f.read()
    cursor.executescript(sql_script)

conn.close()