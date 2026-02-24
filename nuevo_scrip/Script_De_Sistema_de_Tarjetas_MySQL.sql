-- =====================================================================
-- 		SISTEMA DE TARJETAS DE CRÉDITO / DÉBITO CON AUDITORÍA
-- 		Proyecto Programación IV - Colegio Universitario de Cartago
-- =====================================================================

DROP DATABASE IF EXISTS sistema_tarjeta;
CREATE DATABASE sistema_tarjeta CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sistema_tarjeta;

-- ============================================
-- TABLAS PRINCIPALES
-- ============================================

CREATE TABLE cajero (
    id_cajero BIGINT PRIMARY KEY AUTO_INCREMENT,
    codigo_cajero VARCHAR(20) UNIQUE NOT NULL,
    ubicacion VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO'))
);

CREATE TABLE codigo_motivo (
    id_codigo_motivo INT PRIMARY KEY AUTO_INCREMENT,
    codigo INT UNIQUE NOT NULL CHECK (codigo BETWEEN 1 AND 5),
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE tipo_transaccion (
    id_tipo_transaccion INT PRIMARY KEY AUTO_INCREMENT,
    codigo_tipo VARCHAR(30) UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE cuenta (
    id_cuenta BIGINT PRIMARY KEY AUTO_INCREMENT,
    numero_cuenta VARCHAR(23) NOT NULL UNIQUE,  -- Formato XXXX-XXXX-XXXX-XX
    tipo_cuenta VARCHAR(10) NOT NULL CHECK (tipo_cuenta IN ('DEBITO', 'CREDITO')),
    saldo_disponible DECIMAL(15,2) NOT NULL DEFAULT 0 CHECK (saldo_disponible >= 0),
    saldo_total DECIMAL(15,2) NOT NULL DEFAULT 0 CHECK (saldo_total >= 0),
    limite_credito DECIMAL(15,2) NOT NULL DEFAULT 0 CHECK (limite_credito >= 0),
    disponible_credito DECIMAL(15,2) NOT NULL DEFAULT 0 CHECK (disponible_credito >= 0),
    estado VARCHAR(20) DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'INACTIVA', 'CERRADA'))
);

CREATE TABLE tarjeta (
    id_tarjeta BIGINT PRIMARY KEY AUTO_INCREMENT,
    numero_tarjeta VARCHAR(20) NOT NULL,
    pin VARCHAR(4) NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    cvv VARCHAR(3) NOT NULL,
    tipo_tarjeta VARCHAR(10) NOT NULL CHECK (tipo_tarjeta IN ('DEBITO', 'CREDITO')),
    estado VARCHAR(20) DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'INACTIVA', 'VENCIDA')),
    id_cuenta BIGINT NOT NULL,
    identificacion_cliente VARCHAR(20),
    limite_adelanto_efectivo DECIMAL(15,2) DEFAULT 0 CHECK (limite_adelanto_efectivo >= 0),
    disponible_adelanto_efectivo DECIMAL(15,2) DEFAULT 0 CHECK (disponible_adelanto_efectivo >= 0),
    UNIQUE KEY uk_numero_tarjeta (numero_tarjeta),
    CONSTRAINT fk_tarjeta_cuenta FOREIGN KEY (id_cuenta) REFERENCES cuenta(id_cuenta)
);

CREATE TABLE autorizacion (
    id_autorizacion BIGINT PRIMARY KEY AUTO_INCREMENT,
    codigo_autorizacion CHAR(8) NOT NULL UNIQUE,
    id_tarjeta BIGINT NOT NULL,
    id_cajero BIGINT NOT NULL,
    id_tipo_transaccion INT NOT NULL,
    monto DECIMAL(15,2),
    estado VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'APROBADA', 'RECHAZADA', 'CONFIRMADA')),
    fecha_solicitud DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta DATETIME NULL,
    respuesta VARCHAR(10),
    id_codigo_motivo INT NULL,
    CONSTRAINT fk_autorizacion_tarjeta FOREIGN KEY (id_tarjeta) REFERENCES tarjeta(id_tarjeta),
    CONSTRAINT fk_autorizacion_cajero FOREIGN KEY (id_cajero) REFERENCES cajero(id_cajero),
    CONSTRAINT fk_autorizacion_tipo FOREIGN KEY (id_tipo_transaccion) REFERENCES tipo_transaccion(id_tipo_transaccion),
    CONSTRAINT fk_autorizacion_motivo FOREIGN KEY (id_codigo_motivo) REFERENCES codigo_motivo(id_codigo_motivo)
);

CREATE TABLE movimiento (
    id_movimiento BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_tarjeta BIGINT NOT NULL,
    codigo_autorizacion CHAR(8) NOT NULL,
    tipo_movimiento VARCHAR(50) NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'APROBADO', 'RECHAZADO')),
    fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mov_credito_tarjeta FOREIGN KEY (id_tarjeta) REFERENCES tarjeta(id_tarjeta),
    CONSTRAINT fk_mov_credito_aut FOREIGN KEY (codigo_autorizacion) REFERENCES autorizacion(codigo_autorizacion)
);

-- ✅ TABLA AUDITORÍA CORREGIDA (sin DEFAULT USER())
CREATE TABLE auditoria (
    id_auditoria BIGINT PRIMARY KEY AUTO_INCREMENT,
    tabla_afectada VARCHAR(50) NOT NULL,
    accion VARCHAR(20) NOT NULL,
    id_registro_afectado BIGINT,
    numero_referencia VARCHAR(50),
    campo_modificado VARCHAR(50),
    valor_anterior TEXT,
    valor_nuevo TEXT,
    usuario VARCHAR(100) DEFAULT NULL,        -- ✅ CORREGIDO: NULL en lugar de USER()
    ip_address VARCHAR(45) DEFAULT NULL,
    fecha_auditoria DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_fecha_accion (fecha_auditoria, accion),
    INDEX idx_numero_ref (numero_referencia),
    INDEX idx_tabla_fecha (tabla_afectada, fecha_auditoria)
);

-- TRIGGERS (capturan USER() dinámicamente)
DELIMITER $$
CREATE TRIGGER tr_tarjeta_update_auditoria 
AFTER UPDATE ON tarjeta
FOR EACH ROW
BEGIN
    IF OLD.pin != NEW.pin THEN
        INSERT INTO auditoria (
            tabla_afectada, accion, numero_referencia, 
            campo_modificado, valor_anterior, valor_nuevo, 
            id_registro_afectado, usuario
        ) VALUES (
            'tarjeta', 'UPDATE', NEW.numero_tarjeta, 'pin', 
            OLD.pin, NEW.pin, NEW.id_tarjeta, USER()
        );
    END IF;
    
    IF OLD.estado != NEW.estado THEN
        INSERT INTO auditoria (
            tabla_afectada, accion, numero_referencia, 
            campo_modificado, valor_anterior, valor_nuevo, usuario
        ) VALUES (
            'tarjeta', 'UPDATE', NEW.numero_tarjeta, 'estado', 
            OLD.estado, NEW.estado, USER()
        );
    END IF;
END$$

CREATE TRIGGER tr_cuenta_update_auditoria 
AFTER UPDATE ON cuenta
FOR EACH ROW
BEGIN
    IF OLD.saldo_disponible != NEW.saldo_disponible OR 
       OLD.saldo_total != NEW.saldo_total OR
       OLD.disponible_credito != NEW.disponible_credito THEN
        INSERT INTO auditoria (
            tabla_afectada, accion, numero_referencia, campo_modificado, 
            valor_anterior, valor_nuevo, id_registro_afectado, usuario
        ) VALUES (
            'cuenta', 'UPDATE', NEW.numero_cuenta, 'saldos',
            CONCAT('disp:', OLD.saldo_disponible, '|total:', OLD.saldo_total, '|cred:', OLD.disponible_credito),
            CONCAT('disp:', NEW.saldo_disponible, '|total:', NEW.saldo_total, '|cred:', NEW.disponible_credito),
            NEW.id_cuenta, USER()
        );
    END IF;
END$$
DELIMITER ;

-- ÍNDICES
CREATE INDEX idx_cajero_codigo ON cajero(codigo_cajero);
CREATE INDEX idx_autorizacion_codigo ON autorizacion(codigo_autorizacion);
CREATE INDEX idx_autorizacion_fecha ON autorizacion(fecha_solicitud);
CREATE INDEX idx_cuenta_tipo ON cuenta(tipo_cuenta, estado);
CREATE INDEX idx_tarjeta_tipo ON tarjeta(tipo_tarjeta, estado);

-- =====================================================================
-- 				ALTER TABLES
-- =====================================================================

-- ALTER TABLE tarjeta
-- 	MODIFY numero_tarjeta VARBINARY (32), MODIFY pin VARBINARY (32), MODIFY cvv VARBINARY (32);    