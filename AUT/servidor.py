import socket
import json
import threading
from AUT1_AUT2 import procesar_retiro_consulta
from AUT3 import procesar_cambio_pin
from AUT4 import worker_bitacora
from config import PUERTO_SERVIDOR
from AUT4 import registrar_evento_aut4  # ← AUT4 IMPORT - SI ES NECESARIO
from AUT5 import procesar_confirmacion_aut5


def manejar_cliente(conn, addr):
    try:
        data = conn.recv(4096).decode('utf-8').strip()
        if not data: 
            return
        
        # Si la trama es un JSON
        if data.startswith('{'): 
            payload = json.loads(data)
            
            # REGLA: Si trae 'cod_auth' es la confirmación (AUT5)
            if "cod_auth" in payload:
                respuesta = procesar_confirmacion_aut5(data)
            # De lo contrario, es cambio de PIN (AUT3)
            else:
                respuesta = procesar_cambio_pin(payload)
        
        # Si no es JSON, es una trama de texto (AUT1/2)
        else: 
            respuesta = procesar_retiro_consulta(data)
        
        conn.sendall(json.dumps(respuesta).encode('utf-8'))
        
    except Exception as e:
        print(f"Error manejando cliente: {e}")
    finally:
        conn.close()


def iniciar_servidor():
    threading.Thread(target=worker_bitacora, daemon=True).start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', PUERTO_SERVIDOR))
    server.listen(10)

    print("====================================================")
    print("  SERVIDOR AUTORIZADOR INTEGRADO ACTIVO")
    print(f"   Puerto Escucha (C#): {PUERTO_SERVIDOR}")
    print(f"   Puerto Core (Java): 5000")
    print("====================================================")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=manejar_cliente, args=(
            conn, addr), daemon=True).start()
