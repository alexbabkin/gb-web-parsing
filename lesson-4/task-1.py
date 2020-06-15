import pytz
from lxml import html
import requests
from time import sleep
import datetime as dt
from pymongo import MongoClient

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}


SLEEP_INTERVAL = 5


def get_lenta_news_data_time(link, interval=3):
    # дату можно вытащить из ссылки, но не во всех новостях
    # на главной странице (например из раздела главное) есть информация о времени публикации
    rsp = requests.get(link, headers=header)
    sleep(interval)
    dom = html.fromstring(rsp.text)
    news_datetime = dom.xpath('//time[@class="g-date" and @datetime]/@datetime')[0]
    return news_datetime


def parse_lenta():
    main_link = 'https://lenta.ru'

    rsp = requests.get(main_link, headers=header)
    dom = html.fromstring(rsp.text)

    news_a = dom.xpath('//a[contains(@href,"/news") '
                       'and not(contains(@class, "button-more-news")) '
                       'and not(contains(@class, "topic-title-pic__link"))]')

    news = []
    for a in news_a:
        link = a.xpath('.//@href')[0]
        if link.startswith('http'):
            continue

        full_link = f'{main_link}{link}'

        a_text_lst = a.xpath('.//text()')
        if len(a_text_lst) == 2:
            title = a_text_lst[1]
        else:
            title = a_text_lst[0]

        datetime = get_lenta_news_data_time(full_link, SLEEP_INTERVAL)

        news_dict = {'link': full_link, 'title': title, 'datetime': datetime, 'source': 'lenta.ru'}
        news.append(news_dict)

    return news


DAYS = [' 1 ', ' 2 ', ' 3 ', ' 4 ', ' 5 ', ' 6 ', ' 7 ', ' 8 ', ' 9 ', ' 10 ',
        ' 11 ', ' 12 ', ' 13 ', ' 14 ', ' 15 ', ' 16 ', ' 17 ', ' 18 ', ' 19 ', ' 20 ',
        ' 21 ', ' 22 ', ' 23 ', ' 24 ', ' 25 ', ' 26 ', ' 27 ', ' 28 ', ' 29 ', ' 30 ', ' 31 ']
MONTHS = {'января': 1, 'февраля': 2, 'марта': 3, 'арпеля': 4, 'мая': 5, 'июня': 6, 'июля': 7,
          'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}


def parse_yandex_news_info(info):
    info = info.replace(u'\xa0', ' ')
    time = info[-5:]
    info = info.replace(f' {time}', '')
    time = dt.datetime.strptime(time, '%H:%M', )

    moscow_tz = pytz.timezone('Europe/Moscow')
    if info.endswith(' вчера в'):
        source = info.replace(' вчера в', '')
        date = (dt.datetime.now() - dt.timedelta(1)).date()
        datetime = dt.datetime.combine(date, time.time(), tzinfo=moscow_tz)
        return source, str(datetime).replace(' ', 'T')

    day = list(filter(lambda d: d in info, DAYS))
    month = list(filter(lambda m: m in info, MONTHS.keys()))
    if len(day) == 1 and len(month) == 1:
        source = info.replace(f' {day} {month}', '')
        date = dt.date(2020, MONTHS[month[0]], int(day[0]))
        datetime = dt.datetime.combine(date, time.time(), tzinfo=moscow_tz)
        return source, str(datetime).replace(' ', 'T')

    date = dt.datetime.now().date()
    datetime = dt.datetime.combine(date, time.time(), tzinfo=moscow_tz)
    return info, str(datetime).replace(' ', 'T')


def parse_yandex_news():
    main_link = 'https://yandex.ru/news/'
    rsp = requests.get(main_link, headers=header)
    dom = html.fromstring(rsp.text)

    news_items = dom.xpath('//div[contains(@class, "story__topic")]/h2')
    news = []
    for item in news_items:
        link = item.xpath('.//a/@href')[0].replace('/news/', main_link)
        title = item.xpath('.//a/text()')[0]

        info = item.xpath('..//..//div[@class="story__info"]/div[@class="story__date"]/text()')[0]

        source, datetime = parse_yandex_news_info(info)

        news_dict = {'link': link, 'title': title, 'datetime': datetime, 'source': source}
        news.append(news_dict)
    return news


def get_mail_news_info(link, interval=3):
    rsp = requests.get(link, headers=header)
    sleep(interval)
    dom = html.fromstring(rsp.text)
    info = dom.xpath('//div[@class="breadcrumbs breadcrumbs_article js-ago-wrapper"]')[0]
    datetime = info.xpath('.//span[@datetime]/@datetime')[0]
    source = info.xpath('.//span[@class="link__text"]/text()')[0]
    return datetime, source


def parse_mail_news():
    main_link = 'https://news.mail.ru'
    rsp = requests.get(main_link, headers=header)
    dom = html.fromstring(rsp.text)

    news_ref_parents = dom.xpath('//div[@class="daynews__item"] '
                                 '| //li[contains(@class, "list__item")] '
                                 '| //span[@class="cell"]')

    news = []
    for item in news_ref_parents:
        link = item.xpath('.//a/@href')[0]
        full_link = f'{main_link}{link}'

        title = item.xpath('.//a/text()')
        if len(title) == 0:
            inner = item.xpath('.//span[contains(@span, title)]/text()')
            title = inner[0]

        datetime, source = get_mail_news_info(full_link, SLEEP_INTERVAL)
        news_dict = {'link': full_link, 'title': title, 'datetime': datetime, 'source': source}
        news.append(news_dict)

    return news


lenta_news = parse_lenta()
yandex_news = parse_yandex_news()
mail_news = parse_mail_news()

client = MongoClient('192.168.19.48', 8080)
db = client['news']
news_db = db.news

for news in yandex_news:
    news_db.update_one({'link': news['link']}, {'$set': news}, upsert=True)

for news in lenta_news:
    news_db.update_one({'link': news['link']}, {'$set': news}, upsert=True)

for news in mail_news:
    news_db.update_one({'link': news['link']}, {'$set': news}, upsert=True)
