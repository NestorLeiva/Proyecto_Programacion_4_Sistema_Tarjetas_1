-- =====================================================
-- CORE BANCARIO - SQL SERVER
-- =====================================================

USE master;
GO

-- creo la Base de Datos si No Existe

IF NOT EXISTS ( SELECT name FROM SYS.DATABASES WHERE NAME = 'core_bancario')
BEGIN
	CREATE DATABASE core_bancario;
	PRINT '+ BASE DE DATOS CORE_BANCARIO CREADA';
END
ELSE
	PRINT ' ++ BASE DE DATOS YA EXISTE';
GO


USE core_bancario;
GO


-- =====================================================
--				TABLAS
-- =====================================================


-- TABLA CLIENTE

IF NOT EXISTS (SELECT * FROM SYSOBJECTS WHERE name = 'cliente' AND xtype = 'U')
BEGIN
	CREATE TABLE cliente (
	id_cliente BIGINT PRIMARY KEY IDENTITY(1,1),
	nombre NVARCHAR (100) NOT NULL,
	identificacion CHAR (20) UNIQUE NOT NULL,
	estado NVARCHAR(10) DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO','INACTIVO')),
	fecha_registro DATETIME2 DEFAULT SYSDATETIME()
	);
	PRINT '+ TABLA CLIENTE CREADA';
END 
GO


-- TABLA CUENTA

IF NOT EXISTS (SELECT * FROM SYSOBJECTS WHERE name = 'cuenta' AND xtype = 'U')
BEGIN
	CREATE TABLE cuenta (
	id_cuenta BIGINT PRIMARY KEY IDENTITY (1,1),
	numero_cuenta CHAR(25) UNIQUE NOT NULL,
	id_cliente BIGINT NOT NULL,
	saldo_disponible DECIMAL(15,2) DEFAULT 0 NOT NULL,
	estado NVARCHAR(10) DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'INACTIVA', 'BLOQUEADA')) NOT NULL, 
	fecha_apertura DATETIME2 DEFAULT SYSDATETIME()
	);
	PRINT '+ TABLA CUENTA CREADA';
END 
GO

-- TABLA TARJETA_CUENTA

IF NOT EXISTS (SELECT * FROM SYSOBJECTS WHERE name = 'tarjeta_cuenta' AND xtype = 'U')
BEGIN
	CREATE TABLE tarjeta_cuenta (
	id_tarjeta_cuenta BIGINT PRIMARY KEY IDENTITY (1,1),
	numero_tarjeta CHAR(25) NOT NULL,
	id_cuenta BIGINT NOT NULL,
	fecha_asignacion DATETIME2 DEFAULT SYSDATETIME(),
	estado NVARCHAR(10) DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'INACTIVA', 'VENCIDA'))
	);
	PRINT '+ TABLA TARJETA_CUENTA CREADA';
END 
GO

-- TABLA MOVIMIENTO_CUENTA

IF NOT EXISTS (SELECT * FROM SYSOBJECTS WHERE name = 'movimiento_tarjeta' AND xtype = 'U')
BEGIN
	CREATE TABLE movimiento_tarjeta (
	id_movimiento BIGINT PRIMARY KEY IDENTITY(1,1),
	id_cuenta BIGINT NOT NULL,
	numero_tarjeta CHAR(20),
	codigo_autorizacion CHAR(8),
	tipo_movimiento NVARCHAR(30) NOT NULL,
	monto DECIMAL(15,2) NOT NULL,
	saldo_anterior DECIMAL(15,2) NOT NULL,
	saldo_nuevo DECIMAL(15,2) NOT NULL,
	descripcion NVARCHAR(255),
	fecha_movimiento DATETIME2 DEFAULT SYSDATETIME(),
	estado NVARCHAR(20) DEFAULT 'PROCESADO' CHECK (estado IN ('PENDIENTE','PROCESADO','RECHAZADO'))
	);
	PRINT '+ TABLA MOVIMIENTO_TARJETA CREADA';
END 
GO



-- =====================================================
--				TABLAS
-- =====================================================


USE core_bancario;

-- FK CUENTA -> CLIENTE
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_cuenta_cliente')
BEGIN
	ALTER TABLE cuenta
		ADD CONSTRAINT FK_cuenta_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente);
	PRINT '+ FK CUENTA_CLIENTE CREADA';
END
GO

-- KF TARJETA -> CUENTA
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_tarjeta_cuenta')
BEGIN
	ALTER TABLE tarjeta_cuenta
		ADD CONSTRAINT FK_tarjeta_cuenta FOREIGN KEY (id_cuenta) REFERENCES cuenta(id_cuenta);
	PRINT '+ FK TARJETA_CUENTA CREADA';
END
GO


-- FK MOVIMIENTO_TARJETA -> CUENTA
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_movimiento_cuenta')
BEGIN
	ALTER TABLE movimiento_tarjeta
		ADD CONSTRAINT FK_movimiento_cuenta FOREIGN KEY (id_cuenta) REFERENCES cuenta(id_cuenta);
	PRINT '+ FK MOVIMIENTO_CUENTA CREADA';
END
GO

-- =====================================================
--					INDICES
-- =====================================================

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_cuenta_numero')
    CREATE INDEX IX_cuenta_numero ON cuenta(numero_cuenta);
    
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_tarjeta_numero')
    CREATE INDEX IX_tarjeta_numero ON tarjeta_cuenta(numero_tarjeta);
    
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimiento_fecha')
    CREATE INDEX IX_movimiento_fecha ON movimiento_tarjeta(fecha_movimiento);
GO

