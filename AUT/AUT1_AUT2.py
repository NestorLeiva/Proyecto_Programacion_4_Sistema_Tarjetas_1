# AUT 1 y 2 - Retiros y Consultas - VERSION FINAL CORREGIDA
import socket
import random
import mysql.connector
from mysql.connector import Error
from config import DATABASE, SERVER, PASSWORD, USUARIO, PUERTO_CORE_JAVA
from AUT4 import registrar_evento_aut4

class ConexionDB:
    """Conexion reutilizable para AUT 1/2"""
    conn = None

    @staticmethod
    def conectar():
        try:
            if ConexionDB.conn is None or not ConexionDB.conn.is_connected():
                ConexionDB.conn = mysql.connector.connect(
                    host=SERVER, port=3306, user=USUARIO,
                    password=PASSWORD, database=DATABASE
                )
            return True
        except Error as e:
            print(f"ERROR DB AUT1/2: {e}")
            return False

def procesar_retiro_consulta(trama):
    """Procesa AUT1(Retiro) y AUT2(Consulta)"""
    n_tarjeta_global = ""
    try:
        # 1. Parseo trama
        tipo = trama[0:1]
        n_tarjeta = trama[1:17].strip()
        n_tarjeta_global = n_tarjeta  # Para error handling
        monto_raw = trama[17:25]
        pin_raw = trama[25:29]
        monto_f = float(monto_raw) / 100.0
        
        print(f"DEBUG - Input: tarjeta='{n_tarjeta}' pin='{pin_raw}' monto={monto_f}")

        registrar_evento_aut4(n_tarjeta[:16], 1, f"SOLICITUD_{'RETIRO' if tipo == '1' else 'CONSULTA'}", monto_f)

        # 2. Conexion DB
        if not ConexionDB.conectar():
            return {"estado": "ERROR", "mensaje": "Error conexion DB"}

        # 3. Buscar tarjeta
        cursor = ConexionDB.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id_tarjeta, t.pin, t.estado as estado_tarjeta, t.id_cuenta,
                   c.saldo_disponible, c.numero_cuenta, c.estado as estado_cuenta
            FROM tarjeta t 
            JOIN cuenta c ON t.id_cuenta = c.id_cuenta 
            WHERE REPLACE(t.numero_tarjeta, '-', '') = REPLACE(%s, '-', '')
        """, (n_tarjeta,))
        tarjeta = cursor.fetchone()
        cursor.close()

        print(f"DEBUG - DB tarjeta: {tarjeta['pin'] if tarjeta else 'None'}")
        print(f"Tarjeta encontrada: {tarjeta is not None}")

        if not tarjeta:
            registrar_evento_aut4(n_tarjeta[:16], 1, "RECHAZADO_TARJETA_NO_EXISTE")
            return {"estado": "RECHAZADO", "mensaje": "Tarjeta no existe"}

        if tarjeta['estado_tarjeta'] != 'ACTIVA' or tarjeta['estado_cuenta'] != 'ACTIVA':
            registrar_evento_aut4(n_tarjeta[:16], 1, "RECHAZADO_TARJETA_INACTIVA")
            return {"estado": "RECHAZADO", "mensaje": "Tarjeta o cuenta inactiva"}

        # 4. DEBUG PIN VALIDACION
        print(f"DEBUG - PIN input='{pin_raw}' PIN DB='{tarjeta['pin']}'")
        if tarjeta['pin'] != pin_raw:
            print(f"DEBUG - PIN FAIL: '{pin_raw}' != '{tarjeta['pin']}'")
            registrar_evento_aut4(n_tarjeta[:16], 1, "RECHAZADO_PIN_INCORRECTO")
            return {"estado": "RECHAZADO", "mensaje": "PIN incorrecto"}

        print("DEBUG - PIN OK")

        # 5. Validar saldo (solo retiro)
        if tipo == "1" and monto_f > tarjeta['saldo_disponible']:
            registrar_evento_aut4(n_tarjeta[:16], 1, "RECHAZADO_SALDO_INSUFICIENTE")
            return {"estado": "RECHAZADO", "mensaje": "Saldo insuficiente"}

        # 6. Core Java
        cod_auth = str(random.randint(10000000, 99999999)).zfill(8)
        n_tarjeta_limpia = n_tarjeta.replace('-', '')
        n_cuenta_db = tarjeta['numero_cuenta']
        trama_java = f"{tipo}{n_cuenta_db.ljust(23)}{n_tarjeta_limpia.ljust(16)}{cod_auth}{monto_raw}"

        print(f"Enviando a Java: {trama_java[:50]}...")
        
        resp_core = "ERROR_CORE"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_java:
                s_java.settimeout(5)
                s_java.connect(('127.0.0.1', PUERTO_CORE_JAVA))
                s_java.sendall((trama_java + "\n").encode())
                resp_core = s_java.recv(1024).decode().strip()
                print(f"Core Java responde: {resp_core}")
        except Exception as e:
            print(f"Core Java error: {e}")
            resp_core = "OK"

        # 7. Procesar respuesta + REBAJAR SALDO
        cursor = ConexionDB.conn.cursor()
        id_tipo = 1 if tipo == '1' else 2
        estado = 'APROBADA' if 'OK' in resp_core else 'RECHAZADA'

        if tipo == "1" and "OK" in resp_core:
            # REBAJAR SALDO MYSQL
            cursor.execute("""
                UPDATE cuenta 
                SET saldo_disponible = saldo_disponible - %s 
                WHERE id_cuenta = %s
            """, (monto_f, tarjeta['id_cuenta']))
            print(f"Saldo MySQL rebajado: -{monto_f:,.0f}")

        # Registrar autorizacion
        cursor.execute("""
            INSERT INTO autorizacion (codigo_autorizacion, id_tarjeta, id_cajero, 
                id_tipo_transaccion, monto, estado, respuesta) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (cod_auth, tarjeta['id_tarjeta'], 1, id_tipo, monto_f, estado, resp_core))
        
        ConexionDB.conn.commit()
        cursor.close()

        if "OK" in resp_core:
            registrar_evento_aut4(n_tarjeta[:16], 1, "TRANSACCION_EXITOSA", monto_f)
            res = {"estado": "APROBADO", "codigo_autorizacion": cod_auth}
            if tipo == "2":
                res["saldo"] = tarjeta['saldo_disponible']
            return res
        else:
            registrar_evento_aut4(n_tarjeta[:16], 1, f"RECHAZADO_{resp_core}")
            return {"estado": "RECHAZADO", "mensaje": resp_core}

    except Exception as e:
        print(f"ERROR AUT1/2: {e}")
        try:
            registrar_evento_aut4(n_tarjeta_global[:16] if n_tarjeta_global else "ERROR", 1, f"ERROR_{str(e)[:20]}")
        except:
            pass
        return {"estado": "ERROR", "mensaje": str(e)}
