# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


def fetch_csrf_token(text):
    matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
    return matched.split(':').pop().replace(r'"', '')


def fetch_user_id(text, username):
    matched = re.search(
        '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
    ).group()
    return json.loads(matched).get('id')


def get_graphql_url(graphql_url, query_hash, variables):
    return f'{graphql_url}query_hash={query_hash}&{urlencode(variables)}'


class InstagramSpider(scrapy.Spider):
    # атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']

    insta_login = 'babkin.alex.alex'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:9:1593381447:AVdQAEiSo24O1Ml1wrdIZngF8rIdBnQjV1DkAxECpLQyJJVe1xGo' \
                'EP3xkITvl9cPl1kZfnCOIWavCPnCx0S1QJUi47UB67G0Brcly+5EXf+Qv4EBH3RPK5NbKLPJC71IhC+GdNlx3qdZFhbi'
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    users_to_parse = ['tecom_group', 'nntu.alekseeva']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    subscribers_hash = 'c76146de99bb02f6415203be841dd25a'
    subscribes_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response: HtmlResponse):  # Первый запрос на стартовую страницу
        csrf_token = fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.insta_login_link,
            method='POST',
            callback=self.go_to_user,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def go_to_user(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:  # Проверяем ответ после авторизации
            for user in self.users_to_parse:
                yield response.follow(
                    # Переходим на желаемую страницу пользователя. Сделать цикл для кол-ва пользователей больше 2-ух
                    f'/{user}',
                    callback=self.collect_user_data,
                    cb_kwargs={'username': user}
                )

    def collect_user_data(self, response: HtmlResponse, username):
        user_id = fetch_user_id(response.text, username)  # Получаем id пользователя
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}

        yield response.follow(
            get_graphql_url(self.graphql_url, self.subscribers_hash, variables),
            callback=self.parse_user,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables),
                       'query_hash': self.subscribers_hash}
        )

        yield response.follow(
            get_graphql_url(self.graphql_url, self.subscribes_hash, variables),
            callback=self.parse_user,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables),
                       'query_hash': self.subscribes_hash}
        )

    def parse_user(self, response: HtmlResponse, username, user_id,
                   variables, query_hash):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        target_type = 'followed_by' if query_hash == self.subscribers_hash else 'follow'
        if target_type == 'followed_by':
            data = j_data.get('data').get('user').get('edge_followed_by')
        else:
            data = j_data.get('data').get('user').get('edge_follow')

        page_info = data.get('page_info')

        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
            yield response.follow(
                get_graphql_url(self.graphql_url, query_hash, variables),
                callback=self.parse_user,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables),
                           'query_hash': query_hash}
            )
        users = data.get('edges')
        for user in users:
            item = InstaparserItem(
                username=username,
                target_type=target_type,
                id=user_id,
                photo=user['node']['profile_pic_url'],
                name=user['node']['username']
            )
            yield item  # В пайплайн
