import sqlite3

def get_db():
    return sqlite3.connect("honeypot_govi.db", check_same_thread=False)

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        scam_detected INTEGER DEFAULT 0,
        total_messages INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        sender TEXT,
        text TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS intelligence (
        session_id TEXT,
        bank_accounts TEXT,
        upids TEXT,
        phishing_links TEXT,
        phone_numbers TEXT,
        suspicious_keywords TEXT,
        agent_notes TEXT
    )
    """)

    conn.commit()
    conn.close()