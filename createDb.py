import sqlite3

conn = sqlite3.connect('data/bill.db')

try:
    c = conn.cursor()

    bills_table ="""
    CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ca_number TEXT NOT NULL,
    bill_details TEXT NOT NULL
    )"""

    notification_Table ="""
    CREATE TABLE IF NOT EXISTS notification_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ca_number TEXT NOT NULL,
        telegram_chat_ids TEXT,
        whatsapp_phone_numbers TEXT
    )"""

    c.execute(bills_table)

    c.execute(notification_Table)
    print("table created")
except:
    print("table not created")

finally:
    conn.close()       