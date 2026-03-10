using SimuladorCliente.ServiceReference1;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SimuladorCliente
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("--- SIMULADOR COMPLETO: SISTEMA DE TARJETAS ---");

            try
            {
                AutenticacionServiceClient cliente = new AutenticacionServiceClient();

                // Datos base para las pruebas
                string identificacionPrueba = "101110111";
                string usuarioPlano = "rodri";
                string contrasenaPlana = "Admin123!@Rodr"; // Exactamente 14 caracteres

                // ==========================================
                // 1. PROBAR CREACIÓN DE USUARIO
                // ==========================================
                Console.WriteLine("\n[1] Probando WS_AUTENTICACION2: Creando usuario...");
                UsuarioModelo nuevoAdmin = new UsuarioModelo
                {
                    Identificacion = identificacionPrueba,
                    Nombre = "Rodrigo",
                    PrimerApellido = "Admin",
                    SegundoApellido = "Sistema",
                    CorreoElectronico = "rodri@bancoabc.com",
                    Usuario = Seguridad.Encriptar(usuarioPlano),
                    Contrasena = Seguridad.Encriptar(contrasenaPlana),
                    Tipo = 1
                };

                var respuestaCreacion = cliente.CrearUsuario(nuevoAdmin);
                Console.WriteLine($"Respuesta Creación -> Resultado: {respuestaCreacion.Resultado}, Mensaje: {respuestaCreacion.Mensaje}");
                // Nota: Si ya corriste el simulador antes, aquí dirá "Usuario ya existe..." y está bien.

                // ==========================================
                // 2. PROBAR AUTENTICACIÓN (LOGIN)
                // ==========================================
                Console.WriteLine("\n[2] Probando WS_AUTENTICADOR1: Autenticando usuario...");
                string usuarioLogin = Seguridad.Encriptar(usuarioPlano);
                string contrasenaLogin = Seguridad.Encriptar(contrasenaPlana);

                var respuestaLogin = cliente.AutenticarUsuario(usuarioLogin, contrasenaLogin, 1);
                Console.WriteLine($"Respuesta Login -> Resultado: {respuestaLogin.Resultado}, Mensaje: {respuestaLogin.Mensaje}");

                // ==========================================
                // 3. PROBAR MODIFICACIÓN DE USUARIO
                // ==========================================
                Console.WriteLine("\n[3] Probando WS_AUTENTICACION2: Modificando usuario...");

                // Cambiaremos el nombre y el correo. La identificación debe ser la misma.
                string nuevaContrasena = "Admin123!@Modi"; // 14 caracteres para pasar el Regex

                UsuarioModelo adminModificado = new UsuarioModelo
                {
                    Identificacion = identificacionPrueba, // Llave primaria, NO se cambia
                    Nombre = "RodrigoMod", // Modificamos el nombre (sin espacios por el regex)
                    PrimerApellido = "Admin",
                    SegundoApellido = "Sistema",
                    CorreoElectronico = "nuevo.correo@bancoabc.com", // Modificamos el correo
                    Usuario = Seguridad.Encriptar("rodri_nuevo"), // Modificamos el usuario
                    Contrasena = Seguridad.Encriptar(nuevaContrasena),
                    Tipo = 1
                };

                var respuestaModificacion = cliente.ModificarUsuario(adminModificado);
                Console.WriteLine($"Respuesta Modificación -> Resultado: {respuestaModificacion.Resultado}, Mensaje: {respuestaModificacion.Mensaje}");

                // ==========================================
                // 4. PROBAR CAMBIO DE ESTADO
                // ==========================================
                Console.WriteLine("\n[4] Probando WS_AUTENTICACION2: Cambiando estado de usuario...");

                // Cambiamos el estado de activo a inactivo
                var respuestaEstado = cliente.CambiarEstadoUsuario(identificacionPrueba, "inactivo");
                Console.WriteLine($"Respuesta Cambio Estado -> Resultado: {respuestaEstado.Resultado}, Mensaje: {respuestaEstado.Mensaje}");

            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error de conexión: Verifique que el WCF esté en ejecución.\nDetalle: {ex.Message}");
            }

            Console.WriteLine("\nPresiona cualquier tecla para salir.");
            Console.ReadKey();
        }
    }
}