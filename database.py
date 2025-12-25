import sqlite3

DB_NAME = "subscriptions.db"

# ---------- Database Setup ----------

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            name TEXT PRIMARY KEY,
            amount REAL,
            billing_cycle TEXT,
            category TEXT,
            next_payment TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---------- CRUD Operations ----------

def add_subscription(name, amount, billing_cycle, category, next_payment):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO subscriptions
        (name, amount, billing_cycle, category, next_payment)
        VALUES (?, ?, ?, ?, ?)
    """, (name, amount, billing_cycle, category, next_payment))
    conn.commit()
    conn.close()

def get_subscriptions():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT name, amount, billing_cycle, category, next_payment
        FROM subscriptions
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def update_subscription(name, amount, billing_cycle, category, next_payment):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        UPDATE subscriptions
        SET amount = ?, billing_cycle = ?, category = ?, next_payment = ?
        WHERE name = ?
    """, (amount, billing_cycle, category, next_payment, name))
    conn.commit()
    conn.close()

def rename_subscription(old_name, new_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        UPDATE subscriptions
        SET name = ?
        WHERE name = ?
    """, (new_name, old_name))
    conn.commit()
    conn.close()

def cancel_subscription(name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM subscriptions WHERE name = ?",
        (name,)
    )
    conn.commit()
    conn.close()

