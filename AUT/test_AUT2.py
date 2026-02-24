#!/usr/bin/env python3
"""
PRUEBA INTERACTIVA AUT 2 - CONSULTA SALDO (con Core Java)
Tarjeta: 4111-1111-1111-1111 | PIN: 7887 | Cuenta: CC001234567890123456789
"""

import os
from AUT1_AUT2 import procesar_retiro_consulta

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    limpiar_pantalla()
    print(" AUT 2 - CONSULTA SALDO (Core Java + SQL Server)")
    print("=" * 65)
    print(" Tarjetas prueba:")
    print("   4111-1111-1111-1111 → PIN:7887 → Cuenta:CC001234567890123456789")
    print()
    
    while True:
        print(" DATOS CONSULTA:")
        print("-" * 40)
        
        numero_tarjeta = input("   Tarjeta (16 digitos): ").strip()
        pin = input("   PIN (4 digitos): ").strip()
        
        # Limpiar tarjeta
        numero_tarjeta_limpia = ''.join(c for c in numero_tarjeta if c.isdigit())
        
        if len(numero_tarjeta_limpia) != 16:
            print(f" ERROR: 16 digitos requeridos (tiene {len(numero_tarjeta_limpia)})")
            input("Presiona Enter...")
            continue
        
        if len(pin) != 4 or not pin.isdigit():
            print(" ERROR: PIN 4 digitos numericos")
            input("Presiona Enter...")
            continue
        
        # Trama AUT2: tipo(2) + tarjeta(16) + monto(00000000) + pin(4) + padding(26)
        tipo = "2"
        trama = (tipo + numero_tarjeta_limpia.ljust(16) + 
                "00000000" + pin + " "*26)
        
        print(f"\n CONSULTANDO SALDO...")
        print(f"    Tarjeta: {numero_tarjeta_limpia}")
        print(f"    PIN: {'*' * len(pin)}")
        print(f"    Trama: {trama[:30]}...")
        
        resultado = procesar_retiro_consulta(trama)
        
        print("\n RESULTADO AUT 2:")
        if resultado.get('estado') == 'APROBADO':
            print(f"    SALDO: ₡{resultado.get('saldo', 0):,.0f}")
            print(f"    Codigo: {resultado['codigo_autorizacion']}")
            print("    Core Java procesado correctamente")
        else:
            print(f"    Error: {resultado.get('mensaje', 'Desconocido')}")
        
        print("\n" + "="*65)
        continuar = input("¿Otra consulta? (s/N): ").lower().strip()
        if continuar != 's':
            break
        limpiar_pantalla()

if __name__ == "__main__":
    main()
