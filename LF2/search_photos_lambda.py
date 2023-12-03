import json
import boto3
import requests

from requests.auth import HTTPBasicAuth


def lambda_handler(event, context):
    intent = event['interpretations'][0]['intent']['name']

    search_intents = []
    photo_URLs = []
    if intent != 'FallbackIntent':
        first_photo_search_intent = event['interpretations'][0]['intent']['slots'].get('FirstPhotoIntent')
        second_photo_search_intent = event['interpretations'][0]['intent']['slots'].get('SecondPhotoIntent')

        search_intents.append(first_photo_search_intent['value']['originalValue'])
        if second_photo_search_intent is None:
            photo_URLs = search_OpenSearch_index(search_intents)
        else:
            search_intents.append(second_photo_search_intent['value']['originalValue'])
            photo_URLs = search_OpenSearch_index(search_intents)

    lex_response = response_to_lex(event, photo_URLs)
    return lex_response

    # return {
    #     'statusCode': 200,
    #     'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*",
    #                 "Access-Control-Allow-Headers": "*"},
    #     'body': json.dumps(photo_URLs)
    # }


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
        print(response)
        response = json.loads(response.content.decode('utf-8'))

        for hit in response['hits']['hits']:
            photo = hit['_source']['objectKey']
            photo_url = 'https://photo-bucket-2397.s3.amazonaws.com/' + photo
            photo_URLs.append(photo_url)

    return photo_URLs


def response_to_lex(event, photo_URLs):
    session_id = event['sessionId']
    request_id = event['sessionState']['originatingRequestId']
    intent = event['interpretations'][0]['intent']['name']
    nluConfidence = event['interpretations'][0]['nluConfidence']
    first_photo_search_intent = event['interpretations'][0]['intent']['slots'].get('FirstPhotoIntent')
    second_photo_search_intent = event['interpretations'][0]['intent']['slots'].get('SecondPhotoIntent')

    # client = boto3.client('lexv2-runtime')

    # send requestAttributes to the frontend
    requestAttributes = {}

    # no intent is recgonized
    if intent == 'FallbackIntent':
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Delegate"
                },
                "intent": {
                    "name": "FallbackIntent",
                    "slots": {},
                    "state": "ReadyForFulfillment",
                    "confirmationState": "None"
                },
                "sessionAttributes": {},
                "originatingRequestId": request_id
            },
            "interpretations": [
                {
                    "intent": {
                        "name": "FallbackIntent",
                        "slots": {},
                        "state": "ReadyForFulfillment",
                        "confirmationState": "None"
                    },
                    "interpretationSource": "Lex"
                },
                {
                    "nluConfidence": {
                        "score": nluConfidence
                    },
                    "intent": {
                        "name": "PhotoSearchIntent",
                        "slots": {
                            "FirstPhotoIntent": None,
                            "SecondPhotoIntent": None
                        }
                    },
                    "interpretationSource": "Lex"
                }
            ],
            "sessionId": session_id,
            "requestAttributes": requestAttributes
        }

    # only the first slot is fullfilled
    if not (first_photo_search_intent is None) and (second_photo_search_intent is None):
        i = 1
        for url in photo_URLs:
            key = 'photo' + str(i)
            requestAttributes[key] = url
            i = i + 1

        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Delegate"
                },
                "intent": {
                    "name": "PhotoSearchIntent",
                    "slots": {
                        "FirstPhotoIntent": {
                            "value": {
                                "originalValue": first_photo_search_intent['value']['originalValue'],
                                "interpretedValue": first_photo_search_intent['value']['originalValue'],
                                "resolvedValues": [
                                    first_photo_search_intent['value']['originalValue']
                                ]
                            }
                        },
                        "SecondPhotoIntent": None
                    },
                    "state": "ReadyForFulfillment",
                    "confirmationState": "None"
                },
                "sessionAttributes": {},
                "originatingRequestId": request_id
            },
            "interpretations": [
                {
                    "nluConfidence": {
                        "score": nluConfidence
                    },
                    "intent": {
                        "name": "PhotoSearchIntent",
                        "slots": {
                            "FirstPhotoIntent": {
                                "value": {
                                    "originalValue": first_photo_search_intent['value']['originalValue'],
                                    "interpretedValue": first_photo_search_intent['value']['originalValue'],
                                    "resolvedValues": [
                                        first_photo_search_intent['value']['originalValue']
                                    ]
                                }
                            },
                            "SecondPhotoIntent": None
                        },
                        "state": "ReadyForFulfillment",
                        "confirmationState": "None"
                    },
                    "interpretationSource": "Lex"
                },
                {
                    "intent": {
                        "name": "FallbackIntent",
                        "slots": {}
                    },
                    "interpretationSource": "Lex"
                }
            ],
            "sessionId": session_id,
            "requestAttributes": requestAttributes
        }

    # both the first and second slot are fullfilled
    elif not (first_photo_search_intent is None) and not (second_photo_search_intent is None):
        i = 1
        for url in photo_URLs:
            key = 'photo' + str(i)
            requestAttributes[key] = url
            i = i + 1

        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Delegate"
                },
                "intent": {
                    "name": "PhotoSearchIntent",
                    "slots": {
                        "FirstPhotoIntent": {
                            "value": {
                                "originalValue": first_photo_search_intent['value']['originalValue'],
                                "interpretedValue": first_photo_search_intent['value']['originalValue'],
                                "resolvedValues": [
                                    first_photo_search_intent['value']['originalValue']
                                ]
                            }
                        },
                        "SecondPhotoIntent": {
                            "value": {
                                "originalValue": second_photo_search_intent['value']['originalValue'],
                                "interpretedValue": second_photo_search_intent['value']['originalValue'],
                                "resolvedValues": [
                                    second_photo_search_intent['value']['originalValue']
                                ]
                            }
                        }
                    },
                    "state": "ReadyForFulfillment",
                    "confirmationState": "None"
                },
                "sessionAttributes": {},
                "originatingRequestId": request_id
            },
            "interpretations": [
                {
                    "nluConfidence": {
                        "score": nluConfidence
                    },
                    "intent": {
                        "name": "PhotoSearchIntent",
                        "slots": {
                            "FirstPhotoIntent": {
                                "value": {
                                    "originalValue": first_photo_search_intent['value']['originalValue'],
                                    "interpretedValue": first_photo_search_intent['value']['originalValue'],
                                    "resolvedValues": [
                                        first_photo_search_intent['value']['originalValue']
                                    ]
                                }
                            },
                            "SecondPhotoIntent": {
                                "value": {
                                    "originalValue": second_photo_search_intent['value']['originalValue'],
                                    "interpretedValue": second_photo_search_intent['value']['originalValue'],
                                    "resolvedValues": [
                                        second_photo_search_intent['value']['originalValue']
                                    ]
                                }
                            }
                        },
                        "state": "ReadyForFulfillment",
                        "confirmationState": "None"
                    },
                    "interpretationSource": "Lex"
                },
                {
                    "intent": {
                        "name": "FallbackIntent",
                        "slots": {}
                    },
                    "interpretationSource": "Lex"
                }
            ],
            "sessionId": session_id,
            "requestAttributes": requestAttributes
        }