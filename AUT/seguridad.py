# Herramientas de seguridad AES - Compatible con VARBINARY(32)
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from config import KEY

def descifrar_pin(pin_binario):
    """Descifra PIN desde VARBINARY(32) de tabla tarjeta"""
    try:
        cipher = AES.new(KEY, AES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(pin_binario), AES.block_size)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Error descifrado: {e}")
        return None

def cifrar_pin(pin_plano):
    """Cifra PIN para VARBINARY(32) en tabla tarjeta"""
    cipher = AES.new(KEY, AES.MODE_ECB)
    return cipher.encrypt(pad(pin_plano.encode(), AES.block_size))
