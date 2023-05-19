import requests, json

def daos(daoAddress):

    # Запрос на json с DAOs
    url = f'https://dev-ton-vote-cache.herokuapp.com/daos'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа
        
        return data

        # for i in range(len(data)):
        #     address = data[i]['daoAddress'] 
        #     if address == daoAddress:
        #         print(data[i])
        #         return data[i]
            
        # return 'Not Found'

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/daos):', e)

# print(daos('EQDi7_28cJItXu5t5evsnEKNtUYv_1aQve21T4bzFxbxJ8HF'))


def daoAddressInfo(daoAddress):
    # Запрос на json с предложениями по DAO
    url = f'https://dev-ton-vote-cache.herokuapp.com/dao/{daoAddress}'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа

        about = json.loads(data['daoMetadata']['about'])['en']
        avatar = data['daoMetadata']['avatar']
        website = data['daoMetadata']['github'] 
        name = json.loads(data['daoMetadata']['name'])['en']
        telegram = data['daoMetadata']['telegram']
        website = data['daoMetadata']['website']
        
        print(about, avatar, website, name, telegram, website, sep = '\n')

        return data

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/dao/daoAddress):', e)

print(daoAddressInfo('EQDi7_28cJItXu5t5evsnEKNtUYv_1aQve21T4bzFxbxJ8HF'))


def proposal(daoAddress):

    # Запрос на json с предложениями по DAO
    url = f'https://dev-ton-vote-cache.herokuapp.com/proposal/{daoAddress}'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа
        return data
    
        # Обработка полученных данных
        # ...daoAddress

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/proposal/address_dao):', e)
    
# print(proposal('EQCc8vSY5grdLTeTjqUnnCHDQ0mkf906cWf1ap_g0LeRShSg'))
