import oracledb

# 🔥 Ativando modo THICK
oracledb.init_oracle_client(
    lib_dir=r"C:\Oracle\19c\bin"
)

usuario = "rmp"
senha = "rmp423b"
dsn = "engate.greal.com.br:1521/desenv.rmp.com.br"

try:
    conexao = oracledb.connect(
        user=usuario,
        password=senha,
        dsn=dsn
    )

    print("✅ Conectado com sucesso!")

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT 
        sys_context('USERENV','DB_NAME'),
        sys_context('USERENV','SERVICE_NAME'),
        sys_context('USERENV','SERVER_HOST')
    FROM dual
""")

    for linha in cursor:
        print("DB_NAME:", linha[0])
        print("SERVICE_NAME:", linha[1])
        print("SERVER_HOST:", linha[2])

except Exception as e:
    print("❌ Erro:", e)