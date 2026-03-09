import oracledb

# Inicializa modo THICK (usa Oracle Client instalado)
oracledb.init_oracle_client(
    lib_dir=r"C:\Oracle\19c\bin"
)


def criar_conexao():
    try:
        conexao = oracledb.connect(
            user="rmp",
            password="rmp423b",
            dsn="engate.greal.com.br:1521/desenv.rmp.com.br"
        )

        print("✅ Conexão com banco criada.")
        return conexao

    except Exception as e:
        print("❌ Erro ao conectar no banco:", e)
        raise