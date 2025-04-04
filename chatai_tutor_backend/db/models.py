from db.database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mistakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        mistake TEXT,
        correction TEXT
    )
    """)
    
    conn.commit()
    conn.close()



