import requests
import xml.etree.ElementTree as ET
import json
import os
from dotenv import load_dotenv

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

    print("Consumer Name:", bill_details["ConsumerName"])
    print("Bill Month:", bill_details["BillMonth"])
    print("Due Date:", bill_details["DueDate"])
    print("Amount Before Due Date:", bill_details["AmountBeforeDueDate"])
    print("Amount Up to Due Date plus 10 Days:", bill_details["AmountUptoDuedate_plus10Days"])
    print("Amount After Due Date plus 10 Days:", bill_details["AmountAfterDuedate_plus10Days"])
    print("Previous Amount:", bill_details["PreviousAmount"])
    print("Previous Date:", bill_details["PreviousDate"])
    print("Address:", bill_details["Address"])
    print("Error Message:", bill_details["ErrorMessage"])

    return bill_details

def fetch_bill_pdf(ca_number):

    # Returns:
    #     The bill PDF in binary format.

    response = requests.get(
        "http://hargharbijli.bsphcl.co.in/WebService/WebServiceGIS.asmx/GetConsumerBillingPdf",
        params={"CA_Number": ca_number},
    )
    if response.status_code != 200:
        raise Exception("Failed to fetch bill PDF.")

    bill_pdf = response.content
    return bill_pdf

def send_pdf_to_telegram_bot(pdf_file_path, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {'document': open(pdf_file_path, 'rb')}
    data = {'chat_id': chat_id}
    response = requests.post(url, files=files, data=data)
    if response.status_code != 200:
        raise Exception("Failed to send the PDF to Telegram.")

def main():
    previous_bill_details = {}

    
    ca_number = os.environ.get('CA_NUMBER')

    if ca_number is None:
        raise Exception("CA_NUMBER environment variable is not set.")

    # Fetch the bill details.
    bill_details = fetch_bill_details(ca_number)

    # Check if the bill details are different.
    if bill_details != previous_bill_details:
        # Fetch the bill PDF.
        bill_pdf = fetch_bill_pdf(ca_number)

        pdf_file_path = "bill.pdf"
        with open(pdf_file_path, "wb") as f:
            f.write(bill_pdf)

        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')

        if bot_token is None or chat_id is None:
            raise Exception("Telegram bot token or chat ID is not set.")

        send_pdf_to_telegram_bot(pdf_file_path, bot_token, chat_id)

        # Update the previous bill details.
        previous_bill_details = bill_details

if __name__ == "__main__":
    main()