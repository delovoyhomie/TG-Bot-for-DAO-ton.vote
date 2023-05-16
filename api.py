import requests, json

def proposal(address_dao):

    # Запрос на json с предложениями по DAO
    url = f'https://dev-ton-vote-cache.herokuapp.com/proposal/{address_dao}'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа
        return data
    
        # Обработка полученных данных
        # ...daoAddress

    except:
        print('Произошла ошибка при выполнении запроса (/daos):')
    
# print(proposal('EQCc8vSY5grdLTeTjqUnnCHDQ0mkf906cWf1ap_g0LeRShSg'))
