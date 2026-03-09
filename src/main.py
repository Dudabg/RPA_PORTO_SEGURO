from navegador import criar_navegador
from logger_rpa import iniciar_execucao, registrar_erro_tecnico, finalizar_execucao
from database import criar_conexao
from automacao import PortoAutomacao
from config import Config
import time


def main():

    print("🚀 Iniciando monitoramento contínuo...")

    # Conecta no banco
    conexao = criar_conexao()

    # Registra execução do robô
    id_execucao = iniciar_execucao(conexao, "RPA_PORTO")

    print(f"📝 Execução registrada no banco. ID: {id_execucao}")
    print("Para encerrar o robô, pressione CTRL + C\n")

    try:

        while True:

            print("\n==============================")
            print("🔄 NOVO CICLO DE VERIFICAÇÃO")
            print("==============================\n")

            for conta in Config.CNPJS:

                print(f"\n🔎 Verificando CPF: {conta['usuario']}")

                driver = criar_navegador()
                automacao = PortoAutomacao(driver)

                try:

                    automacao.acessar_portal()

                    automacao.realizar_login(
                        conta["usuario"],
                        conta["senha"]
                    )

                    tem_pedido = automacao.acessar_atender_pedido()

                    if tem_pedido:
                        automacao.capturar_dados_pedido()
                    else:
                        print("➡️ Nenhum pedido encontrado.")

                except Exception as e:

                    print(f"❌ Erro no CPF {conta['usuario']}: {e}")

                    # Registra erro no banco
                    registrar_erro_tecnico(
                        conexao,
                        id_execucao,
                        "ERRO_AUTOMACAO",
                        str(e)
                    )

                finally:

                    driver.quit()
                    print("Navegador fechado.")

                time.sleep(5)

            print(f"\n⏳ Aguardando {Config.TEMPO_ESPERA} segundos para próximo ciclo...\n")

            time.sleep(Config.TEMPO_ESPERA)

    except KeyboardInterrupt:

        print("\n🛑 Monitoramento encerrado manualmente.")

    finally:

        # Finaliza execução no banco
        finalizar_execucao(conexao, id_execucao, "RPA_PORTO")

        conexao.close()

        print("🛑 Execução do robô finalizada.")
        print("🔌 Conexão com banco encerrada.")


if __name__ == "__main__":
    main()