# Herramientas de seguridad AES - Compatible con VARBINARY(32)
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from config import KEY

# En seguridad.py
def descifrar_dato(dato_hex):
    """Descifra datos genéricos (tarjeta, CVV, etc.) recibidos en HEX"""
    try:
        if not dato_hex: return None
        cipher = AES.new(KEY, AES.MODE_ECB)
        # Convertimos de HEX a bytes antes de descifrar
        datos_binarios = bytes.fromhex(dato_hex)
        decrypted = unpad(cipher.decrypt(datos_binarios), AES.block_size)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Error descifrando dato: {e}")
        return None

def cifrar_dato(dato_plano):
    """Cifra datos genéricos y los retorna en formato HEX para transporte/almacenamiento"""
    cipher = AES.new(KEY, AES.MODE_ECB)
    cifrado = cipher.encrypt(pad(dato_plano.encode(), AES.block_size))
    return cifrado.hex()
