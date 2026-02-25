# 🏦 Sistema Autorizador Bancario Multi-Tier (Proyecto P6)

Este proyecto es un ecosistema bancario distribuido que simula el flujo real de transacciones de un ATM. La arquitectura integra tres lenguajes de programación distintos y dos motores de base de datos para demostrar interoperabilidad y manejo de sistemas críticos.

## 🏗️ Arquitectura del Sistema

El sistema utiliza una topología de microservicios comunicados mediante **Sockets TCP** y protocolos mixtos (Tramas de longitud fija y objetos JSON).

* **Capa de Cliente (Simulador ATM - C#):** Interfaz de consola que captura las solicitudes del usuario y gestiona la configuración del ID de Cajero.
* **Capa de Middleware (Autorizador - Python):** Orquestador de lógica de negocio. Realiza validaciones de seguridad (PIN/Estado de cuenta), gestiona bitácoras de auditoría y sincroniza datos.
* **Capa de Datos Core (Core Bancario - Java):** Servidor multihilo de alta disponibilidad que procesa el libro mayor contable en una base de datos centralizada.



---

## 🛠️ Stack Tecnológico

| Componente | Lenguaje | Base de Datos | Responsabilidad |
| :--- | :--- | :--- | :--- |
| **Simulador** | .NET / C# | N/A | Captura de datos y formateo de tramas. |
| **Autorizador** | Python 3.11+ | **MySQL** | Validación de PIN, Gestión de Bitácora y Reglas. |
| **Core** | Java 21+ (JDK) | **SQL Server** | Procesamiento de saldos y persistencia contable. |

---

## 📋 Funcionalidades Implementadas

1.  **AUT1 - Retiro de Efectivo:** Sincronización de saldos en tiempo real entre MySQL y SQL Server.
2.  **AUT2 - Consulta de Saldo:** Recuperación de montos actuales desde el Core Java.
3.  **AUT3 - Cambio de PIN:** Actualización segura de credenciales mediante objetos JSON.
4.  **AUT4 - Auditoría:** Registro asíncrono de eventos en archivos planos (`bitacora_4.txt`) con enmascaramiento de datos sensibles.

---

## 🚀 Guía de Instalación y Uso

### 1. Configuración de Bases de Datos
* **MySQL:** Importar tabla `tarjeta`, `cuenta`, `cajero` y `autorizacion`.
* **SQL Server:** Asegurar que la tabla `Cuentas` tenga el saldo maestro sincronizado.

### 2. Orden de Ejecución Requerido
Para garantizar que los sockets puedan conectarse, inicie los servicios en este orden:

1.  **Levantar Core Java:**
    ```bash
    # Ejecutar desde el directorio CoreBancario
    java com.core.CoreBancario
    ```
2.  **Levantar Autorizador Python:**
    ```bash
    # Ejecutar desde el directorio AUT
    python main.py
    ```
3.  **Ejecutar Simulador C#:**
    * Abrir en Visual Studio.
    * Configurar el ID de Cajero al iniciar la aplicación.

---

## 📊 Protocolo de Comunicación

### Trama de Texto (C# a Python)
Para Retiros y Consultas se utiliza una trama de **33 caracteres**:
`[Tipo:1][Tarjeta:16][Monto:8][PIN:4][Cajero:4]`

### Trama Core (Python a Java)
Para sincronización de saldos se utiliza una trama de **58 caracteres**:
`[Tipo:1][Cuenta:23][Tarjeta:18][CodAuth:8][Monto:8]`

### Formato JSON (C# a Python)
Para el Cambio de PIN se utiliza un objeto estructurado:
```json
{
  "tipo": "cambio_pin",
  "numero_tarjeta": "4111...",
  "pin_actual": "2020",
  "pin_nuevo": "1515",
  "id_cajero": 1
}


## 📝 Auditoría y Seguridad
El sistema implementa un módulo de auditoría (AUT4) que registra cada paso del proceso. Las tarjetas se almacenan de forma segura y los errores de base de datos son capturados mediante excepciones personalizadas para evitar fugas de información en el cliente final.