import sqlite3
import bcrypt

def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, 
                      username TEXT NOT NULL UNIQUE, 
                      password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()

def validate_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode('utf-8'), result[0])
    return False

create_table()
