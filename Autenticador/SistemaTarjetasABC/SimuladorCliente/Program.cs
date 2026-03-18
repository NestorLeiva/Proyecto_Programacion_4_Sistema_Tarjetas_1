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
            AutenticacionServiceClient cliente = new AutenticacionServiceClient();
            bool salir = false;

            while (!salir)
            {
                Console.Clear();
                Console.WriteLine("=================================================");
                Console.WriteLine("      SIMULADOR: SISTEMA DE TARJETAS ABC         ");
                Console.WriteLine("=================================================");
                Console.WriteLine("1. WS_AUTENTICACION2: Crear un nuevo usuario");
                Console.WriteLine("2. WS_AUTENTICADOR1:  Autenticar (Hacer Login)");
                Console.WriteLine("3. WS_AUTENTICACION2: Modificar un usuario");
                Console.WriteLine("4. WS_AUTENTICACION2: Cambiar estado de usuario");
                Console.WriteLine("5. Salir del simulador");
                Console.WriteLine("=================================================");
                Console.Write("Elige una opción (1-5): ");

                string opcion = Console.ReadLine();

                try
                {
                    switch (opcion)
                    {
                        case "1":
                            MenuCrearUsuario(cliente);
                            break;
                        case "2":
                            MenuAutenticarUsuario(cliente);
                            break;
                        case "3":
                            MenuModificarUsuario(cliente);
                            break;
                        case "4":
                            MenuCambiarEstado(cliente);
                            break;
                        case "5":
                            salir = true;
                            Console.WriteLine("Saliendo del simulador...");
                            break;
                        default:
                            Console.WriteLine("Opción no válida. Intenta de nuevo.");
                            break;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"\n[ERROR DE CONEXIÓN] Verifica que el servicio WCF esté corriendo.");
                    Console.WriteLine($"Detalle: {ex.Message}");
                }

                if (!salir)
                {
                    Console.WriteLine("\nPresiona cualquier tecla para volver al menú principal...");
                    Console.ReadKey();
                }
            }
        }

        // ==========================================
        // OPCIÓN 1: CREAR USUARIO
        // ==========================================
        static void MenuCrearUsuario(AutenticacionServiceClient cliente)
        {
            Console.Clear();
            Console.WriteLine("--- CREAR NUEVO USUARIO ---");

            UsuarioModelo nuevoUsuario = new UsuarioModelo();

            Console.Write("Identificación: ");
            nuevoUsuario.Identificacion = Console.ReadLine();

            Console.Write("Nombre (Sin espacios ni números): ");
            nuevoUsuario.Nombre = Console.ReadLine();

            Console.Write("Primer Apellido (Sin espacios ni números): ");
            nuevoUsuario.PrimerApellido = Console.ReadLine();

            Console.Write("Segundo Apellido (Sin espacios ni números): ");
            nuevoUsuario.SegundoApellido = Console.ReadLine();

            Console.Write("Correo Electrónico: ");
            nuevoUsuario.CorreoElectronico = Console.ReadLine();

            Console.Write("Nombre de Usuario (Para el login): ");
            string usuarioPlano = Console.ReadLine();
            nuevoUsuario.Usuario = Seguridad.Encriptar(usuarioPlano); // Se encripta inmediatamente

            Console.Write("Contraseña (14 caracteres, 1 mayús, 1 minús, 1 número, 1 especial): ");
            string contrasenaPlana = Console.ReadLine();
            nuevoUsuario.Contrasena = Seguridad.Encriptar(contrasenaPlana); // Se encripta inmediatamente

            Console.Write("Tipo de usuario (1 = Empleados, 2 = Clientes): ");
            if (int.TryParse(Console.ReadLine(), out int tipoSeleccionado))
            {
                nuevoUsuario.Tipo = tipoSeleccionado;
            }
            else
            {
                nuevoUsuario.Tipo = 0; // Valor inválido intencional para que el WCF lo rechace si escribe letras
            }

            Console.WriteLine("\nEnviando datos al Web Service...");
            var respuesta = cliente.CrearUsuario(nuevoUsuario);

            Console.WriteLine($"\nRESULTADO WCF -> {respuesta.Resultado}");
            Console.WriteLine($"MENSAJE WCF   -> {respuesta.Mensaje}");
        }

        // ==========================================
        // OPCIÓN 2: AUTENTICAR USUARIO (LOGIN)
        // ==========================================
        static void MenuAutenticarUsuario(AutenticacionServiceClient cliente)
        {
            Console.Clear();
            Console.WriteLine("--- AUTENTICAR USUARIO ---");

            Console.Write("Ingresa tu Nombre de Usuario: ");
            string usuarioPlano = Console.ReadLine();

            Console.Write("Ingresa tu Contraseña: ");
            string contrasenaPlana = Console.ReadLine();

            Console.Write("Tipo de usuario (1 = Empleados, 2 = Clientes): ");
            int.TryParse(Console.ReadLine(), out int tipoUsuario);

            // Encriptamos antes de enviar al WCF
            string usuarioEncriptado = Seguridad.Encriptar(usuarioPlano);
            string contrasenaEncriptada = Seguridad.Encriptar(contrasenaPlana);

            Console.WriteLine("\nVerificando credenciales...");
            var respuesta = cliente.AutenticarUsuario(usuarioEncriptado, contrasenaEncriptada, tipoUsuario);

            Console.WriteLine($"\nRESULTADO WCF -> {respuesta.Resultado}");
            Console.WriteLine($"MENSAJE WCF   -> {respuesta.Mensaje}");
        }

        // ==========================================
        // OPCIÓN 3: MODIFICAR USUARIO
        // ==========================================
        static void MenuModificarUsuario(AutenticacionServiceClient cliente)
        {
            Console.Clear();
            Console.WriteLine("--- MODIFICAR USUARIO ---");
            Console.WriteLine("(La identificación no se puede cambiar, se usa para buscar al usuario)");

            UsuarioModelo usuarioModificado = new UsuarioModelo();

            Console.Write("Identificación del usuario a modificar: ");
            usuarioModificado.Identificacion = Console.ReadLine();

            Console.Write("Nuevo Nombre: ");
            usuarioModificado.Nombre = Console.ReadLine();

            Console.Write("Nuevo Primer Apellido: ");
            usuarioModificado.PrimerApellido = Console.ReadLine();

            Console.Write("Nuevo Segundo Apellido: ");
            usuarioModificado.SegundoApellido = Console.ReadLine();

            Console.Write("Nuevo Correo Electrónico: ");
            usuarioModificado.CorreoElectronico = Console.ReadLine();

            Console.Write("Nuevo Nombre de Usuario: ");
            string usuarioPlano = Console.ReadLine();
            usuarioModificado.Usuario = Seguridad.Encriptar(usuarioPlano);

            Console.Write("Nueva Contraseña: ");
            string contrasenaPlana = Console.ReadLine();
            usuarioModificado.Contrasena = Seguridad.Encriptar(contrasenaPlana);

            Console.WriteLine("\nEnviando actualización al Web Service...");
            var respuesta = cliente.ModificarUsuario(usuarioModificado);

            Console.WriteLine($"\nRESULTADO WCF -> {respuesta.Resultado}");
            Console.WriteLine($"MENSAJE WCF   -> {respuesta.Mensaje}");
        }

        // ==========================================
        // OPCIÓN 4: CAMBIAR ESTADO
        // ==========================================
        static void MenuCambiarEstado(AutenticacionServiceClient cliente)
        {
            Console.Clear();
            Console.WriteLine("--- CAMBIAR ESTADO DE USUARIO ---");

            Console.Write("Identificación del usuario: ");
            string identificacion = Console.ReadLine();

            Console.Write("Nuevo Estado ('activo' o 'inactivo'): ");
            string nuevoEstado = Console.ReadLine();

            Console.WriteLine("\nActualizando estado...");
            var respuesta = cliente.CambiarEstadoUsuario(identificacion, nuevoEstado);

            Console.WriteLine($"\nRESULTADO WCF -> {respuesta.Resultado}");
            Console.WriteLine($"MENSAJE WCF   -> {respuesta.Mensaje}");
        }
    }
}