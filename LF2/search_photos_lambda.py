def lambda_handler(event, context):
    response = prepare_lex_response(event)
    return response


def prepare_lex_response(event):
    intent = event['sessionState']['intent']['name']
    session_id = event['sessionId']
    request_id = event['sessionState']['originatingRequestId']
    nluConfidence = event['interpretations']['nluConfidence']

    # no intent is recgonized
    if intent == 'FallbackIntent':
        response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
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
                            "FirstPhotoIntent": null,
                            "SecondPhototIntent": null
                        }
                    },
                    "interpretationSource": "Lex"
                }
            ],
            "sessionId": session_id
        }
        return response

    first_photo_search_intent = event['sessionState']['intent']['slots']["FirstPhotoIntent"]
    second_photo_search_intent = event['sessionState']['intent']['slots']["SecondPhotoIntent"]

    if first_photo_search_intent != 'null' and second_photo_search_intent == 'null':
        first_slot_value = first_photo_search_intent['value']['originalValue']
        response = {
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
                },
                "intent": {
                    "name": "PhotoSearchIntent",
                    "slots": {
                        "FirstPhotoIntent": {
                            "value": {
                                "originalValue": first_slot_value,
                                "interpretedValue": first_slot_value,
                                "resolvedValues": [
                                    first_slot_value
                                ]
                            }
                        },
                        "SecondPhototIntent": null
                    },
                    "state": "InProgress",
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
                                    "originalValue": first_slot_value,
                                    "interpretedValue": first_slot_value,
                                    "resolvedValues": [
                                        first_slot_value
                                    ]
                                }
                            },
                            "SecondPhototIntent": null
                        },
                        "state": "InProgress",
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
            "sessionId": session_id
        }

    elif first_photo_search_intent != 'null' and second_photo_search_intent != 'null':
        first_slot_value = first_photo_search_intent['value']['originalValue']
        second_slot_value = secondt_photo_search_intent['value']['originalValue']
        response = {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": "PhotoSearchIntent",
                    "slots": {
                        "FirstPhotoIntent": {
                            "value": {
                                "originalValue": first_slot_value,
                                "interpretedValue": first_slot_value,
                                "resolvedValues": [
                                    first_slot_value
                                ]
                            }
                        },
                        "SecondPhototIntent": {
                            "value": {
                                "originalValue": second_slot_value,
                                "interpretedValue": second_slot_value,
                                "resolvedValues": [
                                    second_slot_value
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
                                    "originalValue": first_slot_value,
                                    "interpretedValue": first_slot_value,
                                    "resolvedValues": [
                                        first_slot_value
                                    ]
                                }
                            },
                            "SecondPhototIntent": {
                                "value": {
                                    "originalValue": second_slot_value,
                                    "interpretedValue": second_slot_value,
                                    "resolvedValues": [
                                        second_slot_value
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
            "sessionId": session_id
        }
