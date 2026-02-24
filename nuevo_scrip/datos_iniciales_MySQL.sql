-- ============================================
--  DATOS DE PRUEBA - TODOS CORREGIDOS
-- ============================================

--  CAJEROS (ESPECIFICANDO COLUMNAS)
INSERT INTO cajero (codigo_cajero, ubicacion, estado) VALUES
('ATM001', 'Sucursal Centro Comercial', 'ACTIVO'),
('ATM002', 'Sucursal Aeropuerto', 'ACTIVO'),
('ATM003', 'Sucursal Mall del Sur', 'INACTIVO');

-- Codigos motivo
INSERT INTO codigo_motivo (codigo, descripcion) VALUES
(1, 'Fondos Insuficientes'),
(2, 'Tarjeta Vencida'),
(3, 'PIN Incorrecto'),
(4, 'Limite de Transacción Excedido'),
(5, 'Tarjeta Bloqueada');

-- Tipos transaccion
INSERT INTO tipo_transaccion (codigo_tipo, descripcion) VALUES
('RETIRO', 'Retiro de efectivo'),
('CONSULTA', 'Consulta de saldo'),
('CAMBIOPIN', 'Cambio de PIN'),
('CONFIRMACION', 'Confirmacion de transaccion');

--  CUENTAS 
INSERT INTO cuenta (numero_cuenta, tipo_cuenta, saldo_disponible, saldo_total, limite_credito, disponible_credito, estado) VALUES
('CD123456789012345678', 'DEBITO', 650000.00, 25000.00, 0.00, 0.00, 'ACTIVA'),
('CC987654321098765432', 'CREDITO', 50000.00, 5000.00, 20000.00, 15000.00, 'ACTIVA'),
('CD111122334444555555', 'DEBITO', 80000.00, 8000.00, 0.00, 0.00, 'INACTIVA'),
('CC555566677788889999', 'CREDITO', 0.00, 0.00, 15000.00, 15000.00, 'CERRADA'),
('CD222233344455556666', 'DEBITO', 500000.00, 50000.00, 0.00, 0.00, 'ACTIVA'),
('CC333344445566667777', 'CREDITO', 100000.00, 10000.00, 10000.00, 10000.00, 'ACTIVA');

-- Tarjetas
INSERT INTO tarjeta (numero_tarjeta, pin, fecha_vencimiento, cvv, tipo_tarjeta, estado, id_cuenta, identificacion_cliente, limite_adelanto_efectivo, disponible_adelanto_efectivo) VALUES
('4111-1111-1111-1111', '1234', '2027-12-01', '123', 'DEBITO', 'ACTIVA', 1, '110520123', 2000.00, 1500.00),
('4222-2222-2222-2222', '5678', '2026-06-01', '456', 'DEBITO', 'ACTIVA', 1, '110520123', 2000.00, 1800.00),
('5111-1111-1111-1111', '2468', '2028-03-01', '789', 'CREDITO', 'ACTIVA', 2, '208760456', 3000.00, 2500.00),
('5222-2222-2222-2222', '1357', '2027-09-01', '012', 'CREDITO', 'VENCIDA', 2, '208760456', 3000.00, 0.00),
('4333-3333-3333-3333', '9999', '2026-12-01', '999', 'DEBITO', 'INACTIVA', 3, '301470789', 1000.00, 0.00),
('5333-3333-3333-3333', '2580', '2028-12-01', '222', 'CREDITO', 'ACTIVA', 5, '402810234', 5000.00, 4500.00);

-- Autorizaciones
INSERT INTO autorizacion (codigo_autorizacion, id_tarjeta, id_cajero, id_tipo_transaccion, monto, estado, fecha_respuesta, respuesta, id_codigo_motivo) VALUES
('AUTH2026', 1, 1, 1, 5000.00, 'APROBADA', NOW(), 'APROBADO', NULL),
('AUTH2027', 2, 2, 2, NULL, 'APROBADA', NOW(), 'APROBADO', NULL),
('AUTH2028', 3, 1, 1, 25000.00, 'RECHAZADA', NOW(), 'RECHAZADO', 1);

-- Movimientos
INSERT INTO movimiento (id_tarjeta, codigo_autorizacion, tipo_movimiento, monto, estado) VALUES
(1, 'AUTH2026', 'RETIRO_EFECTIVO', 5000.00, 'APROBADO'),
(2, 'AUTH2027', 'CONSULTA_SALDO', 0.00, 'APROBADO');

-- VERIFICACIÓN FINAL
SELECT 'TODO CORRECTO' as estado;
SELECT 'Cuentas:', COUNT(*) FROM cuenta UNION ALL
SELECT 'Tarjetas:', COUNT(*) FROM tarjeta UNION ALL
SELECT 'Cajeros:', COUNT(*) FROM cajero UNION ALL
SELECT 'Autorizaciones:', COUNT(*) FROM autorizacion;

-- PRUEBA AUDITORÍA CORREGIDA
UPDATE tarjeta SET pin = '7887' WHERE numero_tarjeta = '4111-1111-1111-1111';
SELECT 'ULTIMA AUDITORIA' AS Titulo;
SELECT * FROM auditoria ORDER BY fecha_auditoria DESC LIMIT 3;