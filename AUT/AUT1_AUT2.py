# AUT 1 y 2 - Retiros y Consultas - VERSION FINAL SINCRONIZADA
import socket
import random
import mysql.connector
from mysql.connector import Error
from config import DATABASE, SERVER, PASSWORD, USUARIO, PUERTO_CORE_JAVA
from AUT4 import registrar_evento_aut4

class ConexionDB:
    """Conexion reutilizable para AUT 1/2 con patron Singleton básico"""
    conn = None

    @staticmethod
    def conectar():
        try:
            if ConexionDB.conn is None or not ConexionDB.conn.is_connected():
                ConexionDB.conn = mysql.connector.connect(
                    host=SERVER, 
                    port=3306, 
                    user=USUARIO,
                    password=PASSWORD, 
                    database=DATABASE
                )
            return True
        except Error as e:
            print(f"ERROR DB AUT1/2: {e}")
            return False

def procesar_retiro_consulta(trama):
    """
    Procesa AUT1 (Retiro) y AUT2 (Consulta)
    Trama esperada de C#: Tipo(1) + Tarjeta(16) + Monto(8) + PIN(4) + Cajero(4) = 33 caracteres
    """
    n_tarjeta_global = ""
    try:
        # 1. Parseo de la trama recibida del Simulador C#
        tipo = trama[0:1]                      # '1' Retiro, '2' Consulta
        n_tarjeta = trama[1:17].strip()        # 16 dígitos
        n_tarjeta_global = n_tarjeta
        monto_raw = trama[17:25]               # 8 dígitos (centavos)
        pin_raw = trama[25:29]                 # 4 dígitos
        
        # Extraer ID Cajero (posiciones 29 a 33)
        try:
            id_cajero = int(trama[29:33])
        except:
            id_cajero = 1 # Default si la trama viene incompleta

        monto_f = float(monto_raw) / 100.0
        
        print(f"DEBUG - Procesando {('RETIRO' if tipo == '1' else 'CONSULTA')} en Cajero: {id_cajero}")
        registrar_evento_aut4(n_tarjeta, id_cajero, f"SOLICITUD_{'RETIRO' if tipo == '1' else 'CONSULTA'}", monto_f)

        # 2. Conexion a Base de Datos Local (MySQL)
        if not ConexionDB.conectar():
            return {"estado": "ERROR", "mensaje": "Error de conexión con DB Autorizador"}

        cursor = ConexionDB.conn.cursor(dictionary=True)
        
        # 3. Validar existencia de Tarjeta y obtener datos de Cuenta
        query = """
            SELECT t.id_tarjeta, t.pin, t.estado as estado_tarjeta, t.id_cuenta,
                   c.saldo_disponible, c.numero_cuenta, c.estado as estado_cuenta
            FROM tarjeta t 
            JOIN cuenta c ON t.id_cuenta = c.id_cuenta 
            WHERE REPLACE(t.numero_tarjeta, '-', '') = REPLACE(%s, '-', '')
        """
        cursor.execute(query, (n_tarjeta,))
        tarjeta = cursor.fetchone()

        # 4. Validaciones de Negocio
        if not tarjeta:
            registrar_evento_aut4(n_tarjeta, id_cajero, "RECHAZADO_TARJETA_INEXISTENTE")
            return {"estado": "RECHAZADO", "mensaje": "Tarjeta no registrada"}

        if tarjeta['estado_tarjeta'] != 'ACTIVA' or tarjeta['estado_cuenta'] != 'ACTIVA':
            registrar_evento_aut4(n_tarjeta, id_cajero, "RECHAZADO_ESTADO_INACTIVO")
            return {"estado": "RECHAZADO", "mensaje": "Tarjeta o cuenta bloqueada"}

        if tarjeta['pin'] != pin_raw:
            registrar_evento_aut4(n_tarjeta, id_cajero, "RECHAZADO_PIN_ERRONEO")
            return {"estado": "RECHAZADO", "mensaje": "PIN incorrecto"}

        # Validar saldo localmente antes de ir al Core (solo para retiros)
        if tipo == "1" and monto_f > float(tarjeta['saldo_disponible']):
            registrar_evento_aut4(n_tarjeta, id_cajero, "RECHAZADO_SALDO_INSUF", monto_f)
            return {"estado": "RECHAZADO", "mensaje": "Saldo insuficiente en autorizador"}

        # 5. Comunicación con el CORE BANCARIO (Java)
        # Sincronización: Tipo(1) + Cuenta(23) + Tarjeta(18) + CodAuth(8) + Monto(8) = 58 caracteres
        cod_auth = str(random.randint(10000000, 99999999))
        n_tarjeta_limpia = n_tarjeta.replace('-', '')
        n_cuenta_db = tarjeta['numero_cuenta']
        
        trama_java = f"{tipo}{n_cuenta_db.ljust(23)}{n_tarjeta_limpia.ljust(18)}{cod_auth}{monto_raw}"

        print(f"INFO - Enviando trama al Core Java (Puerto {PUERTO_CORE_JAVA})...")
        
        resp_core = "ERROR_COMUNICACION_CORE"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_java:
                s_java.settimeout(5)
                s_java.connect(('127.0.0.1', PUERTO_CORE_JAVA))
                s_java.sendall((trama_java + "\n").encode())
                resp_core = s_java.recv(1024).decode().strip()
                print(f"INFO - Core Java respondió: {resp_core}")
        except Exception as e:
            print(f"CRITICAL - No se pudo contactar al Core Java: {e}")
            return {"estado": "ERROR", "mensaje": "Core Bancario no disponible"}

        # 6. Procesar respuesta del Core y afectar DB MySQL
        cursor = ConexionDB.conn.cursor()
        id_tipo_trans = 1 if tipo == '1' else 2 # 1: Retiro, 2: Consulta
        
        if "OK" in resp_core.upper():
            # A) Si es Retiro, rebajamos el saldo también en MySQL para mantener sincronía
            if tipo == "1":
                cursor.execute("""
                    UPDATE cuenta 
                    SET saldo_disponible = saldo_disponible - %s 
                    WHERE id_cuenta = %s
                """, (monto_f, tarjeta['id_cuenta']))
                print(f"SUCCESS - Saldo actualizado en MySQL para cuenta {n_cuenta_db}")

            # B) Registrar la transacción como APROBADA
            cursor.execute("""
                INSERT INTO autorizacion (codigo_autorizacion, id_tarjeta, id_cajero, 
                    id_tipo_transaccion, monto, estado, fecha_solicitud, respuesta) 
                VALUES (%s, %s, %s, %s, %s, 'APROBADA', NOW(), %s)
            """, (cod_auth, tarjeta['id_tarjeta'], id_cajero, id_tipo_trans, monto_f, resp_core))
            
            ConexionDB.conn.commit()
            registrar_evento_aut4(n_tarjeta, id_cajero, "TRANSACCION_EXITOSA", monto_f)

            # C) Preparar respuesta para C#
            resultado = {"estado": "APROBADO", "codigo_autorizacion": cod_auth}
            if tipo == "2":
                # Convertimos Decimal a float para que sea serializable en JSON
                resultado["saldo"] = float(tarjeta['saldo_disponible'])
            
            return resultado

        else:
            # Si el Core rechazó (ej. "SALDO_INSUFICIENTE" o "ERROR_DB")
            registrar_evento_aut4(n_tarjeta, id_cajero, f"RECHAZADO_POR_CORE_{resp_core}")
            return {"estado": "RECHAZADO", "mensaje": f"Core indica: {resp_core}"}

    except Exception as e:
        print(f"FATAL ERROR en AUT1/2: {e}")
        return {"estado": "ERROR", "mensaje": str(e)}
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()