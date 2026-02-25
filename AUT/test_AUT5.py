import socket
import json
from seguridad import cifrar_dato # Usamos tu función para preparar los datos
from config import PUERTO_SERVIDOR

def simular_cajero_confirmacion():
    # 1. Datos de prueba (Deben existir en tu base de datos)
    # Asegúrate de que esta tarjeta tenga una autorización previa pendiente
    tarjeta_real = "4111-1111-1111-1111"
    vencimiento_real = "2027-12-01"
    cvv_real = "123"
    cod_auth_previo = "AUTH2026" # Cambia esto por uno generado por AUT1
    monto = 5000.00
    id_cajero = 1

    print("--- SIMULADOR DE CAJERO (AUT5) ---")
    print(f"Preparando confirmación para tarjeta: {tarjeta_real}")

    # 2. Ciframos los datos sensibles como lo haría el cajero
    # Tu función cifrar_dato ya devuelve un string en HEX
    tarjeta_hex = cifrar_dato(tarjeta_real)
    vencimiento_hex = cifrar_dato(vencimiento_real)
    cvv_hex = cifrar_dato(cvv_real)

    # 3. Construimos el JSON según el Criterio de Aceptación 1
    trama_confirmacion = {
        "cod_auth": cod_auth_previo,
        "tarjeta": tarjeta_hex,
        "vencimiento": vencimiento_hex,
        "cvv": cvv_hex,
        "id_cajero": id_cajero,
        "tipo": "confirmacion",
        "monto": monto
    }

    # 4. Enviamos al servidor
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', PUERTO_SERVIDOR))
            
            # Convertimos dict a string JSON y enviamos
            json_payload = json.dumps(trama_confirmacion)
            print(f"\nEnviando JSON cifrado...")
            s.sendall(json_payload.encode('utf-8'))
            
            # Recibimos respuesta del Autorizador
            respuesta = s.recv(4096).decode('utf-8')
            print(f"\nRespuesta del Servidor: {respuesta}")

    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    simular_cajero_confirmacion()