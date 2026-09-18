import sqlite3


def init_db():
    conn = sqlite3.connect("cloudsage.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu REAL,
            memory REAL,
            disk REAL,
            status TEXT,
            recommendation TEXT,
            current_cost REAL,
            optimized_cost REAL,
            saving REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_history(cpu, memory, disk, status,
                 recommendation, current_cost,
                 optimized_cost, saving):

    conn = sqlite3.connect("cloudsage.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO history (
            cpu,
            memory,
            disk,
            status,
            recommendation,
            current_cost,
            optimized_cost,
            saving
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cpu,
        memory,
        disk,
        status,
        recommendation,
        current_cost,
        optimized_cost,
        saving
    ))

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect("cloudsage.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM history
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows