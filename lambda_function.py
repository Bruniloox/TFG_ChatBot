import json

# Puntos asignados a cada respuesta
POINTS = {
    "Siempre": 0,
    "A veces": 1,
    "Nunca": 2,
    "Paso": None
}

# Validación del slot `IniciarEncuesta`
def validate(slots):
    if not slots['IniciarEncuesta'] or 'value' not in slots['IniciarEncuesta']:
        return {
            'isValid': False,
            'violatedSlot': 'IniciarEncuesta'
        }
    return {'isValid': True}

# Variable global para puntaje acumulado
total_score = 0

def lambda_handler(event, context):
    global total_score  # Utilizamos una variable global para manejar el puntaje
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']

    # Logs para depuración
    print("Intent actual:", intent)
    print("Puntaje acumulado:", total_score)

    # Si estamos en el intent `Bienvenida`
    if intent == "Bienvenida":
        total_score = 0  # Reinicia el puntaje al inicio
        if event['invocationSource'] == 'DialogCodeHook':
            validation_result = validate(slots)
            if not validation_result['isValid']:
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
                user_response = slots['IniciarEncuesta']['value']['interpretedValue'].strip().lower()
                if user_response in ["si"]:
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

    # Si estamos en un intent de preguntas (Pregunta1 - Pregunta15)
    elif "Pregunta" in intent:
        current_question = int(intent.replace("Pregunta", ""))
        slot_name = f"Respuesta{current_question}"

        if event['invocationSource'] == 'DialogCodeHook':
            if slots[slot_name] and slots[slot_name]['value']['interpretedValue'] in POINTS:
                user_response = slots[slot_name]['value']['interpretedValue']
                score = POINTS[user_response]
                print("Respuesta lex", user_response)
                
                # Solo suma si la respuesta no es "Paso"
                if score is not None:
                    total_score += score
                print("Puntaje actual:", total_score)

                next_question = current_question + 1
                print("Siguiente pregunta:", next_question)
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
                    # Cambia la lógica aquí para manejar el intent final
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
                                "content": f"Gracias por completar la encuesta. Tu puntaje total es: {total_score}. ¡Hasta pronto!"
                            }
                        ]
                    }
            else:
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