package com.core;

import java.io.*;
import java.net.*;
import java.sql.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CoreBancario {

    private static final String DB_URL = "jdbc:sqlserver://localhost:1433;databaseName=core_bancario;encrypt=false;trustServerCertificate=true;";
    private static final String USER = "nestor_p6";
    private static final String PASS = "12345678";

    public static void main(String[] args) {
        int puerto = 5000;
        ExecutorService pool = Executors.newFixedThreadPool(10);

        try (ServerSocket server = new ServerSocket(puerto)) {
            System.out.println("==========================================");
            System.out.println("   CORE BANCARIO - SERVIDOR INICIADO");
            System.out.println("   Puerto: " + puerto + " | Pool: 10 hilos");
            System.out.println("==========================================");

            while (true) {
                Socket socket = server.accept();
                System.out.println("\n[CONEXIÓN] Cliente detectado desde: " + socket.getInetAddress().getHostAddress());
                pool.execute(() -> manejarCliente(socket));
            }
        } catch (IOException e) {
            System.err.println("Error en el servidor: " + e.getMessage());
        } finally {
            pool.shutdown();
        }
    }

    private static void manejarCliente(Socket socket) {
        try (socket;
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream())); PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {

            String trama = in.readLine();
            if (trama != null) {
                // CORRECCIÓN: Ahora llamamos a procesarCORE2 para que use la lógica completa de
                // SQL Server
                String respuesta = procesarCORE2(trama);

                // RESPUESTA AL AUTORIZADOR
                out.println(respuesta);

                // AUDITORÍA
                registrarEnBitacora(trama, respuesta);

                System.out.println("[" + Thread.currentThread().getName() + "] Trama: " + trama);
                System.out.println("[" + Thread.currentThread().getName() + "] Respuesta: " + respuesta);
            }
        } catch (Exception e) {
            System.err.println("Error procesando cliente: " + e.getMessage());
        }
    }

    /*
     * =========================================================================
     * MÓDULO: CORE1 - PROCESAMIENTO DE TRANSACCIONES (DÉBITO)
     * Descripción: Maneja el acceso a SQL Server, validación de saldos
     * y actualización de cuentas de ahorro/corriente.
     * =========================================================================
     */
    private static String procesarEnBaseDatos(String trama) {
        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASS)) {
            String tipo = trama.substring(0, 1);
            String cuenta = trama.substring(1, 11).trim();

            if (tipo.equals("2")) { // CONSULTA DE SALDO
                return consultarSaldo(conn, cuenta);
            } else if (tipo.equals("1")) { // RETIRO DE EFECTIVO
                double monto = Double.parseDouble(trama.substring(30, 38)) / 100.0;
                return aplicarRetiro(conn, cuenta, monto);
            }
        } catch (Exception e) {
            return "ERROR_DB";
        }
        return "TIPO_INVALIDO";

    }

    private static String consultarSaldo(Connection conn, String cuenta) throws SQLException {
        String sql = "SELECT saldo_disponible FROM dbo.cuenta WHERE numero_cuenta = ?";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cuenta);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    double saldo = rs.getDouble("saldo_disponible");
                    return "OK" + String.format("%019d", (long) (saldo * 100));
                }
            }
        }
        return "CUENTA_NO_EXISTE";
    }

    private static String aplicarRetiro(Connection conn, String cuenta, double monto) throws SQLException {
        String sqlCheck = "SELECT saldo_disponible FROM dbo.cuenta WHERE numero_cuenta = ?";
        try (PreparedStatement ps = conn.prepareStatement(sqlCheck)) {
            ps.setString(1, cuenta);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    double saldo = rs.getDouble("saldo_disponible");
                    if (saldo >= monto) {
                        String sqlUp = "UPDATE dbo.cuenta SET saldo_disponible = saldo_disponible - ? WHERE numero_cuenta = ?";
                        try (PreparedStatement psUp = conn.prepareStatement(sqlUp)) {
                            psUp.setDouble(1, monto);
                            psUp.setString(2, cuenta);
                            psUp.executeUpdate();
                            return "OK";
                        }
                    } else {
                        return "SALDO_INSUFICIENTE";
                    }
                }
            }
        }
        return "CUENTA_NO_EXISTE";
    }

    /*
     * =========================================================================
     * MÓDULO: CORE3 - BITÁCORA DE AUDITORÍA (JSON)
     * Descripción: Registra todas las tramas entrantes y salientes en un
     * archivo de texto plano con formato estructurado JSON.
     * =========================================================================
     */
    private static void registrarEnBitacora(String tramaIn, String respuestaOut) {
        String fecha = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        String jsonLog = String.format("{\"fecha\": \"%s\", \"trama_in\": \"%s\", \"respuesta_out\": \"%s\"}",
                fecha, tramaIn, respuestaOut);

        try (FileWriter fw = new FileWriter("bitacora_core.txt", true); BufferedWriter bw = new BufferedWriter(fw); PrintWriter out = new PrintWriter(bw)) {
            out.println(jsonLog);
        } catch (IOException e) {
            System.err.println("Error Bitácora: " + e.getMessage());
        }
    }

    /*
     * ###########################################################################
     * CORE 2 - PROCESAMIENTO DE TRANSACCIONES
     * Descripcion: Recibe las tramas del AUT y Valida las Tarjetas/Cuentas,
     * Registra los movimientos y responde
     * ###########################################################################
     */
    private static String procesarCORE2(String trama) {
        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASS)) {
            String tipo = trama.substring(0, 1);
            String numCuenta = trama.substring(1, 24).trim();
            String numTarjeta = trama.substring(24, 42).trim(); // Ajustado a 18 para evitar solapamiento

            if ("1".equals(tipo) || "C".equals(tipo)) { // <--- AHORA ACEPTA 'C' TAMBIÉN
                String codAutoriz = trama.substring(42, 50).trim();
                double monto = Double.parseDouble(trama.substring(50, 58)) / 100.0;

                System.out.println("CORE2 - Procesando " + (tipo.equals("C") ? "Confirmación" : "Retiro")
                        + ": Cuenta " + numCuenta + ", Monto: " + monto);

                return procesarRetiroCORE2(conn, numCuenta, numTarjeta, codAutoriz, monto);
            } else if ("2".equals(tipo)) {
                return consultarSaldo(conn, numCuenta);
            }

            return "ERROR_TIPO";
        } catch (Exception e) {
            System.err.println("CORE2 Error: " + e.getMessage());
            return "ERROR_PROCESO";
        }
    }

    private static String procesarRetiroCORE2(Connection conn, String numCuenta, String numTarjeta, String codAutoriz,
            double monto) throws SQLException {
        conn.setAutoCommit(false); // Inicia transacción para CORE 2
        try {
            // 1. VALIDAR CUENTA + TARJETA + SALDO (Leyendo de SQL Server)
            String sqlCheck = "SELECT id_cuenta, saldo_disponible FROM cuenta WHERE numero_cuenta = ?";

            try (PreparedStatement psCheck = conn.prepareStatement(sqlCheck)) {
                psCheck.setString(1, numCuenta);
                try (ResultSet rs = psCheck.executeQuery()) {
                    if (!rs.next()) {
                        conn.rollback();
                        return "CUENTA_NO_EXISTE";
                    }

                    long idCuenta = rs.getLong("id_cuenta");
                    double saldoAnterior = rs.getDouble("saldo_disponible");

                    if (saldoAnterior < monto) {
                        conn.rollback();
                        return "SALDO_INSUFICIENTE";
                    }

                    double saldoNuevo = saldoAnterior - monto;

                    // 2. ACTUALIZAR SALDO
                    String sqlUpdate = "UPDATE cuenta SET saldo_disponible = ? WHERE id_cuenta = ?";
                    try (PreparedStatement psUpdate = conn.prepareStatement(sqlUpdate)) {
                        psUpdate.setDouble(1, saldoNuevo);
                        psUpdate.setLong(2, idCuenta);
                        psUpdate.executeUpdate();
                    }

                    // 3. REGISTRAR MOVIMIENTO (Requerimiento CORE 2: Auditoría en DB)
                    String descripcion = "Retiro ATM Tarjeta: " + numTarjeta;
                    String sqlMov = "INSERT INTO movimiento_tarjeta (id_cuenta, numero_tarjeta, codigo_autorizacion, tipo_movimiento, monto, saldo_anterior, saldo_nuevo, descripcion, fecha_movimiento) VALUES (?, ?, ?, 'RETIRO', ?, ?, ?, ?, GETDATE())";

                    try (PreparedStatement psMov = conn.prepareStatement(sqlMov)) {
                        psMov.setLong(1, idCuenta);
                        psMov.setString(2, numTarjeta);
                        psMov.setString(3, codAutoriz);
                        psMov.setDouble(4, monto);
                        psMov.setDouble(5, saldoAnterior);
                        psMov.setDouble(6, saldoNuevo);
                        psMov.setString(7, descripcion);
                        psMov.executeUpdate();
                    }
                }
            }

            conn.commit(); // Todo salió bien, guardamos cambios
            return "OK";

        } catch (SQLException e) {
            conn.rollback();
            System.err.println("SQL Error en CORE2: " + e.getMessage());
            return "ERROR_SQL";
        } finally {
            conn.setAutoCommit(true);
        }
    }
}
