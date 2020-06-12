from .common import parse_salary, get_request_header
from bs4 import BeautifulSoup as bs
import requests
from transliterate import translit


main_link_sj = 'https://www.superjob.ru'


def get_sj_vacancy_data(vacancy_struct):
    link_data = vacancy_struct.find('a')
    link = f"{main_link_sj}{link_data['href']}"
    title = link_data.text
    salary_data = vacancy_struct.find('span', {'class': 'f-test-text-company-item-salary'})
    min_salary, max_salary, currency = parse_sj_salary(salary_data.text.replace(u'\xa0', ''))
    min_salary = float(min_salary) if min_salary != '' else ''
    max_salary = float(max_salary) if max_salary != '' else ''
    return {'title': title, 'link': link, 'min_salary': min_salary,
            'max_salary': max_salary,  'currency': currency.lower().replace('.', ''), 'site': main_link_sj}


def parse_sj_salary(salary_text):
    if salary_text == 'По договорённости':
        return '', '', ''
    salary_text = salary_text.replace('от', 'от ').replace('до', 'до ').replace('руб.', ' руб.').replace('—', '-')
    return parse_salary(salary_text)


def get_vacancies(num_of_pages, vacancy_name):
    vacancies = []
    for page in range(num_of_pages):
        sj_params = {'page': page + 1}
        rsp = requests.get(f'{main_link_sj}/vakansii/{translit(vacancy_name, reversed=True)}.html', params=sj_params,
                           headers=get_request_header())
        soup = bs(rsp.text, 'html.parser')
        rsp_vacancies = soup.find_all('div', {'class': 'f-test-vacancy-item'})
        for v in rsp_vacancies:
            vacancies.append(get_sj_vacancy_data(v))
    return vacancies
