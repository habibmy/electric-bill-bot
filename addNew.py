# add_notification.py
import json
import sqlite3

def insert_notification_settings(ca_number, telegram_chat_ids, whatsapp_phone_numbers):
    conn = sqlite3.connect("bill.db")
    c = conn.cursor()

    # Convert lists to JSON strings
    telegram_chat_ids_str = json.dumps(telegram_chat_ids)
    whatsapp_phone_numbers_str = json.dumps(whatsapp_phone_numbers)

    c.execute("""
        INSERT INTO notification_settings (ca_number, telegram_chat_ids, whatsapp_phone_numbers)
        VALUES (?, ?, ?);
    """, (ca_number, telegram_chat_ids_str, whatsapp_phone_numbers_str))

    conn.commit()
    conn.close()

def add_notification_settings():
    # Get input from the user
    ca_number = input("Enter CA Number: ")
    
    # Get WhatsApp phone numbers as a comma-separated string and convert to a list
    whatsapp_phone_numbers_str = input("Enter WhatsApp Phone Numbers (comma-separated) 917894561237, 919898979796: ")
    whatsapp_phone_numbers = [phone.strip() for phone in whatsapp_phone_numbers_str.split(',')]

    # Get Telegram chat IDs as a comma-separated string and convert to a list
    telegram_chat_ids_str = input("Enter Telegram Chat IDs (comma-separated): ")
    telegram_chat_ids = [int(chat_id.strip()) for chat_id in telegram_chat_ids_str.split(',')]

    # Insert data into the notification_settings table
    insert_notification_settings(ca_number, telegram_chat_ids, whatsapp_phone_numbers)

if __name__ == "__main__":
    add_notification_settings()
