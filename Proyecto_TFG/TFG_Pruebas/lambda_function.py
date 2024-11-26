import json

# Validación del slot `IniciarEncuesta`
def validate(slots):
    if not slots['IniciarEncuesta'] or 'value' not in slots['IniciarEncuesta']:
        return {
            'isValid': False,
            'violatedSlot': 'IniciarEncuesta'
        }
    return {'isValid': True}

def lambda_handler(event, context):
    # Extraer información del intent y los slots
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']

    # Logs para depuración
    print("Invocación desde:", event['invocationSource'])
    print("Slots actuales:", slots)
    print("Intent actual:", intent)

    # Si estamos en el intent `Bienvenida`
    if intent == "Bienvenida":
        if event['invocationSource'] == 'DialogCodeHook':
            # Validación del slot
            validation_result = validate(slots)
            if not validation_result['isValid']:
                # Si el slot está vacío, pedir que lo complete
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "type": "ElicitSlot",
                            "slotToElicit": validation_result['violatedSlot']
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots
                        }
                    }
                }
            else:
                # Acceso al valor interpretado del slot
                user_response = slots['IniciarEncuesta']['value']['interpretedValue'].strip().lower()
                print("Respuesta interpretada:", user_response)

                if user_response in ["sí", "si"]:  # Manejar variantes de "sí"
                    # Si la respuesta es "sí", pasar al intent `Pregunta1`
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "ElicitSlot",
                                "slotToElicit": "Respuesta1"
                            },
                            "intent": {
                                "name": "Pregunta1",
                                "slots": {
                                    "Respuesta1": None
                                }
                            }
                        }
                    }
                elif user_response == "no":
                    # Si la respuesta es "no", finalizar la conversación
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "Close"
                            },
                            "intent": {
                                "name": intent,
                                "slots": slots,
                                "state": "Fulfilled"
                            }
                        },
                        "messages": [
                            {
                                "contentType": "PlainText",
                                "content": "¡Gracias por tu tiempo! Si necesitas algo más, no dudes en preguntar."
                            }
                        ]
                    }
                else:
                    # Respuesta no válida, volver a preguntar
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "ElicitSlot",
                                "slotToElicit": "IniciarEncuesta"
                            },
                            "intent": {
                                "name": intent,
                                "slots": slots
                            }
                        },
                        "messages": [
                            {
                                "contentType": "PlainText",
                                "content": "Por favor, responde con 'sí' o 'no'."
                            }
                        ]
                    }

    # Si estamos en un intent de preguntas (Pregunta1 - Pregunta15)
    else:
        current_question = int(intent.replace("Pregunta", ""))
        slot_name = f"Respuesta{current_question}"

        if event['invocationSource'] == 'DialogCodeHook':
            # Validar respuesta del slot
            if slots[slot_name] and slots[slot_name]['value']['interpretedValue'] in ["Siempre", "A veces", "Nunca"]:
                # Respuesta válida, pasar a la siguiente pregunta o finalizar
                next_question = current_question + 1
                if next_question <= 15:
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "ElicitSlot",
                                "slotToElicit": f"Respuesta{next_question}"
                            },
                            "intent": {
                                "name": f"Pregunta{next_question}",
                                "slots": {
                                    f"Respuesta{next_question}": None
                                }
                            }
                        }
                    }
                else:
                    # Si es la última pregunta, finalizar
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "Close"
                            },
                            "intent": {
                                "name": intent,
                                "slots": slots,
                                "state": "Fulfilled"
                            }
                        },
                        "messages": [
                            {
                                "contentType": "PlainText",
                                "content": "Gracias por completar la encuesta. ¡Hasta pronto!"
                            }
                        ]
                    }
            else:
                # Respuesta inválida, pedir nuevamente
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "type": "ElicitSlot",
                            "slotToElicit": slot_name
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "Por favor, responde con 'Siempre', 'A veces' o 'Nunca'."
                        }
                    ]
                }

    return response






