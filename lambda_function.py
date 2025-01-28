import json

# Función para manejar mensajes de depuración
def debug_print(message, debug=False):
    """Imprime un mensaje solo si debug es True."""
    if debug:
        print(message)

# Puntos asignados a cada respuesta
POINTS = {
    "Siempre": 0,  # 'Siempre' suma 0 puntos por defecto
    "A veces": 1,  # 'A veces' suma 1 punto
    "Nunca": 2,    # 'Nunca' suma 2 puntos por defecto
    "Paso": None   # 'Paso' no afecta el puntaje (None significa que no se suma)
}

# Para estas preguntas, 'Siempre' y 'Nunca' tienen puntajes invertidos
INVERTED_QUESTIONS = [4, 5, 6, 7]

# Mapeo de nombres de intents a números de preguntas
INTENT_MAPPING = {
    "PreguntaUno": 1,
    "PreguntaDos": 2,
    "PreguntaTres": 3,
    "PreguntaCuatro": 4,
    "PreguntaCinco": 5,
    "PreguntaSeis": 6,
    "PreguntaSiete": 7,
    "PreguntaOcho": 8,
    "PreguntaNueve": 9,
    "PreguntaDiez": 10,
    "PreguntaOnce": 11,
    "PreguntaDoce": 12,
    "PreguntaTrece": 13,
    "PreguntaCatorce": 14,
    "PreguntaQuince": 15
}

# Variable para controlar el modo de depuración
DEBUG_MODE = True

# Validacion del slot `IniciarEncuesta`
def validate(slots):
    # Verifica si el slot 'IniciarEncuesta' tiene un valor valido
    if not slots['IniciarEncuesta'] or 'value' not in slots['IniciarEncuesta']:
        debug_print("El slot 'IniciarEncuesta' no tiene un valor válido o está ausente.", DEBUG_MODE)
        return {
            'isValid': False,
            'violatedSlot': 'IniciarEncuesta'
        }
    debug_print("Validación del slot 'IniciarEncuesta' completada con éxito.", DEBUG_MODE)
    return {'isValid': True}

# Variable global para puntaje acumulado
total_score = 0

# Funcion principal que maneja los eventos del bot
def lambda_handler(event, context):
    global total_score  # Utiliza una variable global para manejar el puntaje
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']

    # Logs para depuracion
    debug_print(f"Procesando intent: {intent}", DEBUG_MODE)
    debug_print(f"Puntaje acumulado antes de procesar el intent: {total_score}", DEBUG_MODE)

    # Manejo del intent `Bienvenida`
    if intent == "Bienvenida":
        total_score = 0  # Reinicia el puntaje al inicio de la encuesta
        debug_print("Reiniciando el puntaje al inicio de la encuesta.", DEBUG_MODE)
        if event['invocationSource'] == 'DialogCodeHook':
            validation_result = validate(slots)
            if not validation_result['isValid']:
                debug_print("Solicitud inválida para el slot 'IniciarEncuesta'. Solicitando nuevamente.", DEBUG_MODE)
                # Si el slot 'IniciarEncuesta' no es valido, solicita nuevamente el slot
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
                # Captura la respuesta del usuario y decide si empezar o no la encuesta
                user_response = slots['IniciarEncuesta']['value']['interpretedValue'].strip().lower()
                debug_print(f"Respuesta del usuario para 'IniciarEncuesta': {user_response}", DEBUG_MODE)
                if user_response in ["si"]:
                    debug_print("Usuario desea iniciar la encuesta. Pasando a 'PreguntaUno'.", DEBUG_MODE)
                    # Comienza la encuesta solicitando el slot de la primera pregunta
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "ElicitSlot",
                                "slotToElicit": "Respuesta1"
                            },
                            "intent": {
                                "name": "PreguntaUno",
                                "slots": {
                                    "Respuesta1": None
                                }
                            }
                        }
                    }
                elif user_response == "no":
                    debug_print("Usuario decidió no iniciar la encuesta. Cerrando conversación.", DEBUG_MODE)
                    # Cierra la conversacion si el usuario no quiere empezar la encuesta
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

    # Manejo de los intents de preguntas
    elif intent in INTENT_MAPPING:
        current_question = INTENT_MAPPING[intent]
        slot_name = f"Respuesta{current_question}"
        debug_print(f"Procesando la pregunta número {current_question}.", DEBUG_MODE)

        if event['invocationSource'] == 'DialogCodeHook':
            # Verifica si la respuesta está en los puntos definidos
            if slots[slot_name] and slots[slot_name]['value']['interpretedValue'] in POINTS:
                user_response = slots[slot_name]['value']['interpretedValue']
                score = POINTS[user_response]

                # Invierte los puntajes si la pregunta actual está en la lista de preguntas invertidas
                if current_question in INVERTED_QUESTIONS:
                    if user_response == "Siempre":
                        score = 2
                    elif user_response == "Nunca":
                        score = 0

                # Solo suma si la respuesta no es "Paso"
                if score is not None:
                    total_score += score
                debug_print(f"Respuesta válida: {user_response}. Puntaje actualizado: {total_score}", DEBUG_MODE)

                # Pasa a la siguiente pregunta
                next_question = current_question + 1
                if next_question <= 15:
                    # Solicita el slot de la siguiente pregunta
                    next_intent = [key for key, value in INTENT_MAPPING.items() if value == next_question][0]
                    debug_print(f"Pasando a la siguiente pregunta: {next_intent}.", DEBUG_MODE)
                    response = {
                        "sessionState": {
                            "dialogAction": {
                                "type": "ElicitSlot",
                                "slotToElicit": f"Respuesta{next_question}"
                            },
                            "intent": {
                                "name": next_intent,
                                "slots": {
                                    f"Respuesta{next_question}": None
                                }
                            }
                        }
                    }
                else:
                    # Cierra la encuesta si se llega al final de las preguntas
                    debug_print(f"Encuesta completada. Puntaje final: {total_score}.", DEBUG_MODE)
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
                debug_print(f"Respuesta inválida para el slot '{slot_name}'. Solicitando nuevamente.", DEBUG_MODE)
                # Maneja respuestas inválidas y solicita nuevamente el slot
                response = {
                    "sessionState": {
                        "dialogAction": {
                            "type": "ElicitSlot",
                            "slotToElicit": slot_name
                        },
                        "intent": {
                            "name": intent,
                            "slots": slots,
                            "state": "InProgress"
                        }
                    },
                    "messages": [
                        {
                            "contentType": "PlainText",
                            "content": "Por favor, responde con 'Siempre', 'A veces', 'Nunca' o 'Paso' si no quieres responder."
                        }
                    ]
                }

    return response

