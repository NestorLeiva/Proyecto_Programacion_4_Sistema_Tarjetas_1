import pymssql
from datetime import datetime

print("🔍 Testeando SQL Server del CORE BANCARIO...")

try:
    # EXACTAMENTE igual que tu Java
    conn = pymssql.connect(
        host='localhost',
        port=1433,
        user='nestor_p6',
        password='12345678',
        database='core_bancario'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cuenta")
    cuentas = cursor.fetchone()[0]
    
    print(f"✅ ¡CONEXIÓN EXITOSA!")
    print(f"📊 {cuentas} cuentas encontradas")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("🔧 Verifica: SQL Server corriendo, puerto 1433, usuario rodri")
