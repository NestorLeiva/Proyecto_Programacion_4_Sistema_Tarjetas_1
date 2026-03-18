using MongoDB.Driver;
using System;
using System.Linq;
using System.Runtime.Serialization;
using System.ServiceModel;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using System.IO;

namespace ServiciosBancariosWCF
{
    public class AutenticacionService2 : IAutenticacionService
    {
        // BITACORA UNIVERSAL
        private void RegistrarBitacora(string solicitud, string respuesta)
        {
            try
            {
                var registro = new
                {
                    Fecha = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                    SolicitudRecibida = solicitud,
                    RespuestaGenerada = respuesta
                };

                string json = JsonConvert.SerializeObject(registro);

                // Ruta base de la aplicación
                string rutaBase = AppDomain.CurrentDomain.BaseDirectory;

                // Carpeta Logs dentro del proyecto
                string carpetaLogs = Path.Combine(rutaBase, "Logs");

                // Crear carpeta si no existe
                if (!Directory.Exists(carpetaLogs))
                {
                    Directory.CreateDirectory(carpetaLogs);
                }

                // Archivo de log
                string archivoLog = Path.Combine(carpetaLogs, "bitacora.txt");

                // Guardar registro
                File.AppendAllText(archivoLog, json + Environment.NewLine);
            }
            catch
            {
                // Evita que un error en log rompa el servicio
            }
        }

        public bool ValidarDatosUsuario(UsuarioModelo usuario)
        {
            // 1. Validar que no haya campos vacíos
            if (string.IsNullOrWhiteSpace(usuario.Nombre) ||
                string.IsNullOrWhiteSpace(usuario.PrimerApellido) ||
                string.IsNullOrWhiteSpace(usuario.SegundoApellido) ||
                string.IsNullOrWhiteSpace(usuario.Identificacion) ||
                string.IsNullOrWhiteSpace(usuario.Usuario))
            {
                return false;
            }

            // 2. Validar nombres y apellidos
            string patronNombres = @"^[a-zA-ZáéíóúÁÉÍÓÚñÑ]+$";

            if (!Regex.IsMatch(usuario.Nombre, patronNombres) ||
                !Regex.IsMatch(usuario.PrimerApellido, patronNombres) ||
                !Regex.IsMatch(usuario.SegundoApellido, patronNombres))
            {
                return false;
            }

            // 3. Validar correo
            string patronCorreo = @"^[^@\s]+@[^@\s]+\.[^@\s]+$";

            if (!Regex.IsMatch(usuario.CorreoElectronico, patronCorreo))
            {
                return false;
            }

            // 4. Validar contraseña
            string patronContrasena = @"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{14}$";

            if (!Regex.IsMatch(usuario.Contrasena, patronContrasena))
            {
                return false;
            }

            // 5. Validar tipo
            if (usuario.Tipo != 1 && usuario.Tipo != 2)
            {
                return false;
            }

            return true;
        }

        // AUTENTICADOR 1
        public RespuestaBase AutenticarUsuario(string usuarioEncriptado, string contrasenaEncriptada, int tipoUsuario)
        {
            var respuesta = new RespuestaBase();

            // Buscamos que coincida usuario, contraseña, tipo Y que el ESTADO sea "activo"
            var usuarioDb = MongoDbContext.Usuarios.Find(u =>
                u.Usuario == usuarioEncriptado &&
                u.Contrasena == contrasenaEncriptada &&
                u.Tipo == tipoUsuario &&
                u.Estado == "activo" // <-- LA RESTRICCIÓN DE ESTADO
            ).FirstOrDefault();

            if (usuarioDb != null)
            {
                respuesta.Resultado = true;
                respuesta.Mensaje = "Exitoso";
            }
            else
            {
                respuesta.Resultado = false;
                respuesta.Mensaje = "Usuario y/o contraseña incorrectos.";
            }

            RegistrarBitacora($"Autenticar: {usuarioEncriptado}", respuesta.Mensaje);
            return respuesta;
        }

        // AUTENTICACION 2 - CREAR USUARIO
        public RespuestaBase CrearUsuario(UsuarioModelo nuevoUsuario)
        {
            var respuesta = new RespuestaBase();

            // 1. Desencriptamos temporalmente para poder validar el formato original (Regex)
            string usuarioPlano = Seguridad.Desencriptar(nuevoUsuario.Usuario);
            string contrasenaPlana = Seguridad.Desencriptar(nuevoUsuario.Contrasena);

            // Creamos una copia temporal para la validación
            var usuarioParaValidar = new UsuarioModelo
            {
                Nombre = nuevoUsuario.Nombre,
                PrimerApellido = nuevoUsuario.PrimerApellido,
                SegundoApellido = nuevoUsuario.SegundoApellido,
                Identificacion = nuevoUsuario.Identificacion,
                CorreoElectronico = nuevoUsuario.CorreoElectronico,
                Tipo = nuevoUsuario.Tipo,
                Usuario = usuarioPlano, // Usamos el desencriptado para validar
                Contrasena = contrasenaPlana // Usamos el desencriptado para validar (los 14 caracteres)
            };

            // 2. Aplicamos la validación estricta
            if (!ValidarDatosUsuario(usuarioParaValidar))
            {
                respuesta.Resultado = false;
                respuesta.Mensaje = "Usuario ya existe o datos incorrectos o incompletos.";
                RegistrarBitacora($"Crear Usuario: {JsonConvert.SerializeObject(nuevoUsuario)}", respuesta.Mensaje);
                return respuesta;
            }

            // 3. Estado por defecto y validación de existencia en BD
            nuevoUsuario.Estado = "activo";
            var existe = MongoDbContext.Usuarios.Find(u => u.Identificacion == nuevoUsuario.Identificacion).Any();

            if (existe)
            {
                respuesta.Resultado = false;
                respuesta.Mensaje = "El usuario ya existe.";
            }
            else
            {
                // Insertamos el 'nuevoUsuario' original, que ya trae el Usuario y Contrasena encriptados
                MongoDbContext.Usuarios.InsertOne(nuevoUsuario);
                respuesta.Resultado = true;
                respuesta.Mensaje = "Exitoso";
            }

            RegistrarBitacora($"Crear Usuario: {JsonConvert.SerializeObject(nuevoUsuario.Identificacion)}", respuesta.Mensaje);
            return respuesta;
        }

        public RespuestaBase ModificarUsuario(UsuarioModelo usuarioModificado)
        {
            var respuesta = new RespuestaBase();

            // 1. Desencriptamos temporalmente para poder validar con el Regex
            string usuarioPlano = Seguridad.Desencriptar(usuarioModificado.Usuario);
            string contrasenaPlana = Seguridad.Desencriptar(usuarioModificado.Contrasena);

            var usuarioParaValidar = new UsuarioModelo
            {
                Nombre = usuarioModificado.Nombre,
                PrimerApellido = usuarioModificado.PrimerApellido,
                SegundoApellido = usuarioModificado.SegundoApellido,
                Identificacion = usuarioModificado.Identificacion,
                CorreoElectronico = usuarioModificado.CorreoElectronico,
                Tipo = 1, // Tipo 1 por defecto para pasar el Regex, ya que no se suele modificar en este método
                Usuario = usuarioPlano,
                Contrasena = contrasenaPlana
            };

            // 2. Validamos el formato
            if (!ValidarDatosUsuario(usuarioParaValidar))
            {
                respuesta.Resultado = false;
                respuesta.Mensaje = "Usuario no existe o datos incorrectos o incompletos.";
                RegistrarBitacora($"Modificar - Solicitud: {JsonConvert.SerializeObject(usuarioModificado)}", respuesta.Mensaje);
                return respuesta;
            }

            // 3. Verificamos que el usuario exista en Mongo (usando la Identificacion como llave primaria)
            var filtro = Builders<UsuarioModelo>.Filter.Eq(u => u.Identificacion, usuarioModificado.Identificacion);
            var usuarioExistente = MongoDbContext.Usuarios.Find(filtro).FirstOrDefault();

            if (usuarioExistente == null)
            {
                respuesta.Resultado = false;
                respuesta.Mensaje = "Usuario no existe o datos incorrectos o incompletos.";
            }
            else
            {
                // 4. Actualizamos solo los campos permitidos (La llave primaria "Identificacion" no se toca)
                var actualizacion = Builders<UsuarioModelo>.Update
                    .Set(u => u.Nombre, usuarioModificado.Nombre)
                    .Set(u => u.PrimerApellido, usuarioModificado.PrimerApellido)
                    .Set(u => u.SegundoApellido, usuarioModificado.SegundoApellido)
                    .Set(u => u.CorreoElectronico, usuarioModificado.CorreoElectronico)
                    .Set(u => u.Usuario, usuarioModificado.Usuario) // Se guarda la versión que ya viene encriptada
                    .Set(u => u.Contrasena, usuarioModificado.Contrasena); // Se guarda la versión que ya viene encriptada

                MongoDbContext.Usuarios.UpdateOne(filtro, actualizacion);

                respuesta.Resultado = true;
                respuesta.Mensaje = "Exitoso";
            }

            RegistrarBitacora($"Modificar - Solicitud: {JsonConvert.SerializeObject(usuarioModificado)}", respuesta.Mensaje);
            return respuesta;
        }

        public RespuestaBase CambiarEstadoUsuario(string identificacion, string nuevoEstado)
        {
            var respuesta = new RespuestaBase();

            // 1. Validar que el estado enviado sea válido
            if (nuevoEstado != "activo" && nuevoEstado != "inactivo")
            {
                respuesta.Resultado = false;
                respuesta.Mensaje = "Usuario no existe o datos incorrectos.";
                RegistrarBitacora($"Cambio Estado a {nuevoEstado} para ID: {identificacion}", respuesta.Mensaje);
                return respuesta;
            }

            // 2. Buscar si existe el usuario
            var filtro = Builders<UsuarioModelo>.Filter.Eq(u => u.Identificacion, identificacion);
            var usuarioExistente = MongoDbContext.Usuarios.Find(filtro).FirstOrDefault();

            if (usuarioExistente == null)
            {
                respuesta.Resultado = false;
                respuesta.Mensaje = "Usuario no existe o datos incorrectos.";
            }
            else
            {
                // 3. Si existe y el estado es correcto, lo actualizamos
                var actualizacion = Builders<UsuarioModelo>.Update.Set(u => u.Estado, nuevoEstado);
                MongoDbContext.Usuarios.UpdateOne(filtro, actualizacion);

                respuesta.Resultado = true;
                respuesta.Mensaje = "Exitoso";
            }

            RegistrarBitacora($"Cambio Estado a {nuevoEstado} para ID: {identificacion}", respuesta.Mensaje);
            return respuesta;
        }
    }
}