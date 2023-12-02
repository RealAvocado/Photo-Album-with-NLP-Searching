import json
import boto3
import requests

from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    session_id = event[sessionId]
    intent = event['sessionState']['intent']['name']
    first_photo_search_intent = event['sessionState']['intent']['slots'].get(["FirstPhotoIntent"], 'null')
    second_photo_search_intent = event['sessionState']['intent']['slots'].get(["SecondPhotoIntent"], 'null')

    send_response_to_lex(session_id, intent, first_photo_search_intent, second_photo_search_intent)

    search_intents = []
    # if no intent is fulfilled, return empty array
    if intent == 'FallbackIntent':
        return search_intents

    # else, at least one intent is fulfilled
    search_intents.append(first_photo_search_intent)
    if second_photo_search_intent != 'null':
        search_intents.append(second_photo_search_intent)

    photo_URLs = search_OpenSearch_index(search_intents)
    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*"},
        'body': json.dumps(photo_URLs)
    }


def send_response_to_lex(session_id, intent, first_photo_search_intent, second_photo_search_intent):
    client = boto3.client('lexv2-runtime')

    # no intent is recgonized
    if intent == 'FallbackIntent':
        lex_response = {
            "botId": "8JKTFL3V5D",
            "botAliasId": "TSTALIASID",
            "localeId": "en_US",
            "sessionId": session_id,
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                }
            }
        }
        response = client.put_session(lex_response)
        return response

    # only the first slot is fullfilled
    if first_photo_search_intent != 'null' and second_photo_search_intent == 'null':
        first_slot_value = first_photo_search_intent['value']['originalValue']
        lex_response = {
            "botId": "8JKTFL3V5D",
            "botAliasId": "TSTALIASID",
            "localeId": "en_US",
            "sessionId": session_id,
            "messages": [
                {
                    "content": "Enter the photo types.",
                    "contentType": "PlainText"
                }
            ],
            "sessionState": {
                "dialogAction": {
                    "type": "ElicitSlot",
                    "slotToElicit": "SecondPhototIntent"
                }
            }
        }
        response = client.put_session(lex_response)
        return response

    # both the first and second slot are fullfilled
    elif first_photo_search_intent != 'null' and second_photo_search_intent != 'null':
        first_slot_value = first_photo_search_intent['value']['originalValue']
        second_slot_value = secondt_photo_search_intent['value']['originalValue']
        lex_response = {
            "botId": "8JKTFL3V5D",
            "botAliasId": "TSTALIASID",
            "localeId": "en_US",
            "sessionId": session_id,
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                }
            }
        }
        response = client.put_session(lex_response)
        return response


def search_OpenSearch_index(search_intents):
    photo_URLs = []

    username = 'opensearch-user'
    password = 'h7-VUV21[o87hbtyuR'

    host = 'https://search-photos-a2wikxciocdgnhqczvcuy6zzqa.us-east-1.es.amazonaws.com'
    index = 'photos'
    search_url_base = host + '/' + index + '/' + '_search?q='

    for intent in search_intents:
        search_url = search_url_base + intent
        response = requests.get(search_url, auth=HTTPBasicAuth(username, password))
        photo = response['hits']['hits']['_source']['objectKey']
        photo_url = 'https://photo-bucket-2397.s3.amazonaws.com/' + photo
        photo_URLs.append(photo_url)

    return photo_URLs