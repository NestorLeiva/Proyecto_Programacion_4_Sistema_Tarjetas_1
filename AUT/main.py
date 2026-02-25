import os
import subprocess
import time
from servidor import iniciar_servidor
from AUT4 import registrar_evento_aut4


def levantar_core_java():
    """Lanza el servidor Java automáticamente"""
    # Ajusta esta ruta a donde esté tu JAR realmente
    ruta_jar = "./CoreBancario/target/corebancario-1.0-SNAPSHOT.jar"

    if os.path.exists(ruta_jar):
        print(" > Levantando CoreBancario (Java)...")
        # Abre una nueva ventana de consola para Java
        subprocess.Popen(["java", "-jar", ruta_jar],
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(3)  # Esperar a que el server Java esté listo
    else:
        print(
            f" WARN: No se encontró el JAR en {ruta_jar}. Inicia Java manualmente.")


def inicializar_sistema():
    registrar_evento_aut4("SISTEMA", 0, "INICIO_SERVIDOR", 0)
    print(" > AUT4 sincronizado (Bitácora lista)")


if __name__ == "__main__":
    print("============================================================")
    print("  SISTEMA AUTORIZADOR BANCARIO (PYTHON SERVER)")
    print("============================================================")

    levantar_core_java()
    inicializar_sistema()

    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\n Servidor detenido manualmente")
        registrar_evento_aut4("SISTEMA", 0, "APAGADO_SERVIDOR", 0)
