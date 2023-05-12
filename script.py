import re
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    'referer': 'https://rpilocator.com',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


def send_telegram_notification(message):
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message}

    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Failed to send Telegram notification. Error: {response.text}")


def get_regex_text(pattern: str, text: str) -> str:
    text = str(text)
    try:
        pattern = re.compile(r'{}'.format(pattern))
        matches = re.search(pattern, text)
        return matches.group(1)
    except Exception as e:
        return ''


def get_token_and_cookies():
    r = requests.get('https://rpilocator.com', headers=headers)
    token = get_regex_text('localToken="([^"]+)', r.text)

    return token, r.cookies.get_dict()


def get_stock_data(country, cat):
    token, cookies = get_token_and_cookies()
    params = {
        'method': 'getProductTable',
        'token': token,
        'country': country,
        'cat': ','.join(cat),
        '_': '1683866351466',
    }

    response = requests.get(
        'https://rpilocator.com/data.cfm',
        params=params,
        cookies=cookies,
        headers=headers
    )

    print(response.json())
    for item in response.json()['data']:
        if item['avail'] == 'Yes':
            message = f"Product available: {item['description']}\nPrice: {item['price']['display']} {item['price']['currency']}\nLink: {item['link']}"
            send_telegram_notification(message)


if __name__ == '__main__':
    cat = ['PI3', 'PI4', 'PIZERO', 'PIZERO2']
    country = os.getenv("COUNTRY")
    wait_time = int(os.getenv("WAIT_TIME"))
    while True:
        get_stock_data(country, cat)
        # time.sleep(60 * 5)
        time.sleep(wait_time)
