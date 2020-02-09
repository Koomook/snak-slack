import os
import json
from datetime import datetime
from botocore.vendored import requests
# TODO /var/runtime/botocore/vendored/requests/api.py: 64: DeprecationWarning: You are using the get() function from 'botocore.vendored.requests'.  This dependency was removed from Botocore and will be removed from Lambda after 2020/03/31. https: // aws.amazon.com/blogs/developer/removing-the-vendored-version-of-requests-from-botocore/. Install the requests package, 'import requests' directly, and use the requests.get() function instead.

SNAK_API = "https://snak.news/api/news"
SNAK_URL = "https://snak.news/newsList/news/{_id}?channel=slack&corp={corp}"
SNAK_WEBHOOK = os.environ['WEBHOOK']
CORP = os.environ['CORP']


def get_todays_querystring():
    """?startDateTime=2020-02-09T00:00&endDateTime=2020-02-09T23:59" """
    today = datetime.today().strftime('%Y-%m-%d')
    return f"?startDateTime={today}T00:00&endDateTime={today}T23:59"


def get_new_snak(url):
    ret = requests.get(url)
    if ret.status_code != 200:
        raise BaseException("snack api failed")
    return ret.json()['data']


def get_essential_info(data):
    """id, topic, category, title"""
    _id = data['id']
    topic = ",".join(topic['name'] for topic in data['topics'])
    category = data['category']['title']
    title = data['title']

    return _id, topic, category, title


def mk_sentence(_id, topic, category, title):
    """ e.g. [테슬라-모빌리티] 👀 테슬라가 승차공유 서비스 Tesla Network를 출시합니다. https://snak.news/newsList/news/208?channel=slack&corp=pozalabs"""
    link = SNAK_URL.format(_id=_id, corp=CORP)
    return f"[{topic}-{category}] {title} {link}"


def slack_noti(webhook, news_list):
    data = json.dumps({'text': '\n\n'.join(news_list)})
    r = requests.post(webhook, data=data)


def main(event, context):
    qs = get_todays_querystring()
    snak_list = get_new_snak(f"{SNAK_API}{qs}")

    news = []
    for snak in snak_list:
        _id, topic, category, title = get_essential_info(snak)
        sentence = mk_sentence(_id, topic, category, title)
        news.append(sentence)

    slack_noti(SNAK_WEBHOOK, news)

    return 'success'
