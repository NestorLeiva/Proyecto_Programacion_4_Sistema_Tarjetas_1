import json
import socket
import mysql.connector
from config import DATABASE, SERVER, PASSWORD, USUARIO, PUERTO_CORE_JAVA
from seguridad import descifrar_dato, cifrar_dato
from AUT4 import registrar_evento_aut4

def procesar_confirmacion_aut5(trama_json):
    conn = None
    try:
        datos = json.loads(trama_json)

        # 1. Validar datos obligatorios
        campos = ['cod_auth', 'tarjeta', 'vencimiento', 'cvv', 'id_cajero', 'monto']
        if not all(k in datos for k in campos):
            return {"estado": "ERROR", "mensaje": "Faltan datos obligatorios"}

        # 2. Descifrar datos
        n_tarjeta = descifrar_dato(datos['tarjeta'])
        f_vencimiento = descifrar_dato(datos['vencimiento'])
        cvv = descifrar_dato(datos['cvv'])

        if not n_tarjeta or not f_vencimiento or not cvv:
            return {"estado": "ERROR", "mensaje": "Fallo en descifrado de datos sensibles"}

        # 3. Conexión a DB MySQL (Autorizador)
        conn = mysql.connector.connect(
            host=SERVER, user=USUARIO, password=PASSWORD, database=DATABASE
        )
        cursor = conn.cursor(dictionary=True)

        # 4. Validaciones contra DB
        query = """
            SELECT t.id_tarjeta, t.id_cuenta, t.estado as t_estado, t.fecha_vencimiento, t.cvv,
                   c.tipo_cuenta, c.numero_cuenta, c.estado as c_estado
            FROM tarjeta t
            JOIN cuenta c ON t.id_cuenta = c.id_cuenta
            WHERE REPLACE(t.numero_tarjeta, '-', '') = REPLACE(%s, '-', '')
        """
        cursor.execute(query, (n_tarjeta,))
        tarjeta_db = cursor.fetchone()

        if not tarjeta_db or tarjeta_db['t_estado'] != 'ACTIVA':
            return {"estado": "ERROR", "mensaje": "Tarjeta no existe o inactiva"}

        # Comparar datos descifrados con DB
        if str(tarjeta_db['fecha_vencimiento']) != f_vencimiento or tarjeta_db['cvv'] != cvv:
            return {"estado": "ERROR", "mensaje": "Validación de seguridad fallida"}

        # Validar Código de Autorización previo
        cursor.execute("SELECT * FROM autorizacion WHERE codigo_autorizacion = %s AND id_tarjeta = %s",
                       (datos['cod_auth'], tarjeta_db['id_tarjeta']))
        if not cursor.fetchone():
            return {"estado": "ERROR", "mensaje": "Código de autorización no corresponde"}

        # 5. Lógica de Negocio (Débito vs Crédito)
        monto = float(datos['monto'])

        if tarjeta_db['tipo_cuenta'] == 'DEBITO':
            # --- CONSTRUCCIÓN DE TRAMA SINCRONIZADA CON COREBANCARIO.JAVA ---
            # Tipo(1) + Cuenta(23) + Tarjeta(18) + CodAuth(8) + Monto(8) = 58 caracteres
            num_tarjeta_limpia = n_tarjeta.replace("-", "")[:18]
            
            trama_core = (
                "C" + 
                tarjeta_db['numero_cuenta'].ljust(23) + 
                num_tarjeta_limpia.ljust(18) + 
                datos['cod_auth'].ljust(8) + 
                f"{int(monto * 100):08d}"
            )

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_java:
                    s_java.settimeout(5)
                    s_java.connect(('127.0.0.1', PUERTO_CORE_JAVA))
                    s_java.sendall((trama_core + "\n").encode())
                    resp_core = s_java.recv(1024).decode().strip()

                print(f"DEBUG: Trama enviada -> {trama_core}")
                print(f"DEBUG: El Core Java respondió -> '{resp_core}'")

                if "OK" in resp_core.upper():
                    registrar_evento_aut4(n_tarjeta, datos['id_cajero'], "CONFIRMACION_RETIRO", monto)
                    return {"estado": "OK", "codigo_autorizacion": datos['cod_auth']}
                else:
                    return {"estado": "ERROR", "mensaje": f"Core respondio: {resp_core}"}
            
            except Exception as e:
                print(f"Error de conexión con Java: {e}")
                return {"estado": "ERROR", "mensaje": "Core no disponible"}

        else:  # CRÉDITO
            cursor.execute("""
                INSERT INTO movimiento (id_tarjeta, codigo_autorizacion, tipo_movimiento, monto, estado)
                VALUES (%s, %s, 'RETIRO_CONFIRMADO', %s, 'PENDIENTE')
            """, (tarjeta_db['id_tarjeta'], datos['cod_auth'], monto))
            conn.commit()
            
            registrar_evento_aut4(n_tarjeta, datos['id_cajero'], "CONFIRMACION_CREDITO_PENDIENTE", monto)
            return {"estado": "OK", "codigo_autorizacion": datos['cod_auth']}

    except Exception as e:
        return {"estado": "ERROR", "mensaje": str(e)}
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()