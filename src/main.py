from navegador import criar_navegador
from automacao import PortoAutomacao


def main():
    driver = criar_navegador()
    automacao = PortoAutomacao(driver)

    automacao.acessar_portal()
    automacao.realizar_login()

    input("Pressione ENTER para encerrar...")

    driver.quit()


if __name__ == "__main__":
    main()