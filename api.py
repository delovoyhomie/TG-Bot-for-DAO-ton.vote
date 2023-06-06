import requests, json
import endpoints_cache

# /daos is not used
def daos(daoAddress):

    # Запрос на json с DAOs
    url = f'{endpoints_cache.dev_api}/daos'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа
        
        return data

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/daos):', e)

# print(daos('EQDi7_28cJItXu5t5evsnEKNtUYv_1aQve21T4bzFxbxJ8HF'))


def daoAddressInfo(daoAddress):
    # Запрос на json с предложениями по DAO
    url = f'{endpoints_cache.dev_api}/dao/{daoAddress}'

    try:
        response = requests.get(url)
        data = response.json()  # Получение JSON-данных из ответа

        name = json.loads(data['daoMetadata']['metadataArgs']['name'])['en']
        about = json.loads(data['daoMetadata']['metadataArgs']['about'])['en']
        avatar = data['daoMetadata']['metadataArgs']['avatar']
        website = data['daoMetadata']['metadataArgs']['github'] 
        telegram = data['daoMetadata']['metadataArgs']['telegram']
        github = data['daoMetadata']['metadataArgs']['github']

        countProposals = data['nextProposalId']
        daoProposals = data['daoProposals']

        return name, about, avatar, website, telegram, github, countProposals, daoProposals

    except Exception as e:
        print('Произошла ошибка при выполнении запроса (/dao/daoAddress):', e)

# print(daoAddressInfo('EQA-Qno-vCjLbDJXxOB-vhHY8sH8hVbH4if-iSMi-JwaIdP4'))


def proposalAddressInfo(proposalAddress):

    # Запрос на json с предложениями по DAO
    url = f'{endpoints_cache.dev_api}/proposal/{proposalAddress}'

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
    
# print(proposalAddressInfo('EQDUYK1eiH8a67w0QaiHyD6Xx6Y8DpUO22B00L9nY9CdTmgQ'))
