import oracledb
import os
from crypto import descriptografar

rodando_no_docker = os.path.exists("/.dockerenv")

if rodando_no_docker:
    oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_19_19")
else:
    oracledb.init_oracle_client(lib_dir=r"C:\Oracle\19c\bin")

oracledb.defaults.fetch_lobs = False

_CONFIG = {
    "user":     "rmp",
    "password": "rmp423b",
    "dsn":      "engate.greal.com.br:1521/desenv.rmp.com.br"
}


def criar_conexao():
    try:
        conexao = oracledb.connect(**_CONFIG)
        print("✅ Conexão com banco criada.")
        return conexao
    except Exception as e:
        print("❌ Erro ao conectar no banco:", e)
        raise


def garantir_conexao(conexao):
    try:
        conexao.ping()
        return conexao
    except Exception:
        print("⚠️ Conexão perdida. Reconectando...")
        return criar_conexao()


def buscar_credenciais(conexao, bot_name):
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            SELECT USERNAME, PASSWORD
              FROM RMP.RPA_CREDENTIALS
             WHERE BOT_NAME = :bot_name
               AND ACTIVE   = 'Y'
             ORDER BY ID_CREDENTIAL
        """, {"bot_name": bot_name})

        credenciais = []
        colunas = [d[0].lower() for d in cursor.description]

        for row in cursor.fetchall():
            cred = dict(zip(colunas, row))
            cred["password"] = descriptografar(cred["password"])
            credenciais.append(cred)

        return credenciais

    finally:
        cursor.close()