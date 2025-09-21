import sqlite3
DB_FILE = "students.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Student table (already exists, keep it)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Student (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        email TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
    )
    """)

  

    # Create new conversations table with conversation_id
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,         -- "user" or "assistant"
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()