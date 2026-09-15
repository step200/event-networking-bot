import sqlite3

DB_NAME = "meetup.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT NOT NULL,
                tech_stack TEXT NOT NULL,
                goal TEXT NOT NULL
            )
        """)
        conn.commit()

def save_participant(user_id: int, username: str, full_name: str, tech_stack: str, goal: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO participants (user_id, username, full_name, tech_stack, goal)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, full_name, tech_stack, goal))
        conn.commit()

def get_participant(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, full_name, tech_stack, goal FROM participants WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

def get_random_partner(current_user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, full_name, tech_stack, goal 
            FROM participants 
            WHERE user_id != ? 
            ORDER BY RANDOM() LIMIT 1
        """, (current_user_id,))
        return cursor.fetchone()