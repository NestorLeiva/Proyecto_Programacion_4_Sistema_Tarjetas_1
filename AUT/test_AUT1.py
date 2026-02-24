#!/usr/bin/env python3
import os
from AUT1_AUT2 import procesar_retiro_consulta

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    limpiar_pantalla()
    print("PRUEBA INTERACTIVA AUT 1 - RETIROS")
    print("=" * 60)
    print("Tarjetas prueba:")
    print("   4111-1111-1111-1111 → PIN:7887 → Saldo:₡1,460,500")
    
    while True:
        print("\nRETIR0:")
        print("-" * 40)
        
        numero_tarjeta = input("   Numero tarjeta (16 digitos): ").strip()
        monto = float(input("   Monto (ej: 55.50): "))
        pin = input("   PIN (4 digitos): ").strip()
        
        numero_tarjeta_limpia = ''.join(c for c in numero_tarjeta if c.isdigit())
        
        if len(numero_tarjeta_limpia) != 16:
            print(f"ERROR: 16 digitos requeridos")
            input("Enter...")
            continue
        
        if len(pin) != 4 or not pin.isdigit():
            print("ERROR: PIN 4 digitos numericos")
            input("Enter...")
            continue
        
        #  TRAMA CORREGIDA - PIN NO TRUNCADO
        tipo = "1"
        monto_cents = int(monto * 100)
        trama = (tipo + 
                numero_tarjeta_limpia.ljust(16) +      # 16 chars
                f"{monto_cents:08d}".ljust(8) +        # 8 chars monto
                pin.ljust(4) +                         # 4 chars PIN ✓
                " " * 26)                              # 26 padding
        
        print(f"\nTrama generada ({len(trama)} chars): {trama[:55]}...")
        print(f"DEBUG - PIN en trama: '{trama[25:29]}'")
        
        resultado = procesar_retiro_consulta(trama)
        
        print("\nRESULTADO AUT 1:")
        if resultado.get('estado') == 'APROBADO':
            print(f"   Estado: APROBADO")
            print(f"   Codigo: {resultado['codigo_autorizacion']}")
        else:
            print(f"   Estado: {resultado.get('estado')}")
            print(f"   Mensaje: {resultado.get('mensaje', 'Error')}")
        
        print("\n" + "="*60)
        if input("¿Otro retiro? (s/N): ").lower().strip() != 's':
            break
        limpiar_pantalla()

if __name__ == "__main__":
    main()
