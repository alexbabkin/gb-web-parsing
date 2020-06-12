
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


def get_request_header():
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.61 Safari/537.36'}
    return header
