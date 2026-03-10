using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace ServiciosBancariosWCF
{
    public class UsuarioModelo
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; }
        public string Identificacion { get; set; }
        public string Nombre { get; set; }
        public string PrimerApellido { get; set; }
        public string SegundoApellido { get; set; }
        public string CorreoElectronico { get; set; }
        public string Usuario { get; set; }
        public string Contrasena { get; set; }
        public string Estado { get; set; } // "activo" o "inactivo"
        public int Tipo { get; set; } // 1 para empleados, 2 para clientes
    }
}