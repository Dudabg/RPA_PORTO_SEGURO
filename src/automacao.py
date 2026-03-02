from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import Config
from notificador_email import NotificadorEmail  # ✅ NOVO IMPORT
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
   # -------------------------------------------------
# 2️⃣ LOGIN (CORRIGIDO DEFINITIVAMENTE)
# -------------------------------------------------
    def realizar_login(self, usuario, senha):

        print(f"Realizando login com {usuario}...")

        # Espera o campo CPF aparecer
        campo_cpf = self.wait.until(
            EC.presence_of_element_located((By.ID, "inputCPF"))
        )
        campo_cpf.clear()
        campo_cpf.send_keys(usuario)

        # Espera o campo senha aparecer
        campo_senha = self.wait.until(
            EC.presence_of_element_located((By.ID, "inputPassword"))
        )
        campo_senha.clear()
        campo_senha.send_keys(senha)

        # Espera botão ficar clicável
        botao_entrar = self.wait.until(
            EC.element_to_be_clickable((By.ID, "j_id19"))
        )

        # Clica normalmente
        botao_entrar.click()

        print("Login enviado, aguardando carregamento...")

        # Aguarda tela principal carregar
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'ATENDER PEDIDO')]")
            )
        )

        print("Login concluído!")

    # -------------------------------------------------
    # 3️⃣ ATENDER PEDIDO
    # -------------------------------------------------
    # -------------------------------------------------
# 3️⃣ ATENDER PEDIDO (CORRIGIDO)
# -------------------------------------------------
    # -------------------------------------------------
# 3️⃣ ATENDER PEDIDO (CORRIGIDO DEFINITIVO)
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
            # Espera até 15 segundos por QUALQUER um dos dois cenários
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.find_elements(
                    By.XPATH, "//span[contains(text(),'Número Sinistro')]"
                )
                or driver.find_elements(
                    By.CLASS_NAME, "backgroundNoResultTextPadding"
                )
            )

            # 🔎 Se encontrou pedido
            if self.driver.find_elements(By.XPATH, "//span[contains(text(),'Número Sinistro')]"):
                print("✅ Pedido encontrado!")
                return True

            # 🔎 Se encontrou mensagem de nenhum pedido
            if self.driver.find_elements(By.CLASS_NAME, "backgroundNoResultTextPadding"):
                print("⚠️ Nenhum pedido disponível para este CPF.")
                return False

        except TimeoutException:
            print("⚠️ Tempo esgotado. Nenhum pedido identificado.")
            return False
    # -------------------------------------------------
    # 4️⃣ CAPTURAR DADOS
    # -------------------------------------------------
    # -------------------------------------------------
# 4️⃣ CAPTURAR DADOS (MÚLTIPLOS PEDIDOS)
# -------------------------------------------------
    # -------------------------------------------------
# 4️⃣ CAPTURAR DADOS (MÚLTIPLOS PEDIDOS - DEFINITIVO)
# -------------------------------------------------
   # -------------------------------------------------
# 4️⃣ CAPTURAR DADOS (VERSÃO ESTÁVEL)
# -------------------------------------------------
    def capturar_dados_pedido(self):
        print("Capturando pedidos encontrados...")

        pedidos = self.driver.find_elements(
        By.XPATH,
        "//span[normalize-space()='Número Sinistro']/ancestor::td[contains(@id,'formFornecimento:atenderPedidoList')]"
        )

        print(f"🔎 Total de pedidos encontrados: {len(pedidos)}")

        for index, pedido in enumerate(pedidos, start=1):

            print(f"\n📦 Processando pedido {index}...")

            try:

                def pegar_valor(titulo):
                    try:
                        elemento = pedido.find_element(
                            By.XPATH,
                            f".//span[normalize-space()='{titulo}']/ancestor::table[1]//tr[2]//span"
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

                try:
                    criticidade = pedido.find_element(
                        By.XPATH,
                        ".//span[contains(@class,'progress-bar-status-tarefa-text')]"
                    ).text.strip()
                except:
                    criticidade = "Não encontrado"

                dados["criticidade"] = criticidade

                print("DADOS CAPTURADOS:")
                for chave, valor in dados.items():
                    print(f"{chave}: {valor}")

                # 🔒 ENVIO PROTEGIDO
                try:
                    NotificadorEmail.enviar_alerta(dados)
                    print("✅ Email enviado com sucesso!")
                except Exception as e:
                    print("❌ Erro ao enviar email:", e)

            except Exception as erro_bloco:
                print(f"❌ Ero ao processar pedido {index}: {erro_bloco}")

        return True