# TFG_ChatBot

Proyecto_TFG: Carpeta descomprimida de la exportación del bot de Amazon Lex

lambda_function.py: Función lambda del proyecto

Lo primero que tendremos que hacer es crearnos una cuenta en el entorno de AWS para ser capaces de utilizar la herramienta de Amazon Lez y AWS Lambda.
Dentro del GitHub nos interesan los dos archivos.zip, el archivo Chatbot.zip contiene toda la estructura del agente desarrollado, y el archivo lambda_function.zip, contiene la función lambda que gestiona el flujo de la conversación y eventos del agente.

Para importar el agente nos iremos a Lex, después nos iremos al apartado de Bots, iremos al botón de Acción y seleccionamos Importar.

El siguiente paso será ponerle un nombre al bot, importar nuestro archivo, Chatbot.zip, y seleccionar un rol con permisos básicos de AWS.

Una vez importado el bot, nos iremos a la sección de Intents y buscaremos y entraremos en el intent “Bienvenida”. Dentro del intent iremos a la esquina superior derecha y pulsaremos en el botón Crear cargar definitivamente el bot.

El siguiente paso será entrar en AWS Lambda y crear una función, añadiremos el nombre que queramos, seleccionaremos el lenguaje de Python 3.13 y crearemos la función.

Entramos ahora en nuestra función Lambda y cargaremos el archivo lambda_function.zip. Una vez que tenemos la función ya cargada volveremos a Amazon Lex al intent “Bienvenida” en donde nos encontrábamos anteriormente y volveremos a pulsar el botón Crear. Una vez terminado de cargar todo, pulsaremos el botón Prueba, dentro de esta sección seleccionaremos el icono de rueda, y escogeremos nuestra función Lambda y guardaremos la configuración. Con todo esto ya podremos enviarle al agente una de las frases de inicio que veremos en la sección “Ejemplos de enunciados” dentro del intent en el que nos encontramos para empezar el test.
