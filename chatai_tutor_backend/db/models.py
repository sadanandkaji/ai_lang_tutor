from db.database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mistakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        mistake TEXT,
        correction TEXT
    )
    """)
    
    conn.commit()
    conn.close()
