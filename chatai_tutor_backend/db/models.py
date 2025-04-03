from db.database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mistakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,  -- Changed from "user" to "user_id"
        mistake TEXT,
        correction TEXT
    )
    """)
    
    conn.commit()
    conn.close()



