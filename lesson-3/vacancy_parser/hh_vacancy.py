from .common import parse_salary, get_request_header
from bs4 import BeautifulSoup as bs
import requests

main_link_hh = 'https://hh.ru'


def get_hh_vacancy_data(vacancy_struct):
    link_data = vacancy_struct.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
    link = link_data['href']
    title = link_data.text
    salary_data = vacancy_struct.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if salary_data is not None:
        min_salary, max_salary, currency = parse_salary(salary_data.text.replace(u'\xa0', ''))
    else:
        min_salary, max_salary, currency = '', '', ''
    min_salary = float(min_salary) if min_salary != '' else ''
    max_salary = float(max_salary) if max_salary != '' else ''
    return {'title': title, 'link': link, 'min_salary': min_salary,
            'max_salary': max_salary,  'currency': currency.lower().replace('.', ''), 'site': main_link_hh}


def get_vacancies(num_of_pages, vacancy_name):
    vacancies = []
    for page in range(num_of_pages):
        hh_params = {'text': vacancy_name, 'page': page}
        rsp = requests.get(f'{main_link_hh}/search/vacancy', params=hh_params, headers=get_request_header())
        soup = bs(rsp.text, 'html.parser')
        rsp_vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})
        for v in rsp_vacancies:
            vacancies.append(get_hh_vacancy_data(v))
    return vacancies
