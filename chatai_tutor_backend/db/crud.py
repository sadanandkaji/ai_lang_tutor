
from db.database import get_db_connection

def save_mistake(user_id: str, mistake: str, correction: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mistakes (user_id, mistake, correction) VALUES (?, ?, ?)",(user_id, mistake, correction))
    conn.commit()
    conn.close()

def get_mistakes(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT mistake, correction FROM mistakes WHERE user_id=?", (user_id,))
    mistakes = cursor.fetchall()
    conn.close()
    
    # Correctly extract data from row tuples
    return [{"mistake": row[0], "correction": row[1]} for row in mistakes]


