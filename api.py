import requests, json

def daos(daoAddress):

    # Запрос на json с DAOs
    url = f'https://dev-ton-vote-cache.herokuapp.com/daos'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа
        
        return data

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/daos):', e)

# print(daos('EQDi7_28cJItXu5t5evsnEKNtUYv_1aQve21T4bzFxbxJ8HF'))


def daoAddressInfo(daoAddress):
    # Запрос на json с предложениями по DAO
    url = f'https://dev-ton-vote-cache.herokuapp.com/dao/{daoAddress}'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа

        name = json.loads(data['daoMetadata']['name'])['en']
        about = json.loads(data['daoMetadata']['about'])['en']
        avatar = data['daoMetadata']['avatar']
        website = data['daoMetadata']['github'] 
        telegram = data['daoMetadata']['telegram']
        github = data['daoMetadata']['github']

        countProposals = data['nextProposalId']
        daoProposals = data['daoProposals']

        return name, about, avatar, website, telegram, github, countProposals, daoProposals

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/dao/daoAddress):', e)

# print(daoAddressInfo('EQDi7_28cJItXu5t5evsnEKNtUYv_1aQve21T4bzFxbxJ8HF')[7][0])


def proposalAddressInfo(proposalAddress):

    # Запрос на json с предложениями по DAO
    url = f'https://dev-ton-vote-cache.herokuapp.com/proposal/{proposalAddress}'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа
        
        title = data['metadata']['title']
        description = data['metadata']['description']
        daoAddress = data['daoAddress']
        proposalStartTime = data['metadata']['proposalStartTime']
        proposalEndTime = data['metadata']['proposalEndTime']

        return title, description, daoAddress, proposalStartTime, proposalEndTime

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/proposal/proposalAddress):', e)
    
# print(proposal('EQCc8vSY5grdLTeTjqUnnCHDQ0mkf906cWf1ap_g0LeRShSg'))


