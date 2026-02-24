#!/usr/bin/env python3
"""
PRUEBA AUT 3 - Cambio PIN interactivo
Tarjetas validas:
4111-1111-1111-1111 → PIN actual: 7887
4222-2222-2222-2222 → PIN actual: 5678
"""

import os
from AUT3 import procesar_cambio_pin

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    limpiar_pantalla()
    print("PRUEBA INTERACTIVA AUT 3 - CAMBIO PIN")
    print("=" * 60)
    print("Tarjetas prueba:")
    print("   4111-1111-1111-1111 → PIN actual: 7887")
    print("   4222-2222-2222-2222 → PIN actual: 5678")
    print("   5111-1111-1111-1111 → PIN actual: 2468")
    print("   5333-3333-3333-3333 → PIN actual: 2580")
    
    while True:
        print("\nCAMBIAR PIN:")
        print("-" * 40)
        
        numero_tarjeta = input("   Numero tarjeta (16 digitos): ").strip()
        pin_actual = input("   PIN actual (4 digitos): ").strip()
        pin_nuevo = input("   Nuevo PIN (4 digitos): ").strip()
        
        numero_tarjeta_limpia = ''.join(c for c in numero_tarjeta if c.isdigit())
        
        if len(numero_tarjeta_limpia) != 16:
            print("ERROR: Debe ser 16 digitos")
            input("Enter...")
            continue
        
        if len(pin_actual) != 4 or not pin_actual.isdigit():
            print("ERROR: PIN actual debe ser 4 digitos")
            input("Enter...")
            continue
        
        if len(pin_nuevo) != 4 or not pin_nuevo.isdigit():
            print("ERROR: Nuevo PIN debe ser 4 digitos")
            input("Enter...")
            continue
        
        # Datos para AUT3
        datos = {
            "numero_tarjeta": numero_tarjeta,
            "id_cajero": 1,
            "pin_actual": pin_actual,
            "pin_nuevo": pin_nuevo
        }
        
        print(f"\nProcesando cambio PIN...")
        resultado = procesar_cambio_pin(datos)
        
        print("\nRESULTADO AUT 3:")
        if resultado.get('estado') == 'OK':
            print(f"   Estado: OK")
            print(f"   Mensaje: {resultado['mensaje']}")
            print(f"   Codigo: {resultado['codigo_autorizacion']}")
        else:
            print(f"   Estado: {resultado.get('estado')}")
            print(f"   Mensaje: {resultado.get('mensaje', 'Error')}")
        
        print("\n" + "="*60)
        if input("¿Otro cambio PIN? (s/N): ").lower().strip() != 's':
            break
        limpiar_pantalla()

if __name__ == "__main__":
    main()
