# Electric Bill Fetcher

This script fetches Electric Bill for South Bihar and North Bihar Power Distrbution Company customers and send it to your telegram account.
_Now it will also send bill details with pdf as caption._

### To Do

- [ ] Add More notification destination
- [ ] Add option to fetch details for mutiple Consumers

### Getting Started

Clone this repo, create a `.env` file and add following details.

    CA_NUMBER=<your CA Number from bill>
    TELEGRAM_BOT_TOKEN=<Replace with your bot token generated by botfather>
    TELEGRAM_CHAT_ID=<get it chat id bot>

#### Install Libraries

    pip install -r requirements.txt

Now Run it with

    python main.py

### Add a cron job to fetch and get bill every month (Optional)
