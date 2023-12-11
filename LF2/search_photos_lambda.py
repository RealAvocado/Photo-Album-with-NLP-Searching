import json
import boto3
import requests

from requests.auth import HTTPBasicAuth

lexbot = boto3.client('lexv2-runtime')

def lambda_handler(event, context):
    search_intents = []
    query = event['q']
    response_from_lex = lexbot.recognize_text(
        botId='4IGQQYF4KC',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId='202312101159',
        text=query,
    )

    # no intent is fulfilled
    if response_from_lex['sessionState']['intent']['name'] == 'FallbackIntent':
        return []

    # else if at least an intent is fulfilled
    first_photo_slot = response_from_lex['sessionState']['intent']['slots']['FirstPhotoIntent']
    second_photo_slot = response_from_lex['sessionState']['intent']['slots']['SecondPhotoIntent']

    if second_photo_slot is None:
        search_intents.append(first_photo_slot['value']['originalValue'])
    else:
        search_intents.append(first_photo_slot['value']['originalValue'])
        search_intents.append(second_photo_slot['value']['originalValue'])

    photo_URLs = search_OpenSearch_index(search_intents)
    return photo_URLs

def search_OpenSearch_index(search_intents):
    photo_URLs = []

    username = 'opensearch-user'
    password = '***************'
    index = 'photos'
    host = 'https://search-photos-a2wikxciocdgnhqczvcuy6zzqa.us-east-1.es.amazonaws.com'

    search_url_base = host + '/' + index + '/' + '_search?q='

    for intent in search_intents:
        search_url = search_url_base + intent
        response = requests.get(search_url, auth=HTTPBasicAuth(username, password))
        print(response)
        # ============! ATTENTION !===========================
        response = json.loads(response.content.decode('utf-8'))

        for hit in response['hits']['hits']:
            photo = hit['_source']['objectKey']
            photo_url = 'https://photo-bucket-2397.s3.amazonaws.com/' + photo
            photo_URLs.append(photo_url)

    return photo_URLs
