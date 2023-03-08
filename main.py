import requests
from terminaltables import AsciiTable
import os

def predict_rub_salary(vacancy):
    try:
        salary = vacancy['salary']
        if salary['currency'] != 'RUR':
            return None
        if salary['from'] and salary['to']:
            return (salary['from'] + salary['to']) // 2
        elif salary['from']:
            return salary['from'] * 1.2
        elif salary['to']:
            return salary['to'] * 0.8
        else:
            return None
    except TypeError:
        return None


def get_vacancies_dataset_hh(languages):
    url = 'https://api.hh.ru/vacancies'
    vacancies_data = {}
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
                'only_with_salary': True
            }
            response = requests.get(url, params=params)
            data = response.json()
            if not data['items']:
                break
            for vacancy in data['items']:
                salary = predict_rub_salary(vacancy)
                if salary:
                    salaries_count += 1
                    salaries_sum += salary
            page += 1
        if salaries_count:
           vacancies_data[language] = {
                'vacancies_found': data['found'],
                'vacancies_processed': page * 100,
                'salaries_found': salaries_count,
                'average_salary': int(salaries_sum / salaries_count)
            }

    return vacancies_data


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


def get_vacancies_dataset_sj(languages, sj_api_key):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': sj_api_key,
    }
    vacancies_data = {}
    for language in languages:
        page = 0
        salaries_count = 0
        salaries_sum = 0
        while True:
            params = {
                'page': page,
                'count': 100,
                'town': 4,
                'period': 30,
                'keyword': language,
                'keywords': ['программист', 'программиста', 'разработка']
            }
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if not data['items']:
                break
            for vacancy in data['items']:
                salary = predict_rub_salary(vacancy)
                if salary:
                    salaries_count += 1
                    salaries_sum += salary
            page += 1
        if salaries_count:
             vacancies_data({
                 'languages':language,
                 'vacancies_found': data['found'],
                 'vacancies_processed': page * 100,
                 'average_salary': int(salaries_sum / salaries_count)
            })

    return vacancies_data

def predict_rub_salary_sj(vacancy):
    if not vacancy['currency'] == 'rub':
        return None
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    return predict_rub_salary(salary_from, salary_to)


def draw_table(dataset, title):
    table_lines = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано',
         'Средняя зарплата']
    ]
    for language in dataset:
        table_lines.append(
            [   
                language,
                dataset[language]["vacancies_found"],
                dataset[language]["vacancies_processed"],
                dataset[language]["average_salary"],
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
    dataset_hh = get_vacancies_dataset_hh(languages)
    title_hh = 'HeadHunter Moscow'
    draw_table(dataset_hh, title_hh)
    dataset_sj = get_vacancies_dataset_sj(languages, sj_api_key)
    title_sj = 'SuperJob Moscow'
    draw_table(dataset_sj, title_sj)

if __name__ == '__main__':
    main()
