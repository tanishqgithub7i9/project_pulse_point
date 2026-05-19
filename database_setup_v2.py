# -*- coding: utf-8 -*-
"""
database_setup_v2.py — Project Pulse-Point Database Setup
==========================================================
WHAT THIS DOES:
    Creates the SQLite database with the full, correct schema.
    
    It's SMART — it also handles existing databases:
    - If the table doesn't exist → creates it fresh
    - If old columns are missing → adds them (migration)
    
    This is called "database migration" — a real industry skill!

WHY SQLITE:
    SQLite stores your entire database in a single .db file.
    No server needed. Perfect for local data projects.
    The SQL syntax is identical to PostgreSQL/MySQL — what you
    learn here transfers directly to production databases.
"""

import sqlite3
import config


def setup_database():
    """Create or upgrade the bitcoin_prices table."""
    
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    # ── Step 1: Create table with FULL schema ─────────────────────────────────
    # IF NOT EXISTS means: "only create if it's not already there"
    # This makes the script safe to run multiple times
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bitcoin_prices (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            price     REAL    NOT NULL,
            sentiment REAL,
            headline  TEXT
        )
    ''')
    print('[OK] Table structure verified.')

    # ── Step 2: Handle existing databases (migration) ─────────────────────────
    # PRAGMA table_info() is an SQLite command that lists all columns
    existing_cols = [
        row[1]
        for row in cursor.execute('PRAGMA table_info(bitcoin_prices)').fetchall()
    ]
    print(f'   Existing columns: {existing_cols}')

    # Add missing columns for users upgrading from the old version
    if 'sentiment' not in existing_cols:
        cursor.execute('ALTER TABLE bitcoin_prices ADD COLUMN sentiment REAL')
        print('   [+] Migration: Added "sentiment" column.')

    if 'headline' not in existing_cols:
        cursor.execute('ALTER TABLE bitcoin_prices ADD COLUMN headline TEXT')
        print('   [+] Migration: Added "headline" column.')

    # ── Step 3: Check how many rows currently exist ────────────────────────────
    cursor.execute('SELECT COUNT(*) FROM bitcoin_prices')
    row_count = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    print()
    print('DATABASE READY!')
    print(f'   File       : {config.DB_PATH}')
    print(f'   Schema     : id | timestamp | price | sentiment | headline')
    print(f'   Rows now   : {row_count:,}')
    print()
    if row_count == 0:
        print('   [!] No data yet -- run: python generate_sample_data.py')
    else:
        print('   [OK] Data exists -- ready for analysis!')


if __name__ == '__main__':
    setup_database()
