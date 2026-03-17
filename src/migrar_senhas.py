from database import criar_conexao
from crypto import criptografar

def migrar_senhas():

    conexao = criar_conexao()
    cursor  = conexao.cursor()

    try:
        cursor.execute("""
            SELECT ID_CREDENTIAL, PASSWORD
              FROM RMP.RPA_CREDENTIALS
             ORDER BY ID_CREDENTIAL
        """)
        rows = cursor.fetchall()

        print(f"🔑 {len(rows)} credencial(is) encontrada(s) para migrar.\n")

        for id_cred, senha_atual in rows:

            # Evita criptografar duas vezes
            if senha_atual.startswith("gA"):
                print(f"⏭️  ID={id_cred} já está criptografada. Pulando.")
                continue

            senha_criptografada = criptografar(senha_atual)

            cursor.execute("""
                UPDATE RMP.RPA_CREDENTIALS
                   SET PASSWORD   = :senha,
                       UPDATED_AT = CURRENT_TIMESTAMP,
                       UPDATED_BY = 'MIGRATION'
                 WHERE ID_CREDENTIAL = :id
            """, {"senha": senha_criptografada, "id": id_cred})

            print(f"✅ ID={id_cred} | senha criptografada com sucesso.")

        conexao.commit()
        print("\n✅ Migração concluída!")

    except Exception as e:
        conexao.rollback()
        print(f"\n❌ Erro durante migração: {e}")
        raise

    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    migrar_senhas()