
import re
import time
import requests
import os
from dotenv import load_dotenv


load_dotenv()  # using this to get input from .env

headers = {
    'referer': 'https://rpilocator.com',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


def send_telegram_notification(message):

    """
    Had to make a bot on telegram. chatgpt will give the details of the process from creating bot to getting all the credentials.
    """

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
    """
    This function will get the token and cookies from the website. without matching token and cookies the website will
    not return response.
    """
    r = requests.get('https://rpilocator.com', headers=headers)  # requesting to homepage of the rpi locator
    token = get_regex_text('localToken="([^"]+)', r.text)  # using regular expression to fetch the token

    return token, r.cookies.get_dict()  # returning token and cookies getting from the request


def get_stock_data(country, cat):
    token, cookies = get_token_and_cookies()  # we will call the function to get the token and cookies
    params = {
        'method': 'getProductTable',
        'token': token,
        'country': country,
        'cat': cat,
        '_': '1683866351466',
    }

    response = requests.get(
        'https://rpilocator.com/data.cfm',
        params=params,
        cookies=cookies,
        headers=headers
    )

    """
    we got the above api and request params from the browser's network tab. we have opened https://rpilocator.com/,
    then opened network tab, then reloaded page to capture the correct request,
    then copied as curl and converted that to python requests.
    """

    for item in response.json()['data']:
        if item['avail'] == 'Yes':
            if "pishop" not in item['link']:
                message = f"Product available: {item['description']}\nPrice: {item['price']['display']} {item['price']['currency']}\nLink: {item['link']}"  # shaping the message
                send_telegram_notification(message)  # sending telegram message

def get_job_data():
    token = ""

    headers = {
        'authorization': f'Status|unauthenticated|Session|{token}|',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'query': 'query searchJobCardsByLocation($searchJobRequest: SearchJobRequest!) {\n  searchJobCardsByLocation(searchJobRequest: $searchJobRequest) {\n    nextToken\n    jobCards {\n      jobId\n      language\n      dataSource\n      requisitionType\n      jobTitle\n      jobType\n      employmentType\n      city\n      state\n      postalCode\n      locationName\n      totalPayRateMin\n      totalPayRateMax\n      tagLine\n      bannerText\n      image\n      jobPreviewVideo\n      distance\n      featuredJob\n      bonusJob\n      bonusPay\n      scheduleCount\n      currencyCode\n      geoClusterDescription\n      surgePay\n      jobTypeL10N\n      employmentTypeL10N\n      bonusPayL10N\n      surgePayL10N\n      totalPayRateMinL10N\n      totalPayRateMaxL10N\n      distanceL10N\n      monthlyBasePayMin\n      monthlyBasePayMinL10N\n      monthlyBasePayMax\n      monthlyBasePayMaxL10N\n      jobContainerJobMetaL1\n      virtualLocation\n      poolingEnabled\n    }\n  }\n}\n',
        'variables': {
            'searchJobRequest': {
                'locale': 'en-US',
                'country': 'United States',
                'keyWords': '',
                'equalFilters': [],
                'containFilters': [
                    {
                        'key': 'isPrivateSchedule',
                        'val': [
                            'false',
                        ],
                    },
                ],
                'rangeFilters': [
                    {
                        'key': 'hoursPerWeek',
                        'range': {
                            'minimum': 0,
                            'maximum': 80,
                        },
                    },
                ],
                'orFilters': [],
                'dateFilters': [
                    {
                        'key': 'firstDayOnSite',
                        'range': {
                            'startDate': '2023-12-29',
                        },
                    },
                ],
                'sorters': [],
                'pageSize': 100,
                'geoQueryClause': {
                    # 'lat': 48.19471,
                    # 'lng': -122.1264,

                    'lat': 34.10261,
                    'lng': -117.43577,

                    'unit': 'mi',
                    'distance': 50,
                },
            },
        },
    }

    response = requests.post(
        'https://e5mquma77feepi2bdn4d6h3mpu.appsync-api.us-east-1.amazonaws.com/graphql',
        headers=headers,
        json=json_data,
    )

    # {'data': {'searchJobCardsByLocation': {'nextToken': None, 'jobCards': []}}}

    job_cards = response.json()['data']['searchJobCardsByLocation']['jobCards']
    if len(job_cards) > 0:
        for job_card in job_cards:
            message = f"Job available: {job_card['jobTitle']}\nLocation: {job_card['locationName']}"
            send_telegram_notification(message)


if __name__ == '__main__':
    cat = os.getenv("CATEGORY")  # we will read category from environment variable, example: CATEGORY=PI3,PI4,PIZERO,PIZERO2
    country = os.getenv("COUNTRY")  # we will read country from environment variable, example: COUNTRY=US
    wait_time = int(os.getenv("WAIT_TIME"))  # we will read wait time from environment variable, this will tell the script to wait before every check. example: WAIT_TIME=60
    while True:
        # get_stock_data(country, cat)  # we will call the function to get the stock data
        get_job_data()
        print(f"Sleeping for {wait_time} seconds")
        time.sleep(wait_time)
