import oracledb
from crypto import descriptografar

oracledb.init_oracle_client(lib_dir=r"C:\Oracle\19c\bin")

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
    """Verifica se conexão ainda está viva. Reconecta se necessário."""
    try:
        conexao.ping()
        return conexao
    except Exception:
        print("⚠️ Conexão perdida. Reconectando...")
        return criar_conexao()


def buscar_credenciais(conexao, bot_name):
    """
    Busca credenciais ativas do banco e descriptografa as senhas.
    Retorna lista de dicts: [{"username": "cpf", "password": "senha"}, ...]
    """
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
            cred["password"] = descriptografar(cred["password"])  # ✅ descriptografa antes de usar
            credenciais.append(cred)

        return credenciais

    finally:
        cursor.close()