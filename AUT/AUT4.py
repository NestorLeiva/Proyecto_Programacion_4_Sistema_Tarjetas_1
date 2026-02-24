import threading
import queue
import json
import os
from datetime import datetime

# Configuración de la ruta (ajusta si es necesario)
RUTA_BITACORA = "bitacora_4.txt"

# 1. La Cola para manejar las peticiones de forma ordenada
cola_bitacora = queue.Queue()

def enmascarar_tarjeta(tarjeta):
    """Enmascara la tarjeta al formato: 1345 45** **** 2587"""
    t = str(tarjeta).replace("-", "").replace(" ", "")
    if len(t) >= 16:
        # Formato específico según criterio 2.b
        return f"{t[0:4]} {t[4:6]}** **** {t[12:16]}"
    return t

def worker_bitacora():
    """
    Función que procesa la cola en segundo plano.
    Este es el nombre que tu servidor.py está intentando importar.
    """
    while True:
        # Obtiene el evento de la cola
        evento = cola_bitacora.get()
        if evento is None:
            break
        
        try:
            fecha_str = datetime.now().strftime("%d/%m/%Y")
            hora_str = datetime.now().strftime("%H:%M:%S")
            
            # Estructura JSON según criterio 3
            datos_json = {
                "tarjeta": enmascarar_tarjeta(evento.get('tarjeta')),
                "cajero": evento.get('cajero'),
                "cliente": evento.get('cliente'),
                "tipo": evento.get('tipo'),
                "monto": f"{float(evento.get('monto', 0)):.2f}" if evento.get('monto') is not None else "0.00"
            }
            
            # Formato de línea: Fecha: {JSON}
            linea = f"{fecha_str} {hora_str}: {json.dumps(datos_json, ensure_ascii=False)}\n"
            
            with open(RUTA_BITACORA, 'a', encoding='utf-8') as f:
                f.write(linea)
                
        except Exception as e:
            print(f"Error en hilo de bitácora: {e}")
        finally:
            cola_bitacora.task_done()

# 2. Iniciar el hilo de forma automática al importar el módulo
hilo = threading.Thread(target=worker_bitacora, daemon=True)
hilo.start()

def registrar_evento_aut4(tarjeta, cajero, tipo, monto=None, cliente="112340456"):
    """Función para encolar registros desde cualquier parte del sistema"""
    evento = {
        "tarjeta": tarjeta,
        "cajero": cajero,
        "cliente": cliente,
        "tipo": tipo,
        "monto": monto
    }
    cola_bitacora.put(evento)