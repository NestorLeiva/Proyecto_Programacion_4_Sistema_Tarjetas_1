# main.py
import os
from servidor import iniciar_servidor
from AUT4 import registrar_evento_aut4

def inicializar_sistema():
    registrar_evento_aut4("SISTEMA", 0, "INICIO_SERVIDOR")
    print(" AUT4 sinconizado")

if __name__ == "__main__":
    print("============================================================")
    print("  SISTEMA AUTORIZADOR BANCARIO")
    print("============================================================")
    
    inicializar_sistema()
    print("\nIniciando servidor AUT (puerto 5001)...")

    
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\n Servidor detenido")
        registrar_evento_aut4("SISTEMA", 0, "APAGADO_SERVIDOR")
