import requests, json
import endpoints_cache

def daos(daoAddress):

    # Запрос на json с DAOs
    url = f'{endpoints_cache.production}/daos'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа
        
        return data

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/daos):', e)

# print(daos('EQDi7_28cJItXu5t5evsnEKNtUYv_1aQve21T4bzFxbxJ8HF'))


def daoAddressInfo(daoAddress):
    # Запрос на json с предложениями по DAO
    url = f'{endpoints_cache.production}/dao/{daoAddress}'

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
    url = f'{endpoints_cache.production}/proposal/{proposalAddress}'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа
        
        title = json.loads(data['metadata']['title'])['en']
        description = json.loads(data['metadata']['description'])['en']
        daoAddress = data['daoAddress']
        proposalStartTime = data['metadata']['proposalStartTime']
        proposalEndTime = data['metadata']['proposalEndTime']


        
        #proposalResult
        yes, no, abstain = None, None, None
        if data['proposalResult']:
            yes = data['proposalResult']['yes']
            no = data['proposalResult']['no']
            abstain = data['proposalResult']['abstain']
        
        return title, description, daoAddress, proposalStartTime, proposalEndTime, yes, no, abstain

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/proposal/proposalAddress):', e)
    
# print(proposalAddressInfo('EQDfb8TzJjHrbeK7KnOv_Ao5pVBTP02uK8NiXaP4MlmU0y6N')[1])
