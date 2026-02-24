# AUT 4 - Bitacora asincrona - Compatible con nueva estructura
import json
import threading
from queue import Queue
from datetime import datetime
from config import RUTA_BITACORA

cola_bitacora = Queue()

def enmascarar_tarjeta(numero_tarjeta: str) -> str:
    """Enmascara numero_tarjeta para logs (VARCHAR(20))"""
    if isinstance(numero_tarjeta, bytes):
        numero_tarjeta = numero_tarjeta.decode('utf-8', errors='ignore')
    
    digitos = ''.join(c for c in numero_tarjeta if c.isdigit())
    if len(digitos) >= 16:
        return f"{digitos[:4]} {digitos[4:6]}** **** {digitos[-4:]}"
    return "**** **** **** ****"

def worker_bitacora():
    """Worker que escribe en archivo desde cola"""
    while True:
        linea = cola_bitacora.get()
        try:
            with open(RUTA_BITACORA, "a", encoding="utf-8") as f:
                f.write(linea + "\n")
        finally:
            cola_bitacora.task_done()

def registrar_evento_aut4(tarjeta, cajero, tipo, monto=None):
    """Registra en bitacora (tabla auditoria se llena por triggers)"""
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    registro = {
        "tarjeta": enmascarar_tarjeta(tarjeta),
        "cajero": cajero,
        "tipo": tipo,
        "monto": f"{monto:.2f}" if monto else "0.00"
    }
    linea = f"{fecha}: {json.dumps(registro)}"
    cola_bitacora.put(linea)
