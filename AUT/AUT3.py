# AUT 3 - Cambio PIN - CORREGIDO DEFINITIVO
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DATABASE, SERVER, PASSWORD, USUARIO
from AUT4 import registrar_evento_aut4

class Conexion:
    """Conexion singleton para AUT 3"""
    conn = None

    @staticmethod
    def conectar():
        try:
            if Conexion.conn is None or not Conexion.conn.is_connected():
                Conexion.conn = mysql.connector.connect(
                    host=SERVER, port=3306, user=USUARIO,
                    password=PASSWORD, database=DATABASE
                )
            return True
        except Error as e:
            print(f"ERROR DB AUT3: {e}")
            return False

def procesar_cambio_pin(datos):
    """Cambia PIN - Registra en autorizacion"""
    n_tarjeta = datos.get("numero_tarjeta", "").strip()
    id_cajero = datos.get("id_cajero", 1)
    pin_actual = datos.get("pin_actual", "").strip()
    pin_nuevo = datos.get("pin_nuevo", "").strip()

    print(f"AUT3 - Cambio PIN: {n_tarjeta}")

    registrar_evento_aut4(n_tarjeta[:16], id_cajero, "SOLICITUD_CAMBIO_PIN")

    cursor = None
    try:
        if not Conexion.conectar():
            return {"estado": "ERROR", "mensaje": "Error conexion DB"}

        cursor = Conexion.conn.cursor(dictionary=True)

        # Buscar tarjeta ignorando guiones
        query = """
            SELECT t.id_tarjeta, t.pin, t.estado as estado_tarjeta
            FROM tarjeta t 
            JOIN cuenta c ON t.id_cuenta = c.id_cuenta
            WHERE REPLACE(t.numero_tarjeta, '-', '') = REPLACE(%s, '-', '')
            AND t.estado = 'ACTIVA' AND c.estado = 'ACTIVA'
        """
        cursor.execute(query, (n_tarjeta,))
        fila = cursor.fetchone()

        if not fila:
            msg = "Tarjeta no existe o inactiva"
            registrar_evento_aut4(n_tarjeta[:16], id_cajero, "CAMBIO_PIN_TARJETA_INACTIVA")
            return {"estado": "ERROR", "mensaje": msg}

        # Validar PIN actual
        if fila['pin'] != pin_actual:
            registrar_evento_aut4(n_tarjeta[:16], id_cajero, "CAMBIO_PIN_FALLIDO_PIN_INC")
            return {"estado": "ERROR", "mensaje": "PIN actual incorrecto"}

        # Validar nuevo PIN
        if len(pin_nuevo) != 4 or not pin_nuevo.isdigit():
            return {"estado": "ERROR", "mensaje": "Nuevo PIN debe ser 4 digitos numericos"}

        # ✅ CORREGIDO: Codigo de 8 caracteres exactos NUMERICOS
        codigo_p = f"{int(datetime.now().timestamp()*1000) % 10000000:08d}"

        # Actualizar PIN
        cursor.execute(
            "UPDATE tarjeta SET pin = %s WHERE id_tarjeta = %s",
            (pin_nuevo, fila["id_tarjeta"])
        )

        # Registrar autorizacion
        cursor.execute("""
            INSERT INTO autorizacion 
            (codigo_autorizacion, id_tarjeta, id_cajero, id_tipo_transaccion, 
             monto, estado, fecha_solicitud, respuesta) 
            VALUES (%s, %s, %s, 3, 0, 'APROBADA', NOW(), 'PIN_CAMBIADO')
        """, (codigo_p, fila["id_tarjeta"], id_cajero))

        Conexion.conn.commit()
        registrar_evento_aut4(n_tarjeta[:16], id_cajero, "CAMBIO_PIN_EXITOSO")

        return {
            "estado": "OK",
            "mensaje": "PIN actualizado correctamente",
            "codigo_autorizacion": codigo_p
        }

    except Exception as e:
        if Conexion.conn and Conexion.conn.is_connected():
            Conexion.conn.rollback()
        print(f"ERROR AUT3: {e}")
        registrar_evento_aut4(n_tarjeta[:16], id_cajero, f"CAMBIO_PIN_ERROR_{str(e)[:20]}")
        return {"estado": "ERROR", "mensaje": f"Error interno: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
