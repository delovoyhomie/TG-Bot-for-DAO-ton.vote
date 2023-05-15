import requests, json

url = 'https://dev-ton-vote-cache.herokuapp.com/daos'  # Замените URL на свой API-эндпоинт

def daos():
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на наличие ошибок HTTP

        data = response.json()  # Получение JSON-данных из ответа
        return data
        # Обработка полученных данных
        # ...

    except requests.exceptions.RequestException as e:
        print('Произошла ошибка при выполнении запроса:', e)
    except json.JSONDecodeError as e:
        print('Произошла ошибка при декодировании JSON:', e)
