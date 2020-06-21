from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import datetime as dt
import pytz
from time import sleep
from pymongo import MongoClient


DAYS = ['1 ', '2 ', '3 ', '4 ', '5 ', '6 ', '7 ', '8 ', '9 ', '10 ',
        '11 ', '12 ', '13 ', '14 ', '15 ', '16 ', '17 ', '18 ', '19 ', '20 ',
        '21 ', '22 ', '23 ', '24 ', '25 ', '26 ', '27 ', '28 ', '29 ', '30 ', '31 ']
MONTHS = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7,
          'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}


def parse_datetime(date_str):
    date, time = date_str.split(',')
    year = date_str.replace(time, '').replace(',', '').replace(date, '')
    time = dt.datetime.strptime(time.strip(), '%H:%M', )
    moscow_tz = pytz.timezone('Europe/Moscow')

    day = list(filter(lambda d: d in date, DAYS))
    month = list(filter(lambda m: m in date, MONTHS.keys()))

    date = dt.date(int(year) if year != '' else 2020, MONTHS[month[0]], int(day[0]))
    datetime = dt.datetime.combine(date, time.time(), tzinfo=moscow_tz)
    return datetime


driver = webdriver.Chrome()

driver.get('https://mail.ru/')

login_field = driver.find_element_by_id('mailbox:login')
login_field.send_keys('study.ai_172')

domain_filed = driver.find_element_by_id('mailbox:domain')
select = Select(domain_filed)
select.select_by_visible_text("@mail.ru")
domain_filed.click()

enter_pass_button = driver.find_element_by_xpath("//input[@value='Ввести пароль']")
enter_pass_button.click()

pass_field = driver.find_element_by_id('mailbox:password')
pass_field.send_keys('NextPassword172')

enter_button = driver.find_element_by_xpath("//input[@value='Ввести пароль']")
enter_button.click()

wait_element = WebDriverWait(driver, 5).until(
        ec.visibility_of_all_elements_located((By.CLASS_NAME, 'js-letter-list-item'))
    )

mails_urls = {}
while True:
    mails = driver.find_elements_by_class_name('js-letter-list-item')

    added_mails = 0
    for m in mails:
        if m.id not in mails_urls.keys():
            added_mails += 1
            mails_urls[m.id] = m.get_attribute('href')
    if added_mails == 0:
        break

    driver.execute_script("arguments[0].scrollIntoView(true);", mails[-1])
    sleep(1)

mails_data = []
for m in mails_urls.values():
    driver.get(m)

    wait_element = WebDriverWait(driver, 5).until(
        ec.visibility_of_all_elements_located((By.CLASS_NAME, 'js-readmsg-msg'))
    )

    sender_elem = driver.find_element_by_xpath('//div[@class="letter__author"]/span[@class="letter-contact"]')
    sender = sender_elem.get_attribute('title')
    date = driver.find_element_by_xpath("//div[@class='letter__date']").text
    theme = driver.find_element_by_xpath("//h2[@class='thread__subject thread__subject_pony-mode']").text
    body = driver.find_element_by_xpath('//div[@class="js-helper js-readmsg-msg"]').text
    news_dict = {'link': m, 'sender': sender, 'datetime': parse_datetime(date), 'theme': theme, 'body': body}
    mails_data.append(news_dict)


client = MongoClient('192.168.19.48', 8080)
db = client['mails']
mails_db = db.mails

for mail in mails_data:
    mails_db.update_one({'link': mail['link']}, {'$set': mail}, upsert=True)

driver.close()
