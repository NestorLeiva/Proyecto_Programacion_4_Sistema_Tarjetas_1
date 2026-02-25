-- =====================================================
-- DATOS DE PRUEBA - CORE BANCARIO (5 REGISTROS)
-- =====================================================

USE core_bancario;
GO

-- =====================================================
-- 1. CLIENTES (5 clientes costarricenses)
-- =====================================================
INSERT INTO cliente (nombre, identificacion) VALUES
('Juan Pérez', '110520123'),
('María González', '110520125'),
('Carlos Ramírez', '208760456'),
('Ana Martínez', '202760756'),
('Luis Hernández', '301471789');
GO

USE core_bancario;
GO

-- =====================================================
-- 2. CUENTAS (5 cuentas para los clientes)
-- =====================================================
INSERT INTO cuenta (numero_cuenta, id_cliente, saldo_disponible, estado) VALUES
('CD123456789012345678', 1, 650000.00, 'ACTIVA'),
('CC987654321098765432', 2, 505000.00, 'ACTIVA'),
('CD111122334444555555', 3, 804000.00, 'ACTIVA'),
('CC555566677788889999', 4, 0.00, 'BLOQUEADA'),
('CD222233344455556666', 5, 509000.00, 'ACTIVA');

SELECT * FROM cuenta;
GO

-- =====================================================
-- 3. TARJETAS (5 tarjetas vinculadas)
-- =====================================================
INSERT INTO tarjeta_cuenta (numero_tarjeta, id_cuenta, estado) VALUES
('4111-1111-1111-1111', 1, 'ACTIVA'),
('4111-2222-2222-2222', 2, 'ACTIVA'),
('4111-3333-3333-3333', 3, 'VENCIDA'),
('4111-4444-4444-4444', 1, 'ACTIVA'),
('4111-5555-5555-5555', 5, 'ACTIVA');
SELECT * FROM tarjeta_cuenta;
GO

-- =====================================================
-- 4. MOVIMIENTOS (5 transacciones reales)
-- =====================================================
INSERT INTO movimiento_tarjeta (id_cuenta, numero_tarjeta, codigo_autorizacion, tipo_movimiento, monto, saldo_anterior, saldo_nuevo, descripcion, estado) VALUES
(1, '4111-1111-1111-1111', 'A1234567', 'RETIRO_EFECTIVO', 50000.00, 1550000.00, 1500000.00, 'Retiro ATM Walmart Cartago', 'PROCESADO'),
(2, '4111-2222-2222-2222', 'B2345678', 'PAGO_SERVICIOS', 30000.00, 880000.00, 850000.00, 'Pago luz ICE', 'PROCESADO'),
(3, '4111-3333-3333-3333', 'C3456789', 'DEPOSITO', 200000.00, 2000000.00, 2200000.00, 'Nómina BAC San José', 'PROCESADO'),
(1, '4111-4444-4444-4444', 'D4567890', 'TRANSFERENCIA', 100000.00, 1500000.00, 1400000.00, 'Transferencia a Ana Martínez', 'PENDIENTE'),
(5, '4111-5555-5555-5555', 'E5678901', 'COMPRA_TIENDA', 75000.00, 1825000.00, 1750000.00, 'Auto Mercado San Rafael', 'PROCESADO');
SELECT * FROM movimiento_tarjeta;
GO