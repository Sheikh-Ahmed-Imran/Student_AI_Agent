import uuid
import datetime
from db import get_connection

def add_message(conversation_id: str, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, datetime.datetime.now())
    )
    conn.commit()
    conn.close()


def get_conversation(conversation_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, created_at FROM conversations WHERE conversation_id=? ORDER BY id",
        (conversation_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
