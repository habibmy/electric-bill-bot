import requests
import xml.etree.ElementTree as ET
import json

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