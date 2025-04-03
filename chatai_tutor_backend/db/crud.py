from db.database import get_db_connection

def save_mistake(user: str, mistake: str, correction: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mistakes (user, mistake, correction) VALUES (?, ?, ?)", (user, mistake, correction))
    conn.commit()
    conn.close()

def get_mistakes(user: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT mistake, correction FROM mistakes WHERE user=?", (user,))
    mistakes = cursor.fetchall()
    conn.close()
    return mistakes
