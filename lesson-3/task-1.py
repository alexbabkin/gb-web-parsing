from pymongo import MongoClient
from pprint import pprint
from vacancy_parser import hh_vacancy, sj_vacancy

client = MongoClient('192.168.19.48', 8080)
db = client['vacancies']
vacancy_db = db.vacancy
vacancy_db.delete_many({})

query_vacancy = input('vacancy: ')
query_pages = int(input('search pages: '))

sj_vs = sj_vacancy.get_vacancies(query_pages, query_vacancy)
hh_vs = hh_vacancy.get_vacancies(query_pages, query_vacancy)

vacancy_db.insert_many(sj_vs)
vacancy_db.insert_many(hh_vs)

search_salary_currency = input('salary currency: ').lower()
search_salary_value = float(input('salary value: '))
is_minimal = bool(input('should minimal salary be greater than entered? (0 or 1): ') or False)

# В случае если в вакансии указана только одна величина зп, а не диапазон,
# эта величина принимается за максимальную и минимальную при парсинге
if is_minimal:
    search_result = vacancy_db.find(
        {'currency': f'{search_salary_currency}', 'min_salary': {'$gt': search_salary_value}})
else:
    search_result = vacancy_db.find(
        {'currency': f'{search_salary_currency}', 'max_salary': {'$gt': search_salary_value}})

for sr in search_result:
    pprint(sr)
