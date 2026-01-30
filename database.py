import sqlite3
import os

DB_PATH = "data/organ_donation.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            blood_group TEXT,
            organ TEXT,
            city TEXT,
            urgency INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipients (
            recipient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            blood_group TEXT,
            organ TEXT,
            city TEXT,
            urgency INTEGER
        )
    """)

    conn.commit()
    conn.close()


def add_donor(name, age, blood_group, organ, city, urgency):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO donors (name, age, blood_group, organ, city, urgency)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, blood_group, organ, city, urgency))
    conn.commit()
    conn.close()


def add_recipient(name, age, blood_group, organ, city, urgency):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recipients (name, age, blood_group, organ, city, urgency)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, blood_group, organ, city, urgency))
    conn.commit()
    conn.close()


def get_donors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donors")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_recipients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipients")
    rows = cursor.fetchall()
    conn.close()
    return rows