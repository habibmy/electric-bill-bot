import requests
import xml.etree.ElementTree as ET
import json
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()


def fetch_bill_details(ca_number):

    response = requests.get(
        "http://hargharbijli.bsphcl.co.in/WebService/WebServiceGIS.asmx/GetConsumerBillingDetails",
        params={"CA_Number": ca_number},
    )
    if response.status_code != 200:
        raise Exception("Failed to fetch bill details.")

    root = ET.fromstring(response.text)
    json_string = root.text
    bill_details = json.loads(json_string)

    return bill_details


def fetch_bill_pdf(ca_number):

    # Returns:
    #   The bill PDF in binary format.

    response = requests.get(
        "http://hargharbijli.bsphcl.co.in/WebService/WebServiceGIS.asmx/GetConsumerBillingPdf",
        params={"CA_Number": ca_number},
    )
    if response.status_code != 200:
        raise Exception("Failed to fetch bill PDF.")

    bill_pdf = response.content
    return bill_pdf


def send_pdf_to_telegram_bot(pdf_file_data, bot_token, chat_id, bill_details):
    caption = f"""
    *Bill Details*

*Consumer:* {bill_details['ConsumerName']}
*Month:* {bill_details['BillMonth']}
*Due Date:* {bill_details['DueDate']}
*Amount Due:* ₹{bill_details['PreviousAmount']}

*Previous Amount:* ₹{bill_details['PreviousAmount']}
*Previous Date:* {bill_details['PreviousDate']}

*Address:* {bill_details['Address']}

*Please settle your bill by the due date to avoid late payment fees.*
"""

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {"document": ("bill.pdf", pdf_file_data)}
    data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
    response = requests.post(url, files=files, data=data)
    if response.status_code != 200:
        raise Exception("Failed to send the PDF to Telegram.")


def send_bill_to_whatsapp(whatsapp_api_url, phone_number, bill_details, bill_pdf_data):

    caption = """
*Bill Details*

*Consumer:* {ConsumerName}
*Month:* {BillMonth}
*Due Date:* {DueDate}
*Amount Due:* ₹{PreviousAmount}

*Previous Amount:* ₹{PreviousAmount}
*Previous Date:* {PreviousDate}

*Address:* {Address}

Please settle your bill by the due date to avoid late payment fees.
""".format(
        **bill_details
    )

    payload = {
        "phone": phone_number,
        "caption": caption,
    }

    files = {"file": ("bill.pdf", bill_pdf_data, "application/pdf")}

    response = requests.post(whatsapp_api_url, data=payload, files=files)

    if response.status_code != 200:
        raise Exception("Failed to send bill PDF to WhatsApp.")


def main():

    ca_number = os.environ.get("CA_NUMBER")

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
    c.execute("SELECT bill_details FROM bills ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    previous_bill_details = row[0] if row else None

    conn.close()

    if ca_number is None:
        raise Exception("CA_NUMBER environment variable is not set.")

    # Fetch the bill details.
    bill_details = fetch_bill_details(ca_number)
    bill_details_str = json.dumps(bill_details)

    # Check if the bill details have changed.
    if bill_details_str != previous_bill_details:
        # Fetch the bill PDF.
        bill_pdf = fetch_bill_pdf(ca_number)

        # Send the bill PDF to WhatsApp.
        whatsapp_api_url = os.environ.get("WHATSAPP_API_URL")
        whatsapp_phone_number = os.environ.get("WHATSAPP_PHONE_NUMBER")
        if whatsapp_api_url is not None:
            send_bill_to_whatsapp(
                whatsapp_api_url, whatsapp_phone_number, bill_details, bill_pdf
            )

        # Send the bill PDF to Telegram.
        telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if telegram_bot_token is not None and telegram_chat_id is not None:
            send_pdf_to_telegram_bot(
                bill_pdf, telegram_bot_token, telegram_chat_id, bill_details
            )

        # Save the bill details to the database.
        conn = sqlite3.connect("bill.db")
        c = conn.cursor()
        ca_number = str(ca_number)
        c.execute(
            "INSERT INTO bills (ca_number, bill_details) VALUES (?, ?)",
            (ca_number, bill_details_str),
        )
        conn.commit()
        conn.close()

        # Update the previous bill details.
        previous_bill_details = bill_details
    else:
        print("No new bills")


if __name__ == "__main__":
    main()
