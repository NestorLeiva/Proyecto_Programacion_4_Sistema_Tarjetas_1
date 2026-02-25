using System;
using System.Net.Sockets;
using System.Text;

namespace SimuladorATM
{
    class Program
    {
        static string ipServidor = "127.0.0.1";
        static int puerto = 5001;
        static int idCajero = 1;

        static void Main(string[] args)
        {
            Console.Clear();
            Console.WriteLine("=== CONFIGURACIÓN INICIAL DEL ATM ===");
            Console.Write("Ingrese el ID de este Cajero (debe existir en DB MySQL): ");
            int.TryParse(Console.ReadLine(), out idCajero);

            while (true)
            {
                Console.Clear();
                Console.WriteLine("======================================");
                Console.WriteLine($"   ATM ACTIVO - CAJERO ID: {idCajero}");
                Console.WriteLine("======================================");
                Console.WriteLine("1. Consultar Saldo");
                Console.WriteLine("2. Retirar Efectivo");
                Console.WriteLine("3. Cambiar PIN");
                Console.WriteLine("4. Salir");
                Console.Write("\nSeleccione una opción: ");

                string opcion = Console.ReadLine();
                switch (opcion)
                {
                    case "1": ProcesarConsulta(); break;
                    case "2": ProcesarRetiro(); break;
                    case "3": ProcesarCambioPin(); break;
                    case "4": return;
                }
                Console.WriteLine("\nPresione cualquier tecla para continuar...");
                Console.ReadKey();
            }
        }

        static void ProcesarConsulta()
        {
            Console.Write("Ingrese tarjeta (16 dígitos): ");
            string tarjeta = Console.ReadLine().Replace("-", "").PadRight(16).Substring(0, 16);
            Console.Write("Ingrese PIN: ");
            string pin = Console.ReadLine().PadRight(4).Substring(0, 4);

            // Trama: Tipo(1) + Tarjeta(16) + Monto(8) + PIN(4) + Cajero(4)
            string trama = $"2{tarjeta}00000000{pin}{idCajero:D4}";
            Comunicar(trama);
        }

        static void ProcesarRetiro()
        {
            Console.Write("Ingrese tarjeta: ");
            string tarjeta = Console.ReadLine().Replace("-", "").PadRight(16).Substring(0, 16);

            Console.Write("Monto a retirar (ej: 5000): ");
            string montoInput = Console.ReadLine();

            // Convertimos a entero y luego a string de 8 posiciones con ceros a la izquierda
            // Así, si el usuario pone "5000", se envía "00005000"
            int montoInt = 0;
            int.TryParse(montoInput, out montoInt);
            string monto = montoInt.ToString().PadLeft(8, '0');

            Console.Write("Ingrese PIN: ");
            string pin = Console.ReadLine().Trim().PadRight(4).Substring(0, 4);

            // Trama: Tipo(1) + Tarjeta(16) + Monto(8) + PIN(4) + Cajero(4)
            string trama = $"1{tarjeta}{monto}{pin}{idCajero:D4}";
            Comunicar(trama);
        }

        static void ProcesarCambioPin()
        {
            Console.Write("Tarjeta: ");
            string tarjeta = Console.ReadLine().Replace("-", "");
            Console.Write("PIN Actual: ");
            string actual = Console.ReadLine();
            Console.Write("PIN Nuevo: ");
            string nuevo = Console.ReadLine();

            // JSON Manual para evitar errores de librería
            string json = "{" +
                $"\"tipo\": \"cambio_pin\"," +
                $"\"numero_tarjeta\": \"{tarjeta}\"," +
                $"\"pin_actual\": \"{actual}\"," +
                $"\"pin_nuevo\": \"{nuevo}\"," +
                $"\"id_cajero\": {idCajero}" +
            "}";
            Comunicar(json);
        }

        static void Comunicar(string mensaje)
        {
            try
            {
                using (TcpClient client = new TcpClient(ipServidor, puerto))
                using (NetworkStream stream = client.GetStream())
                {
                    byte[] data = Encoding.UTF8.GetBytes(mensaje);
                    stream.Write(data, 0, data.Length);
                    byte[] responseData = new byte[1024];
                    int bytes = stream.Read(responseData, 0, responseData.Length);
                    Console.WriteLine("\n--- RESPUESTA ---");
                    Console.WriteLine(Encoding.UTF8.GetString(responseData, 0, bytes));
                }
            }
            catch (Exception e) { Console.WriteLine("Error: " + e.Message); }
        }
    }
}