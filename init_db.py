import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('''
UPDATE books SET image = NULL;
''')

conn.close()

print("Book images reset successfully!")