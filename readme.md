# Electric Bill Fetcher

This script fetches Electric Bill for South Bihar and North Bihar Power Distrbution Company customers and send it to your telegram account.
You can also use Whatsapp to send message (Optional).

_Now it will also send bill details with pdf as caption._

### To Do

- [ ] Add More notification destination
- [ ] Add option to edit Telegram chat id and WhatsApp phone number
- [x] ~~Create Dockerfile~~
- [x] ~~Add option to fetch details for mutiple Consumers~~
- [x] ~~Send with [Whatsapp API](https://github.com/aldinokemal/go-whatsapp-web-multidevice)~~

### Getting Started

Clone this repo, create a `.env` file and add following details.

    TELEGRAM_BOT_TOKEN=<Replace with your bot token generated by botfather>

1.  **Install Libraries:**
    pip install -r requirements.txt

2.  **Run the script to create the database:**
    python createDb.py
    This will create the SQLite database (`bill.db`) to store CA numbers and related details.
3.  **Add CA number and telegram bot token**

        python addNew.py

    > Leave empty for WhatsApp if you don't have api.

    This script will prompt you to enter details for a new CA and add it to the database.

4.  **Now Run it with**

        python main.py

## Sending with WhatsApp (Optional)

- The script has the ability to send bill details via WhatsApp. However, this feature is optional and you will need to setup [WhatsApp API](https://github.com/aldinokemal/go-whatsapp-web-multidevice).

### Steps to Enable WhatsApp Notification

1.  **Update the `.env` file:**

    Add the following details to your `.env` file

    `WHATSAPP_API_URL=<Your WhatsApp API URL>`

    Replace `<Your WhatsApp API URL>` with the appropriate values.

2.  Add the phone number with country code like `917894561230` while adding CA number with `addNew.py`.

## Add a cron job to fetch and get bill every month (Optional)

### Setting up a Cron Job (Optional)

To automatically fetch and get the bill every day, you can set up a cron job. For example:

```bash
0 0 * * * /path/to/python /path/to/main.py
```

This will run the script at midnight every day.

Make sure to replace `/path/to/python` and `/path/to/main.py` with the correct paths for your Python executable and the `main.py` script.

Feel free to adjust the cron job timing based on your preferences and requirements.
