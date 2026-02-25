import socket
import json
# Importamos la función centralizada desde tu archivo
from AUT1_AUT2 import procesar_retiro_consulta
from AUT3 import procesar_cambio_pin
from AUT5 import procesar_confirmacion_aut5


def iniciar_servidor():
    puerto_escucha = 5001
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', puerto_escucha))
    server.listen(5)

    print(f"====================================================")
    print(f"  SERVIDOR AUTORIZADOR INTEGRADO ACTIVO")
    print(f"   Puerto Escucha (C#): {puerto_escucha}")
    print(f"====================================================")

    while True:
        client, addr = server.accept()
        try:
            # Recibimos la trama del simulador C#
            data = client.recv(4096).decode('utf-8').strip()
            if not data:
                continue

            # 1. Si los datos vienen en formato JSON (AUT3 o AUT5)
            if data.startswith('{'):
                datos_json = json.loads(data)
                tipo = datos_json.get('tipo', '')

                if tipo == 'cambio_pin':
                    respuesta = procesar_cambio_pin(datos_json)
                elif 'cod_auth' in datos_json:  # Flujo de confirmación AUT5
                    respuesta = procesar_confirmacion_aut5(data)
                else:
                    respuesta = {"estado": "ERROR",
                                 "mensaje": "Formato JSON no reconocido"}

            # 2. Si es trama de texto fija (AUT1 o AUT2)
            else:
                # Simplemente pasamos la trama completa a tu función en AUT1_AUT2.py
                # que ya se encarga de parsear [0:1], [1:17], etc.
                respuesta = procesar_retiro_consulta(data)

            # Enviamos la respuesta de vuelta al simulador C#
            client.send(json.dumps(respuesta).encode('utf-8'))

        except Exception as e:
            print(f"Error procesando cliente: {e}")
            error_msg = {"estado": "ERROR", "mensaje": str(e)}
            client.send(json.dumps(error_msg).encode('utf-8'))
        finally:
            client.close()
