using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace SimuladorCliente
{
    public static class Seguridad
    {
        private static readonly string ClaveSecreta = "Banc0ABC_S1st3m4T4rj3t4s_2026!!!";
        private static readonly string VectorInicializacion = "1234567890123456";

        public static string Encriptar(string textoPlano)
        {
            if (string.IsNullOrEmpty(textoPlano)) return textoPlano;
            byte[] arregloClave = Encoding.UTF8.GetBytes(ClaveSecreta);
            byte[] arregloIV = Encoding.UTF8.GetBytes(VectorInicializacion);
            byte[] arregloTextoPlano = Encoding.UTF8.GetBytes(textoPlano);

            using (Aes aesAlg = Aes.Create())
            {
                aesAlg.Key = arregloClave;
                aesAlg.IV = arregloIV;
                ICryptoTransform encryptor = aesAlg.CreateEncryptor(aesAlg.Key, aesAlg.IV);
                using (MemoryStream msEncrypt = new MemoryStream())
                {
                    using (CryptoStream csEncrypt = new CryptoStream(msEncrypt, encryptor, CryptoStreamMode.Write))
                    {
                        csEncrypt.Write(arregloTextoPlano, 0, arregloTextoPlano.Length);
                        csEncrypt.FlushFinalBlock();
                    }
                    return Convert.ToBase64String(msEncrypt.ToArray());
                }
            }
        }

        public static string Desencriptar(string textoEncriptado)
        {
            if (string.IsNullOrEmpty(textoEncriptado)) return textoEncriptado;
            byte[] arregloClave = Encoding.UTF8.GetBytes(ClaveSecreta);
            byte[] arregloIV = Encoding.UTF8.GetBytes(VectorInicializacion);
            byte[] arregloTextoCifrado = Convert.FromBase64String(textoEncriptado);

            using (Aes aesAlg = Aes.Create())
            {
                aesAlg.Key = arregloClave;
                aesAlg.IV = arregloIV;
                ICryptoTransform decryptor = aesAlg.CreateDecryptor(aesAlg.Key, aesAlg.IV);
                using (MemoryStream msDecrypt = new MemoryStream(arregloTextoCifrado))
                {
                    using (CryptoStream csDecrypt = new CryptoStream(msDecrypt, decryptor, CryptoStreamMode.Read))
                    {
                        using (StreamReader srDecrypt = new StreamReader(csDecrypt))
                        {
                            return srDecrypt.ReadToEnd();
                        }
                    }
                }
            }
        }
    }
}
