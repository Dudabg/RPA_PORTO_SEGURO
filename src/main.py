from navegador import criar_navegador
from logger_rpa import iniciar_execucao, registrar_erro_tecnico, finalizar_execucao, gravar_log_execucao, ExecutionLogger
from database import criar_conexao, garantir_conexao, buscar_credenciais
from automacao import PortoAutomacao
from config import Config
import time
from datetime import datetime

NOME_ROBO = "RPA_PORTO_001"

# ──────────────────────────────────────────────
# AGENDAMENTO
# ──────────────────────────────────────────────
HORA_INICIO = 8   # 08:00
HORA_FIM    = 18  # 18:00
DIAS_UTEIS  = [0, 1, 2, 3, 4]  # 0=segunda ... 4=sexta


def dentro_do_horario_comercial():
    agora = datetime.now()
    hora  = agora.hour
    dia   = agora.weekday()
    return dia in DIAS_UTEIS and HORA_INICIO <= hora < HORA_FIM


def main():

    logger = ExecutionLogger()
    logger.log("Iniciando monitoramento contínuo...")

    conexao      = criar_conexao()
    id_execucao  = iniciar_execucao(conexao, NOME_ROBO)
    status_final = "SUCCESS"

    logger.log(f"Execução registrada. ID: {id_execucao}")
    logger.log("Para encerrar, pressione CTRL+C\n")

    try:

        while True:

            # ✅ Verifica se está no horário comercial
            if not dentro_do_horario_comercial():
                agora = datetime.now()
                logger.log(f"[{agora.strftime('%d/%m/%Y %H:%M')}] Fora do horário comercial. Aguardando...")
                time.sleep(60)  # verifica a cada 1 minuto
                continue

            logger.log("\n==============================")
            logger.log("NOVO CICLO DE VERIFICAÇÃO")
            logger.log("==============================\n")

            conexao = garantir_conexao(conexao)
            contas  = buscar_credenciais(conexao, NOME_ROBO)

            if not contas:
                logger.log("Nenhuma credencial ativa encontrada no banco. Aguardando próximo ciclo...")

            else:
                logger.log(f"{len(contas)} credencial(is) ativa(s) encontrada(s).\n")

                for conta in contas:

                    # ✅ Checa horário a cada CPF também
                    if not dentro_do_horario_comercial():
                        logger.log("Saindo do horário comercial. Pausando até amanhã.")
                        break

                    logger.limpar()
                    logger.log(f"Verificando CPF: {conta['username']}")

                    driver    = criar_navegador()
                    automacao = PortoAutomacao(
                        driver,
                        conexao     = conexao,
                        id_execucao = id_execucao,
                        nome_robo   = NOME_ROBO,
                        logger      = logger,
                    )

                    try:
                        automacao.acessar_portal()
                        automacao.realizar_login(conta["username"], conta["password"])
                        tem_pedido = automacao.acessar_atender_pedido()

                        if tem_pedido:
                            automacao.capturar_dados_pedido()
                        else:
                            logger.log("Nenhum pedido encontrado.")

                    except Exception as e:
                        logger.log(f"Erro no CPF {conta['username']}: {e}")
                        registrar_erro_tecnico(
                            conexao     = conexao,
                            id_execucao = id_execucao,
                            nome_robo   = NOME_ROBO,
                            tipo        = "ERRO_AUTOMACAO",
                            mensagem    = str(e),
                            excecao     = e,
                        )

                    finally:
                        driver.quit()
                        logger.log("Navegador fechado.")
                        gravar_log_execucao(
                            conexao     = conexao,
                            id_execucao = id_execucao,
                            log_texto   = logger.obter_log(),
                        )

                    time.sleep(5)

            logger.log(f"Aguardando {Config.TEMPO_ESPERA}s para próximo ciclo...\n")
            time.sleep(Config.TEMPO_ESPERA)

    except KeyboardInterrupt:
        logger.log("Encerrado manualmente.")
        status_final = "SUCCESS"

    except Exception as e:
        logger.log(f"Erro inesperado: {e}")
        status_final = "ERROR"
        registrar_erro_tecnico(
            conexao     = conexao,
            id_execucao = id_execucao,
            nome_robo   = NOME_ROBO,
            tipo        = "ERRO_CRITICO",
            mensagem    = str(e),
            excecao     = e,
        )
        raise

    finally:
        finalizar_execucao(conexao, id_execucao, NOME_ROBO, status=status_final)
        conexao.close()
        logger.log(f"Conexão encerrada. Status final: {status_final}")


if __name__ == "__main__":
    main()