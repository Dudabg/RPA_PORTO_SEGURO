from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import Config
import time


class PortoAutomacao:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 60)  # aumentei para 60s

    # -------------------------------------------------
    # 1️⃣ ACESSAR PORTAL
    # -------------------------------------------------
    def acessar_portal(self):
        print("Acessando o portal...")
        self.driver.get(Config.PORTO_URL)

        # Espera a página estabilizar
        time.sleep(5)

    # -------------------------------------------------
    # 2️⃣ LOGIN
    # -------------------------------------------------
    def realizar_login(self):
        print("Realizando login...")

        # Espera mais tempo antes de preencher
        time.sleep(5)

        # CPF
        campo_cpf = self.wait.until(
            EC.presence_of_element_located((By.ID, "inputCPF"))
        )
        campo_cpf.clear()
        campo_cpf.send_keys(Config.PORTO_USER)

        # Senha
        campo_senha = self.wait.until(
            EC.presence_of_element_located((By.ID, "inputPassword"))
        )
        campo_senha.clear()
        campo_senha.send_keys(Config.PORTO_PASSWORD)

        time.sleep(2)

        # Botão ENTRAR
        botao_entrar = self.wait.until(
            EC.presence_of_element_located((By.ID, "j_id19"))
        )

        self.driver.execute_script("arguments[0].click();", botao_entrar)

        print("Login enviado, aguardando carregamento...")

        # Espera a nova página carregar totalmente
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'ATENDER PEDIDO')]")
            )
        )

        print("Login concluído!")

    # -------------------------------------------------
    # 3️⃣ ATENDER PEDIDO
    # -------------------------------------------------
    def acessar_atender_pedido(self):
        print("Acessando ATENDER PEDIDO...")

        time.sleep(3)

        elemento = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'ATENDER PEDIDO')]")
            )
        )

        self.driver.execute_script("arguments[0].click();", elemento)

        print("Clique realizado, aguardando tela do pedido...")

        # Espera carregar tela do pedido
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'Número Sinistro')]")
            )
        )

        print("Tela do pedido carregada!")

    # -------------------------------------------------
    # 4️⃣ CAPTURAR DADOS
    # -------------------------------------------------
    def capturar_dados_pedido(self):
        print("Capturando dados do pedido...")

        # espera o bloco carregar
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[normalize-space()='Número Sinistro']")
            )
        )

        def pegar_valor(titulo):
            try:
                elemento = self.driver.find_element(
                    By.XPATH,
                    f"//span[normalize-space()='{titulo}']"
                    f"/parent::td/parent::tr"
                    f"/following-sibling::tr[1]"
                    f"//span[@class='text_common']"
                )
                return elemento.text.strip()
            except:
                return "Não encontrado"

        dados = {
            "numero_sinistro": pegar_valor("Número Sinistro"),
            "data_solicitacao": pegar_valor("Data da Solicitação"),
            "numero_pedido": pegar_valor("Número do Pedido"),
            "data_pedido": pegar_valor("Data do Pedido"),
            "marca": pegar_valor("Marca"),
            "veiculo": pegar_valor("Veículo"),
            "modelo": pegar_valor("Modelo"),
            "placa": pegar_valor("Placa"),
            "chassi": pegar_valor("Chassi"),
            "ano": pegar_valor("Ano"),
        }

        # criticidade (já está certo no seu HTML)
        try:
            criticidade = self.driver.find_element(
                By.XPATH,
                "//span[contains(@class,'progress-bar-status-tarefa-text')]"
            ).text.strip()
        except:
            criticidade = "Não encontrado"

        dados["criticidade"] = criticidade

        print("\nDADOS CAPTURADOS:")
        for chave, valor in dados.items():
            print(f"{chave}: {valor}")

        return dados