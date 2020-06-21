from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pymongo import MongoClient
import json
from json import JSONDecodeError

options = Options()
options.add_argument('start-maximized')

driver = webdriver.Chrome(options=options)

driver.get('https://www.mvideo.ru/')

try:
    wait_element = WebDriverWait(driver, 10).until(
        ec.visibility_of_all_elements_located((By.CLASS_NAME, 'tooltipster-box'))
    )
    driver.find_element_by_class_name('tooltipster-close').click()
except TimeoutException:
    pass

blocks = driver.find_elements_by_xpath('//div[@data-init="gtm-push-products"]')
target_block = None
for b in blocks:
    try:
        b.find_element_by_xpath('.//div[contains(text(),"Хиты продаж")]')
        target_block = b
        break
    except NoSuchElementException:
        continue

next_button = target_block.find_element_by_class_name('next-btn')
while True:
    next_button.click()
    if 'disabled' in next_button.get_attribute('class'):
        break

items = target_block.find_elements_by_xpath('.//a[@data-product-info]')
products = []
for i in items:
    data = i.get_attribute('data-product-info')
    try:
        info = json.loads(data)
        products.append(info)
    except JSONDecodeError:
        continue

client = MongoClient('192.168.19.48', 8080)
db = client['products']
products_db = db.products

for p in products:
    products_db.update_one({'productId': p['productId']}, {'$set': p}, upsert=True)

driver.close()
