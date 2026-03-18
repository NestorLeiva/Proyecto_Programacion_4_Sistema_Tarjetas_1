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

        [BsonElement("identificacion")]
        public string Identificacion { get; set; }

        [BsonElement("nombre")]
        public string Nombre { get; set; }

        [BsonElement("primerApellido")]
        public string PrimerApellido { get; set; }

        [BsonElement("segundoApellido")]
        public string SegundoApellido { get; set; }

        [BsonElement("correoElectronico")]
        public string CorreoElectronico { get; set; }

        [BsonElement("usuario")]
        public string Usuario { get; set; }

        [BsonElement("contrasena")]
        public string Contrasena { get; set; }

        [BsonElement("estado")]
        public string Estado { get; set; } // "activo" o "inactivo"

        [BsonElement("tipo")]
        public int Tipo { get; set; } // 1 para empleados, 2 para clientes
    }
}