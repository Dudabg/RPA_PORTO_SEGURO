from database import criar_conexao
from crypto import criptografar


def trocar_senha():

    print("🔑 TROCA DE SENHA - RPA CREDENTIALS\n")

    # ── Solicita os dados 
    cpf        = input("Digite o CPF (USERNAME): ").strip()
    nova_senha = input("Digite a nova senha:     ").strip()

    if not cpf or not nova_senha:
        print("❌ CPF e senha são obrigatórios.")
        return

    # ── Conecta no banco ─
    conexao = criar_conexao()
    cursor  = conexao.cursor()

    try:
        # Verifica se o CPF existe
        cursor.execute("""
            SELECT ID_CREDENTIAL, USERNAME, ACTIVE
              FROM RMP.RPA_CREDENTIALS
             WHERE USERNAME = :cpf
        """, {"cpf": cpf})

        row = cursor.fetchone()

        if not row:
            print(f"❌ CPF '{cpf}' não encontrado no banco.")
            return

        id_cred, username, active = row
        print(f"\n✅ CPF encontrado → ID={id_cred} | ACTIVE={active}")

        # Criptografa a nova senha
        senha_criptografada = criptografar(nova_senha)

        # Atualiza no banco
        cursor.execute("""
            UPDATE RMP.RPA_CREDENTIALS
               SET PASSWORD   = :senha,
                   UPDATED_AT = CURRENT_TIMESTAMP,
                   UPDATED_BY = 'SCRIPT_TROCA_SENHA'
             WHERE USERNAME = :cpf
        """, {"senha": senha_criptografada, "cpf": cpf})

        conexao.commit()
        print(f"✅ Senha do CPF {cpf} atualizada e criptografada com sucesso!")

    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro ao trocar senha: {e}")
        raise

    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    trocar_senha()