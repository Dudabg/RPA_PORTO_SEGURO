from navegador import criar_navegador
from automacao import PortoAutomacao
from config import Config
import time


def main():

    print("🚀 Iniciando monitoramento contínuo...")
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

                    # 🔥 CORREÇÃO AQUI
                    tem_pedido = automacao.acessar_atender_pedido()

                    if tem_pedido:
                        automacao.capturar_dados_pedido()
                    else:
                        print("➡️ Indo para o próximo CPF...")

                except Exception as e:
                    print(f"❌ Erro no CPF {conta['usuario']}: {e}")

                finally:
                    driver.quit()
                    print("Navegador fechado.")

                time.sleep(5)

            print(f"\n⏳ Aguardando {Config.TEMPO_ESPERA} segundos para próximo ciclo...\n")
            time.sleep(Config.TEMPO_ESPERA)

    except KeyboardInterrupt:
        print("\n🛑 Monitoramento encerrado manualmente.")

    input("Pressione ENTER para encerrar...")


if __name__ == "__main__":
    main()