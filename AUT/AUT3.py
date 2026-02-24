# AUT 3 - Cambio PIN - Adaptado a nueva DB estructura
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DATABASE, SERVER, PASSWORD, USUARIO
from AUT4 import registrar_evento_aut4
from seguridad import descifrar_pin, cifrar_pin


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
    """Cambia PIN - Registra en autorizacion y activa TRIGGER auditoria"""
    n_tarjeta = datos.get("numero_tarjeta", "")
    id_cajero = datos.get("id_cajero", 1)

    registrar_evento_aut4(n_tarjeta, id_cajero, "SOLICITUD_CAMBIO_PIN")

    cursor = None
    try:
        if not Conexion.conectar():
            return {"estado": "ERROR", "mensaje": "Error conexion DB"}

        cursor = Conexion.conn.cursor(dictionary=True)

        # 1. Buscar tarjeta y validar cuenta activa
        query = """
            SELECT t.id_tarjeta, t.pin, t.estado as estado_tarjeta
            FROM tarjeta t 
            JOIN cuenta c ON t.id_cuenta = c.id_cuenta
            WHERE t.numero_tarjeta = %s AND t.estado = 'ACTIVA' AND c.estado = 'ACTIVA'
        """
        cursor.execute(query, (n_tarjeta,))
        fila = cursor.fetchone()

        if not fila:
            msg = "Tarjeta no existe o inactiva"
            registrar_evento_aut4(n_tarjeta, id_cajero,
                                  "CAMBIO_PIN_TARJETA_INACTIVA")
            return {"estado": "ERROR", "mensaje": msg}

        # 2. Validar PIN actual (desencriptado)
        pin_db_binario = fila["pin"]  # VARBINARY(32)
        if descifrar_pin(pin_db_binario) != datos["pin_actual"]:
            registrar_evento_aut4(n_tarjeta, id_cajero,
                                  "CAMBIO_PIN_FALLIDO_PIN_INC")
            return {"estado": "ERROR", "mensaje": "PIN actual incorrecto"}

        # 3. Cifrar nuevo PIN
        nuevo_pin_binario = cifrar_pin(datos["pin_nuevo"])

        # 4. Actualizar PIN (TRIGGER auditoria se activa automaticamente)
        cursor.execute("UPDATE tarjeta SET pin = %s WHERE id_tarjeta = %s",
                       (nuevo_pin_binario, fila["id_tarjeta"]))

        # 5. Registrar en tabla autorizacion (nuevo formato)
        codigo_p = f"PIN{datetime.now().strftime('%H%M%S')}"
        cursor.execute("""
            INSERT INTO autorizacion 
            (codigo_autorizacion, id_tarjeta, id_cajero, id_tipo_transaccion, 
             monto, estado, fecha_solicitud, respuesta) 
            VALUES (%s, %s, %s, 
                   (SELECT id_tipo_transaccion FROM tipo_transaccion 
                    WHERE codigo_tipo = 'CAMBIO_PIN' LIMIT 1), 
                   0, 'APROBADA', NOW(), 'OK')
        """, (codigo_p, fila["id_tarjeta"], id_cajero))

        Conexion.conn.commit()
        registrar_evento_aut4(n_tarjeta, id_cajero, "CAMBIO_PIN_EXITOSO")

        return {
            "estado": "OK",
            "mensaje": "PIN actualizado correctamente",
            "codigo_autorizacion": codigo_p
        }

    except Exception as e:
        Conexion.conn.rollback()
        return {"estado": "ERROR", "mensaje": f"Error interno: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
