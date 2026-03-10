using MongoDB.Driver;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace ServiciosBancariosWCF
{
    public static class MongoDbContext
    {
        private static IMongoDatabase database;

        public static IMongoDatabase GetDatabase()
        {
            if (database == null)
            {
                // Cambia esta cadena si tu MongoDB tiene usuario/contraseña o está en otro puerto
                var client = new MongoClient("mongodb://localhost:27017");
                database = client.GetDatabase("BancoABC");
            }
            return database;
        }

        public static IMongoCollection<UsuarioModelo> Usuarios => GetDatabase().GetCollection<UsuarioModelo>("Usuarios");
    }
}