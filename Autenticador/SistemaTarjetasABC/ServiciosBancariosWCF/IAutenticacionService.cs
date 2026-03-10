using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.ServiceModel;
using System.Text;
using System.Threading.Tasks;

namespace ServiciosBancariosWCF
{
    [DataContract]
    public class RespuestaBase
    {
        [DataMember]
        public bool Resultado { get; set; }

        [DataMember]
        public string Mensaje { get; set; }
    }

    [ServiceContract]
    public interface IAutenticacionService
    {
        // WS_AUTENTICADOR1
        [OperationContract]
        RespuestaBase AutenticarUsuario(string usuarioEncriptado, string contrasenaEncriptada, int tipoUsuario);

        // WS_AUTENTICACION2
        [OperationContract]
        RespuestaBase CrearUsuario(UsuarioModelo nuevoUsuario);

        [OperationContract]
        RespuestaBase ModificarUsuario(UsuarioModelo usuarioModificado);

        [OperationContract]
        RespuestaBase CambiarEstadoUsuario(string identificacion, string nuevoEstado);
    }
}
