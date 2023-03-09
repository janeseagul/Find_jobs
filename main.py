import requests
from terminaltables import AsciiTable
import os


def predict_rub_salary(salary_from, salary_to=None):
    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    if salary_from:
        return int(salary_from * 1.2)
    if salary_to:
        return int(salary_to * 0.8)


def get_vacancies_stats_hh(languages):
    url = 'https://api.hh.ru/vacancies'
    vacancies_stats = {}
    for language in languages:
        page = 0
        salaries_count = 0
        salaries_sum = 0
        while True:
            params = {
                'text': f'программист {language}',
                'area': 1,
                'per_page': 100,
                'page': page,
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if not data['items']:
                break
            for vacancy in data['items']:
                salary = predict_rub_salary(vacancy.get('salary', {}).get('from'), vacancy.get('salary', {}).get('to'))
                if salary:
                    salaries_count += 1
                    salaries_sum += salary
            page += 1
        if salaries_count:
            vacancies_stats[language] = {
                'vacancies_found': data['found'],
                'vacancies_processed': params['page'] * 100,
                'salaries_found': salaries_count,
                'average_salary': int(salaries_sum / salaries_count) if salaries_count else 0
            }

    return vacancies_stats


def predict_rub_salary_hh(vacancy):
    salary = vacancy["salary"]
    if not salary:
        return None
    if not salary['currency'] == 'RUR':
        return None
    if salary['gross']:
        gross = 0.87
    else:
        gross = 1
    if salary['from']:
        salary_from = int(salary['from'] * gross)
    else:
        salary_from = None
    if salary['to']:
        salary_to = int(salary['to'] * gross)
    else:
        salary_to = None
    return predict_rub_salary(salary_from, salary_to)


def get_vacancies_stats_sj(languages, sj_api_key):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': sj_api_key,
    }
    vacancies_stats = {}
    for language in languages:
        page = 0
        salaries_count = 0
        salaries_sum = 0
        while True:
            params = {
                'keyword': f'программист {language}',
                'town': 'Москва',
                'count': 100,
                'page': page
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if not data['objects']:
                break
            for vacancy in data['objects']:
                salary = predict_rub_salary(vacancy.get('payment', {}).get('from'),
                                            vacancy.get('payment', {}).get('to'))
                if salary:
                    salaries_count += 1
                    salaries_sum += salary
            page += 1
        if salaries_count:
            vacancies_stats[language] = {
                'vacancies_found': data['more'],
                'vacancies_processed': params['page'] * 100,
                'salaries_found': salaries_count,
                'average_salary': int(salaries_sum / salaries_count) if salaries_count else 0
            }

    return vacancies_stats


def predict_rub_salary_sj(vacancy):
    if not vacancy['currency'] == 'rub':
        return None
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    return predict_rub_salary(salary_from, salary_to)


def draw_table(stats, title):
    table_lines = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано',
         'Средняя зарплата']
    ]
    for language in stats:
        table_lines.append(
            [
                language,
                stats[language]["vacancies_found"],
                stats[language]["vacancies_processed"],
                stats[language]["average_salary"],
            ]
        )
    table_instance = AsciiTable(table_lines, title)
    print(table_instance.table)


def main():
    languages = [
        'Java',
        'Python',
        'JavaScript',
        'Ruby',
        'PHP',
        'C++',
        'CSS',
        'C#',
        'C',
        'Go',
        'Shell',
        'Objective-C',
        'Scala',
        'Swift',
        'TypeScript'
    ]
    sj_api_key = os.environ['SJ_API_KEY']
    stats_hh = get_vacancies_stats_hh(languages)
    title_hh = 'HeadHunter Moscow'
    draw_table(stats_hh, title_hh)
    stats_sj = get_vacancies_stats_sj(languages, sj_api_key)
    title_sj = 'SuperJob Moscow'
    draw_table(stats_sj, title_sj)


if __name__ == '__main__':
    main()
