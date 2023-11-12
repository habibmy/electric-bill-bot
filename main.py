import os
from dotenv import load_dotenv
import sqlite3
import json
from functions import fetch_bill_details, fetch_bill_pdf, send_bill_to_whatsapp, send_pdf_to_telegram_bot

load_dotenv()

def main():
    # Fetch all CA numbers and their associated messaging details from the database
    conn = sqlite3.connect("bill.db")
    c = conn.cursor()
    c.execute("SELECT ca_number, telegram_chat_ids, whatsapp_phone_numbers FROM notification_settings")
    ca_numbers_and_details = c.fetchall()
    conn.close()

    # Iterate over each CA number and fetch/send details
    for ca_number, telegram_chat_ids_str, whatsapp_phone_numbers_str in ca_numbers_and_details:
        # Get other environment variables
        whatsapp_api_url = os.environ.get("WHATSAPP_API_URL")
        telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

        # Convert JSON strings to lists
        telegram_chat_ids = json.loads(telegram_chat_ids_str) if telegram_chat_ids_str else []
        whatsapp_phone_numbers = json.loads(whatsapp_phone_numbers_str) if whatsapp_phone_numbers_str else []

        # Get the previous bill details from the database.
        conn = sqlite3.connect("bill.db")
        c = conn.cursor()

        c.execute(
            """CREATE TABLE IF NOT EXISTS bills (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ca_number TEXT NOT NULL,
          bill_details TEXT NOT NULL
      )"""
        )
        c.execute("SELECT bill_details FROM bills WHERE ca_number = ? ORDER BY id DESC LIMIT 1", (ca_number,))
        row = c.fetchone()
        previous_bill_details = row[0] if row else None

        conn.close()

        # Fetch the bill details.
        bill_details = fetch_bill_details(ca_number)
        bill_details_str = json.dumps(bill_details)

        # Check if the bill details have changed.
        if bill_details_str != previous_bill_details:
            # Fetch the bill PDF.
            bill_pdf = fetch_bill_pdf(ca_number)

            # Send the bill PDF to WhatsApp.
            if whatsapp_api_url is not None:
                for phone_number in whatsapp_phone_numbers:
                    send_bill_to_whatsapp(whatsapp_api_url, phone_number, bill_details, bill_pdf)

            # Send the bill PDF to Telegram.
            if telegram_bot_token is not None:
                for chat_id in telegram_chat_ids:
                    send_pdf_to_telegram_bot(bill_pdf, telegram_bot_token, chat_id, bill_details)

            # Save the bill details to the database.
            conn = sqlite3.connect("bill.db")
            c = conn.cursor()
            c.execute(
                "INSERT INTO bills (ca_number, bill_details) VALUES (?, ?)",
                (ca_number, bill_details_str),
            )
            conn.commit()
            conn.close()

            # Update the previous bill details.
            previous_bill_details = bill_details
        else:
            print(f"No new bills for CA number: {ca_number}")

if __name__ == "__main__":
    main()
