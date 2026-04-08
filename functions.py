import requests
import xml.etree.ElementTree as ET
import json
from playwright.sync_api import sync_playwright

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


# def fetch_bill_pdf(ca_number):

#     # Returns:
#     #   The bill PDF in binary format.

#     response = requests.get(
#         "http://hargharbijli.bsphcl.co.in/WebService/WebServiceGIS.asmx/GetConsumerBillingPdf",
#         params={"CA_Number": ca_number},
#     )
#     if response.status_code != 200:
#         raise Exception("Failed to fetch bill PDF.")

#     bill_pdf = response.content
#     return bill_pdf

def fetch_bill_pdf(ca_number):

    # Returns:
    #   The bill PDF in binary format.

    response = requests.get(
        "https://api.bsphcl.co.in/sbWSMobileApp/ViewBill.asmx/GetViewBill",
        params={"strCANumber": ca_number},headers = {"User-Agent": "Mozilla/5.0"}
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
*Amount Due:* ₹{bill_details['AmountBeforeDueDate']}

*Previous Amount:* ₹{bill_details['PreviousAmount']}
*Previous Date:* {bill_details['PreviousDate']}

*Address:* {bill_details['Address']}

*Please settle your bill by the due date to avoid late payment fees.*
"""
    file_name = bill_details['ConsumerName'] + "-" + bill_details['BillMonth'] + "-bill.pdf"
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {"document": (file_name, pdf_file_data)}
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
*Amount Due:* ₹{AmountBeforeDueDate}

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
    
def fetch_bill_details_with_playwright(page, ca_number):

    responses = []

    def handle_response(response):
        if "SpmIntegrationsData" in response.url:
            try:
                data = response.json()
                responses.append(data)
            except:
                pass

    page.on("response", handle_response)

    # input
    page.fill('input[formcontrolname="accno"]', "")
    page.fill('input[formcontrolname="accno"]', ca_number)
    page.click('button:has-text("Search")')

    page.wait_for_selector('a:has-text("View Bill")')
    page.remove_listener("response", handle_response)

    bill = None
    history = None

    # 🔍 classify responses
    for r in responses:
        try:
            d = r[0]["data"]

            # bill data
            if "billMonth" in d:
                bill = d

            # history data
            elif "data" in d:
                history = r

        except:
            pass

    return {
        "bill": bill,
        "history": history
    }