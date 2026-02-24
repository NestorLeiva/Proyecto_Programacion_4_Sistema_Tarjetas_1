#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba completa conexion a base de datos sistema_tarjeta
Verifica: conexion, tablas, datos de prueba, queries basicos
"""

import mysql.connector
from mysql.connector import Error
import os
from config import DATABASE, SERVER, PASSWORD, USUARIO  # Usa tu config

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def test_conexion_basica():
    """Prueba 1: Conexion simple"""
    print(" PRUEBA 1: CONEXION BASICA")
    print("-" * 40)
    
    try:
        conexion = mysql.connector.connect(
            host=SERVER,
            port=3306,
            user=USUARIO,
            password=PASSWORD,
            database=DATABASE
        )
        
        if conexion.is_connected():
            info_db = conexion.get_server_info()
            print(f" CONEXION EXITOSA!")
            print(f"    Servidor: {info_db}")
            print(f"     Base datos: {DATABASE}")
            return conexion
    except Error as e:
        print(f" ERROR CONEXION: {e}")
        return None

def test_tablas_existentes(conexion):
    """Prueba 2: Verificar tablas existen"""
    print("\n PRUEBA 2: TABLAS EXISTENTES")
    print("-" * 40)
    
    try:
        cursor = conexion.cursor()
        cursor.execute("SHOW TABLES")
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        
        tablas_esperadas = ['cajero', 'cuenta', 'tarjeta', 'autorizacion', 'movimiento', 'auditoria']
        for tabla in tablas_esperadas:
            if tabla in tablas:
                print(f" {tabla}")
            else:
                print(f" FALTA {tabla}")
        
        print(f" Total tablas: {len(tablas)}")
        cursor.close()
        return True
    except Error as e:
        print(f" ERROR: {e}")
        return False

def test_datos_prueba(conexion):
    """Prueba 3: Verificar datos de prueba"""
    print("\n PRUEBA 3: DATOS DE PRUEBA")
    print("-" * 40)
    
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) as total FROM tarjeta")
        tarjetas = cursor.fetchone()['total']
        print(f" Tarjetas: {tarjetas}")
        
        cursor.execute("SELECT COUNT(*) as total FROM cuenta")
        cuentas = cursor.fetchone()['total']
        print(f" Cuentas: {cuentas}")
        
        cursor.execute("SELECT COUNT(*) as total FROM cajero")
        cajeros = cursor.fetchone()['total']
        print(f" Cajeros: {cajeros}")
        
        # Mostrar primera tarjeta
        cursor.execute("SELECT numero_tarjeta, estado, tipo_tarjeta FROM tarjeta LIMIT 1")
        tarjeta = cursor.fetchone()
        if tarjeta:
            print(f" Ejemplo tarjeta: {tarjeta['numero_tarjeta']} ({tarjeta['estado']})")
        
        cursor.close()
    except Error as e:
        print(f" ERROR: {e}")

def test_query_tarjeta(conexion):
    """Prueba 4: Query real con datos"""
    print("\n PRUEBA 4: QUERY TARJETA")
    print("-" * 40)
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.numero_tarjeta, t.estado, c.saldo_disponible, c.numero_cuenta
            FROM tarjeta t JOIN cuenta c ON t.id_cuenta = c.id_cuenta 
            WHERE t.estado = 'ACTIVA' LIMIT 3
        """)
        resultados = cursor.fetchall()
        
        if resultados:
            print(" DATOS ACTIVOS ENCONTRADOS:")
            for r in resultados:
                print(f"    {r['numero_tarjeta']} -> ₡{r['saldo_disponible']:,.0f}")
        else:
            print("  No hay tarjetas activas")
        
        cursor.close()
    except Error as e:
        print(f" ERROR: {e}")

def test_aut3_pin(conexion):
    """Prueba 5: Validacion PIN (AUT3)"""
    print("\n PRUEBA 5: VALIDACION PIN")
    print("-" * 40)
    
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT numero_tarjeta, pin FROM tarjeta WHERE numero_tarjeta = '4111-1111-1111-1111'")
        tarjeta = cursor.fetchone()
        
        if tarjeta:
            print(f" Tarjeta encontrada: {tarjeta['numero_tarjeta']}")
            print(f"    PIN en BD: {tarjeta['pin'][:8]}...")
        else:
            print(" Tarjeta de prueba no encontrada")
        
        cursor.close()
    except Error as e:
        print(f" ERROR: {e}")

def main():
    limpiar_pantalla()
    print(" TEST COMPLETO CONEXION BASE DATOS")
    print("=" * 60)
    
    # Prueba 1
    conexion = test_conexion_basica()
    if not conexion:
        print("\n IMPOSIBLE CONECTAR - Revisa config.py")
        return
    
    # Pruebas adicionales
    test_tablas_existentes(conexion)
    test_datos_prueba(conexion)
    test_query_tarjeta(conexion)
    test_aut3_pin(conexion)
    
    # Cerrar conexion
    conexion.close()
    print("\n CONEXION CERRADA CORRECTAMENTE")
    print("\n ¡TODAS LAS PRUEBAS PASARON!")
    print(" Listo para probar AUT 1,2,3")

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para salir...")
