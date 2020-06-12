from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from transliterate import translit, get_available_language_codes

main_link_hh = 'https://hh.ru'
main_link_sj = 'https://www.superjob.ru'


def parse_salary(salary_text):
    if '-' in salary_text:
        tokens = salary_text.split('-')
        t_tokens = tokens[1].split(' ')
        return tokens[0], t_tokens[0], t_tokens[1]
    if 'от' in salary_text:
        tokens = salary_text.split(' ')
        return tokens[1], '', tokens[2]
    if 'до' in salary_text:
        tokens = salary_text.split(' ')
        return '', tokens[1], tokens[2]
    tokens = salary_text.split(' ')
    return tokens[0], tokens[0], tokens[1]


def parse_sj_salary(salary_text):
    if salary_text == 'По договорённости':
        return '', '', ''
    salary_text = salary_text.replace('от', 'от ').replace('до', 'до ').replace('руб.', ' руб.').replace('—', '-')
    return parse_salary(salary_text)


def get_hh_vacancy_data(vacancy_struct):
    link_data = vacancy_struct.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
    link = link_data['href']
    title = link_data.text
    salary_data = vacancy_struct.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if salary_data is not None:
        min_salary, max_salary, currency = parse_salary(salary_data.text.replace(u'\xa0', ''))
    else:
        min_salary, max_salary, currency = '', '', ''
    min_salary = f'{min_salary}{currency}' if min_salary != '' else ''
    max_salary = f'{max_salary}{currency}' if max_salary != '' else ''
    return {'title': title, 'link': link, 'min_salary': min_salary, 'max_salary': max_salary, 'site': main_link_hh}


def get_sj_vacancy_data(vacancy_struct):
    link_data = vacancy_struct.find('a')
    link = f"{main_link_sj}{link_data['href']}"
    title = link_data.text
    salary_data = vacancy_struct.find('span', {'class': 'f-test-text-company-item-salary'})
    min_salary, max_salary, currency = parse_sj_salary(salary_data.text.replace(u'\xa0', ''))
    min_salary = f'{min_salary}{currency}' if min_salary != '' else ''
    max_salary = f'{max_salary}{currency}' if max_salary != '' else ''
    return {'title': title, 'link': link, 'min_salary': min_salary, 'max_salary': max_salary, 'site': main_link_sj}


query_vacancy = input('vacancy: ')
query_pages = int(input('search pages: '))

vacancies = pd.DataFrame()
for page in range(query_pages):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

    hh_params = {'text': query_vacancy, 'page': page}
    rsp = requests.get(f'{main_link_hh}/search/vacancy', params=hh_params, headers=header)
    soup = bs(rsp.text, 'html.parser')
    rsp_vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})
    for v in rsp_vacancies:
        vacancies = vacancies.append(get_hh_vacancy_data(v), ignore_index=True)

    sj_params = {'page': page + 1}
    rsp = requests.get(f'{main_link_sj}/vakansii/{translit(query_vacancy, reversed=True)}.html', params=hh_params, headers=header)
    soup = bs(rsp.text, 'html.parser')
    rsp_vacancies = soup.find_all('div', {'class': 'f-test-vacancy-item'})
    for v in rsp_vacancies:
        vacancies = vacancies.append(get_sj_vacancy_data(v), ignore_index=True)

vacancies.to_csv('vacancies_data.csv')
