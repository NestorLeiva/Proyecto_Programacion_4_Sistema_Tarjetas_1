#!/usr/bin/env python3
"""
PRUEBA INTERACTIVA AUT 4 - BITACORA ASINCRONA
Verifica que todos los eventos se registren correctamente
"""

import os
import time
from AUT1_AUT2 import procesar_retiro_consulta
from AUT3 import procesar_cambio_pin
from AUT4 import registrar_evento_aut4
from config import RUTA_BITACORA

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_bitacora_ultimas_lineas(n=10):
    """Muestra últimas N líneas del archivo bitacora"""
    try:
        with open(RUTA_BITACORA, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            print("\n=== ÚLTIMAS LÍNEAS BITÁCORA ===")
            for linea in lineas[-n:]:
                print(linea.strip())
    except FileNotFoundError:
        print("Archivo bitacora no existe aún")

def main():
    limpiar_pantalla()
    print("PRUEBA INTERACTIVA AUT 4 - BITACORA ASINCRONA")
    print("=" * 60)
    print("Tarjetas prueba:")
    print("   4111-1111-1111-1111 → PIN:1010")
    print("   4222-2222-2222-2222 → PIN:5678")
    print("\nBitacora: ", RUTA_BITACORA)
    
    while True:
        print("\n=== MENÚ AUT4 ===")
        print("1. Probar AUT1 (Retiro) → Eventos retiro")
        print("2. Probar AUT3 (Cambio PIN) → Eventos cambio PIN")
        print("3. Registrar evento directo AUT4")
        print("4. Ver bitacora (últimas 15 líneas)")
        print("5. Limpiar bitacora")
        print("0. Salir")
        
        opcion = input("\nOpción (0-5): ").strip()
        
        if opcion == "1":
            # Prueba AUT1 - Retiro exitoso
            numero_tarjeta = "4111111111111111"
            pin = "1010"
            monto = 100.50
            
            trama = (
                "1" + numero_tarjeta.ljust(16) + 
                f"{int(monto*100):08d}".ljust(8) + 
                pin.ljust(4) + " " * 26
            )
            
            print(f"\n Probando AUT1 retiro ₡{monto}")
            resultado = procesar_retiro_consulta(trama)
            print(f"Resultado AUT1: {resultado}")
            time.sleep(1)  # Esperar escritura asíncrona
            
        elif opcion == "2":
            # Prueba AUT3 - Cambio PIN
            datos = {
                "numero_tarjeta": "4111-1111-1111-1111",
                "id_cajero": 1,
                "pin_actual": "1010",
                "pin_nuevo": "2020"
            }
            
            print("\n Probando AUT3 cambio PIN")
            resultado = procesar_cambio_pin(datos)
            print(f"Resultado AUT3: {resultado}")
            time.sleep(1)
            
        elif opcion == "3":
            # Evento directo AUT4
            tarjeta = input("Tarjeta (16 dig): ").strip()[:16]
            cajero = input("Cajero (1-9): ").strip() or "1"
            evento = input("Tipo evento: ").strip() or "PRUEBA_DIRECTA"
            monto = input("Monto (opcional): ").strip()
            monto = float(monto) if monto.replace('.','').isdigit() else None
            
            print(f"\n Registrando evento directo...")
            registrar_evento_aut4(tarjeta, int(cajero), evento, monto)
            print("Evento en cola → Revisa bitacora en 2 seg")
            time.sleep(2)
            
        elif opcion == "4":
            mostrar_bitacora_ultimas_lineas(15)
            input("\nEnter para continuar...")
            
        elif opcion == "5":
            # Limpiar bitacora
            try:
                open(RUTA_BITACORA, 'w').close()
                print(f" Bitacora limpiada: {RUTA_BITACORA}")
            except:
                print("No se pudo limpiar bitacora")
                
        elif opcion == "0":
            print("\n Fin prueba AUT4")
            break
            
        else:
            print("Opción inválida")
        
        input("\nEnter para continuar...")

if __name__ == "__main__":
    main()
