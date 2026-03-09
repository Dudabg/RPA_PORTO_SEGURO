from logger_rpa import iniciar_execucao
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import Config
from notificador_email import NotificadorEmail
import time


class PortoAutomacao:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 60)

    # -------------------------------------------------
    # 1️⃣ ACESSAR PORTAL
    # -------------------------------------------------

    def acessar_portal(self):

        print("Acessando o portal...")
        self.driver.get(Config.PORTO_URL)

        time.sleep(5)

    # -------------------------------------------------
    # 2️⃣ LOGIN
    # -------------------------------------------------

    def realizar_login(self, usuario, senha):

        print(f"Realizando login com {usuario}...")

        campo_cpf = self.wait.until(
            EC.presence_of_element_located((By.ID, "inputCPF"))
        )
        campo_cpf.clear()
        campo_cpf.send_keys(usuario)

        campo_senha = self.wait.until(
            EC.presence_of_element_located((By.ID, "inputPassword"))
        )
        campo_senha.clear()
        campo_senha.send_keys(senha)

        botao_entrar = self.wait.until(
            EC.element_to_be_clickable((By.ID, "j_id19"))
        )

        botao_entrar.click()

        print("Login enviado, aguardando carregamento...")

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

        elemento = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'ATENDER PEDIDO')]")
            )
        )

        self.driver.execute_script("arguments[0].click();", elemento)

        print("Clique realizado, aguardando resposta da tela...")

        try:

            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.find_elements(
                    By.CLASS_NAME,
                    "background_detalhes_sinistro_right_top_side"
                )
                or driver.find_elements(
                    By.CLASS_NAME,
                    "backgroundNoResultTextPadding"
                )
            )

            if self.driver.find_elements(By.CLASS_NAME, "background_detalhes_sinistro_right_top_side"):
                print("✅ Pedido encontrado!")
                return True

            if self.driver.find_elements(By.CLASS_NAME, "backgroundNoResultTextPadding"):
                print("⚠️ Nenhum pedido disponível.")
                return False

        except TimeoutException:

            print("⚠️ Tempo esgotado.")
            return False

    # -------------------------------------------------
    # 4️⃣ CAPTURAR DADOS
    # -------------------------------------------------

    def capturar_dados_pedido(self):

        print("Capturando pedidos encontrados...")

        pedidos = self.driver.find_elements(
            By.CLASS_NAME,
            "background_detalhes_sinistro_right_top_side"
        )

        print(f"🔎 Total de pedidos encontrados: {len(pedidos)}")

        for index, pedido in enumerate(pedidos, start=1):

            print(f"\n📦 Processando pedido {index}...")

            try:

                def pegar_valor(titulo):

                    try:

                        label = pedido.find_element(
                            By.XPATH,
                            f".//span[normalize-space()='{titulo}']"
                        )

                        valor = label.find_element(
                            By.XPATH,
                            "./ancestor::tr/following-sibling::tr[1]//span"
                        )

                        return valor.text.strip()

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
                    "ano": pegar_valor("Ano")

                }

                # criticidade
                try:

                    criticidade = pedido.find_element(
                        By.XPATH,
                        ".//span[contains(@class,'progress-bar-status-tarefa-text')]"
                    ).text.strip()

                except:

                    criticidade = "Não encontrado"

                dados["criticidade"] = criticidade

                print("\n📋 DADOS CAPTURADOS:")

                for chave, valor in dados.items():

                    print(f"{chave}: {valor}")

                # ENVIO EMAIL

                try:

                    NotificadorEmail.enviar_alerta(dados)
                    print("✅ Email enviado com sucesso!")

                except Exception as e:

                    print("❌ Erro ao enviar email:", e)

                time.sleep(1)

            except Exception as erro_bloco:

                print(f"❌ Erro ao processar pedido {index}: {erro_bloco}")

        return True