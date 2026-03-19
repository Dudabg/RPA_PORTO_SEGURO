from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config import Config
from notificador_email import NotificadorEmail
from logger_rpa import registrar_ordem, atualizar_status_ordem, registrar_erro_tecnico, registrar_erro_negocio, pedido_ja_existe
import time
import json


class PortoAutomacao:

    def __init__(self, driver, conexao, id_execucao, nome_robo="RPA_PORTO_001", logger=None):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 120)
        self.conexao = conexao
        self.id_execucao = id_execucao
        self.nome_robo = nome_robo
        self.nome_usuario = None
        self.logger = logger

    def _log(self, mensagem: str):
        if self.logger:
            self.logger.log(mensagem)
        else:
            print(mensagem)

    # -------------------------------------------------
    # 1️⃣ ACESSAR PORTAL
    # -------------------------------------------------

    def acessar_portal(self):

        self._log("Acessando o portal...")
        self.driver.get(Config.PORTO_URL)
        time.sleep(10)

    # -------------------------------------------------
    # 2️⃣ LOGIN
    # -------------------------------------------------

    def realizar_login(self, usuario, senha):

        self._log(f"Realizando login com {usuario}...")

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

        self._log("Login enviado, aguardando carregamento...")

        # ✅ Aguarda: dashboard OU mensagem de erro de login
        try:
            WebDriverWait(self.driver, 60).until(
                lambda driver:
                    driver.find_elements(
                        By.XPATH,
                        "//li[contains(text(),'LOGIN E/OU SENHA INVÁLIDOS')]"
                    )
                    or driver.find_elements(
                        By.XPATH,
                        "//span[contains(text(),'ATENDER PEDIDO')]"
                    )
            )
        except TimeoutException:
            raise Exception(f"Timeout aguardando resposta do login para CPF {usuario}")

        # ✅ Verifica se apareceu erro de login inválido
        if self.driver.find_elements(
            By.XPATH,
            "//li[contains(text(),'LOGIN E/OU SENHA INVÁLIDOS')]"
        ):
            self._log(f"⚠️ Login inválido para CPF {usuario}. Verifique a senha no banco.")

            # ✅ Grava como erro técnico (robô não conseguiu executar)
            registrar_erro_tecnico(
                conexao     = self.conexao,
                id_execucao = self.id_execucao,
                nome_robo   = self.nome_robo,
                tipo        = "LOGIN_INVALIDO",
                mensagem    = f"CPF {usuario}: LOGIN E/OU SENHA INVÁLIDOS no portal.",
            )

            # Envia e-mail de alerta
            try:
                NotificadorEmail.enviar_alerta_login_invalido(usuario)
            except Exception as e_email:
                self._log(f"Erro ao enviar alerta de login inválido: {e_email}")

                # ✅ Falha no e-mail de alerta = erro de negócio com id_order NULL
                registrar_erro_negocio(
                    conexao       = self.conexao,
                    id_order      = None,
                    regra_negocio = "ERRO_EMAIL_ALERTA_LOGIN",
                    mensagem      = f"Falha ao enviar alerta de login inválido para CPF {usuario}: {str(e_email)[:500]}",
                    nome_robo     = self.nome_robo,
                )

            raise Exception(f"LOGIN_INVALIDO: CPF {usuario}")

        # ✅ Login OK — aguarda dashboard carregar
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'ATENDER PEDIDO')]")
            )
        )

        # ✅ Captura o nome do usuário logado
        try:
            self.nome_usuario = self.driver.find_element(
                By.XPATH,
                "//span[contains(@class,'text_common_blue') and contains(@class,'bold')]"
            ).text.strip()
            self._log(f"Usuário logado: {self.nome_usuario}")
        except Exception:
            self.nome_usuario = "Não identificado"
            self._log("Não foi possível capturar o nome do usuário.")

        self._log("Login concluído!")

    # -------------------------------------------------
    # 3️⃣ ATENDER PEDIDO
    # -------------------------------------------------

    def acessar_atender_pedido(self):

        self._log("Acessando ATENDER PEDIDO...")

        elemento = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'ATENDER PEDIDO')]")
            )
        )

        self.driver.execute_script("arguments[0].click();", elemento)

        self._log("Clique realizado, aguardando resposta da tela...")

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
                self._log("Pedido encontrado!")
                return True

            if self.driver.find_elements(By.CLASS_NAME, "backgroundNoResultTextPadding"):
                self._log("Nenhum pedido disponível.")
                return False

        except TimeoutException:
            self._log("Tempo esgotado.")
            return False

    # -------------------------------------------------
    # 4️⃣ CAPTURAR DADOS + GRAVAR NO BANCO
    # -------------------------------------------------

    def capturar_dados_pedido(self):

        self._log("Capturando pedidos encontrados...")

        pedidos = self.driver.find_elements(
            By.CLASS_NAME,
            "background_detalhes_sinistro_right_top_side"
        )

        self._log(f"Total de pedidos encontrados: {len(pedidos)}")

        for index, pedido in enumerate(pedidos, start=1):

            self._log(f"Processando pedido {index}...")

            id_order = None

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
                        return None

                dados = {
                    "nome_usuario":     self.nome_usuario,
                    "numero_sinistro":  pegar_valor("Número Sinistro"),
                    "data_solicitacao": pegar_valor("Data da Solicitação"),
                    "numero_pedido":    pegar_valor("Número do Pedido"),
                    "data_pedido":      pegar_valor("Data do Pedido"),
                    "marca":            pegar_valor("Marca"),
                    "veiculo":          pegar_valor("Veículo"),
                    "modelo":           pegar_valor("Modelo"),
                    "placa":            pegar_valor("Placa"),
                    "chassi":           pegar_valor("Chassi"),
                    "ano":              pegar_valor("Ano"),
                }

                # ── Criticidade ─────────────────────────────────────────────
                try:
                    criticidade = pedido.find_element(
                        By.XPATH,
                        ".//span[contains(@class,'progress-bar-status-tarefa-text')]"
                    ).text.strip()
                except Exception:
                    criticidade = None

                dados["criticidade"] = criticidade

                # ── Permite Reposição ───────────────────────────────────────
                try:
                    reposicao_el = pedido.find_element(
                        By.XPATH,
                        ".//span[normalize-space()='Permite Reposição']"
                    )
                    img_src = reposicao_el.find_element(
                        By.XPATH,
                        "./ancestor::tr/following-sibling::tr[1]//img"
                    ).get_attribute("src")

                    permite_reposicao = "Não" if "alert_recusa" in img_src else "Sim"

                except Exception:
                    permite_reposicao = None

                dados["permite_reposicao"] = permite_reposicao

                self._log("DADOS CAPTURADOS:")
                for chave, valor in dados.items():
                    self._log(f"  {chave}: {valor or '—'}")

                # ── Verificação de duplicata ────────────────────────────────
                numero = dados["numero_pedido"]

                if numero and pedido_ja_existe(self.conexao, numero):
                    self._log(f"Pedido {numero} já registrado. Pulando.")
                    continue

                # ── Insere no banco ─────────────────────────────────────────
                id_order = registrar_ordem(
                    conexao       = self.conexao,
                    id_execucao   = self.id_execucao,
                    numero_pedido = numero,
                    raw_payload   = json.dumps(dados, ensure_ascii=False),
                    nome_robo     = self.nome_robo,
                    customer_name = "PORTO SEGURO",
                    order_date    = dados["data_pedido"],
                )

                self._log(f"Pedido inserido no banco. ID_ORDER={id_order}")

                # ── Campos obrigatórios ─────────────────────────────────────
                campos_obrigatorios = {
                    "numero_pedido": dados["numero_pedido"],
                    "placa":         dados["placa"],
                    "chassi":        dados["chassi"],
                }

                for campo, valor in campos_obrigatorios.items():
                    if not valor:
                        registrar_erro_negocio(
                            conexao       = self.conexao,
                            id_order      = id_order,
                            regra_negocio = "CAMPO_OBRIGATORIO_AUSENTE",
                            mensagem      = f"Campo obrigatório '{campo}' não encontrado no portal.",
                            nome_robo     = self.nome_robo,
                        )
                        self._log(f"Campo obrigatório ausente: {campo}. Erro de negócio registrado.")

                # ── Envio de e-mail ─────────────────────────────────────────
                try:
                    NotificadorEmail.enviar_alerta(dados)
                    self._log("Email enviado com sucesso!")

                    atualizar_status_ordem(
                        conexao   = self.conexao,
                        id_order  = id_order,
                        status    = "PROCESSED",
                        nome_robo = self.nome_robo,
                    )

                except Exception as e_email:
                    self._log(f"Erro ao enviar email: {e_email}")

                    # ✅ Falha no e-mail = erro de negócio (pedido capturado mas não comunicado)
                    registrar_erro_negocio(
                        conexao       = self.conexao,
                        id_order      = id_order,
                        regra_negocio = "ERRO_ENVIO_EMAIL",
                        mensagem      = f"Falha ao enviar e-mail para Key Account: {str(e_email)[:500]}",
                        nome_robo     = self.nome_robo,
                    )

                    atualizar_status_ordem(
                        conexao   = self.conexao,
                        id_order  = id_order,
                        status    = "ERROR",
                        nome_robo = self.nome_robo,
                    )

                time.sleep(1)

            except Exception as erro_bloco:

                self._log(f"Erro ao processar pedido {index}: {erro_bloco}")

                registrar_erro_tecnico(
                    conexao     = self.conexao,
                    id_execucao = self.id_execucao,
                    nome_robo   = self.nome_robo,
                    tipo        = "ERRO_CAPTURA_PEDIDO",
                    mensagem    = str(erro_bloco),
                    excecao     = erro_bloco,
                )

                if id_order:
                    atualizar_status_ordem(
                        conexao   = self.conexao,
                        id_order  = id_order,
                        status    = "ERROR",
                        nome_robo = self.nome_robo,
                    )

        return True