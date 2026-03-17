from datetime import datetime
import socket
import traceback


# ══════════════════════════════════════════════
# LOGGER DE CONSOLE — captura prints para o banco
# ══════════════════════════════════════════════

class ExecutionLogger:
    """
    Substitui o print() padrão durante a execução.
    Tudo que seria impresso no console também é
    acumulado em memória para gravar no banco.
    """

    def __init__(self):
        self._linhas = []

    def log(self, mensagem: str):
        """Imprime no console E acumula para o banco."""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linha = f"[{timestamp}] {mensagem}"
        print(linha)
        self._linhas.append(linha)

    def obter_log(self) -> str:
        """Retorna todo o log acumulado como texto."""
        return "\n".join(self._linhas)

    def limpar(self):
        """Limpa o log acumulado (usado entre CPFs se necessário)."""
        self._linhas = []


# ══════════════════════════════════════════════
# RPA_EXECUTION
# ══════════════════════════════════════════════

def iniciar_execucao(conexao, nome_robo):

    cursor = conexao.cursor()

    try:
        sql = """
            INSERT INTO RMP.RPA_EXECUTION
            (ID_EXECUTION, ROBOT_NAME, START_AT, STATUS,
             HOSTNAME, CREATED_AT, CREATED_BY)
            VALUES
            (RMP.SEQ_RPA_EXECUTION.NEXTVAL, :robot_name, :start_at,
             :status, :hostname, :created_at, :created_by)
            RETURNING ID_EXECUTION INTO :id_exec
        """
        id_exec = cursor.var(int)
        cursor.execute(sql, {
            "robot_name": nome_robo,
            "start_at":   datetime.now(),
            "status":     "RUNNING",
            "hostname":   socket.gethostname(),
            "created_at": datetime.now(),
            "created_by": nome_robo,
            "id_exec":    id_exec,
        })
        conexao.commit()
        return id_exec.getvalue()[0]

    finally:
        cursor.close()


def finalizar_execucao(conexao, id_execucao, nome_robo, status="SUCCESS"):

    cursor = conexao.cursor()

    try:
        sql = """
            UPDATE RMP.RPA_EXECUTION
            SET END_AT     = :end_at,
                STATUS     = :status,
                UPDATED_AT = :updated_at,
                UPDATED_BY = :updated_by
            WHERE ID_EXECUTION = :id_exec
        """
        cursor.execute(sql, {
            "end_at":     datetime.now(),
            "status":     status,
            "updated_at": datetime.now(),
            "updated_by": nome_robo,
            "id_exec":    id_execucao,
        })
        conexao.commit()

    finally:
        cursor.close()


def gravar_log_execucao(conexao, id_execucao, log_texto: str):
    """
    Grava (ou concatena) o log de execução na coluna
    RPA_EXECUTION_LOG da tabela RPA_EXECUTION.
    Chamado incrementalmente a cada CPF verificado.
    """
    cursor = conexao.cursor()

    try:
        sql = """
            UPDATE RMP.RPA_EXECUTION
               SET RPA_EXECUTION_LOG = RPA_EXECUTION_LOG || :log_texto,
                   UPDATED_AT        = SYSTIMESTAMP
             WHERE ID_EXECUTION = :id_exec
        """
        cursor.execute(sql, {
            "log_texto": log_texto + "\n",
            "id_exec":   id_execucao,
        })
        conexao.commit()

    finally:
        cursor.close()


# ══════════════════════════════════════════════
# RPA_ORDER
# ══════════════════════════════════════════════

def pedido_ja_existe(conexao, numero_pedido):
    """
    Verifica se o pedido já foi registrado e processado com sucesso.
    Retorna True se já existe com status PENDING ou PROCESSED.
    Pedidos com status ERROR são permitidos tentar novamente.
    """
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
              FROM RMP.RPA_ORDER
             WHERE ORDER_NUMBER = :numero
               AND STATUS IN ('PENDING', 'PROCESSED')
        """, {"numero": numero_pedido})

        return cursor.fetchone()[0] > 0

    finally:
        cursor.close()


def registrar_ordem(conexao, id_execucao, numero_pedido, raw_payload, nome_robo,
                    customer_name=None, order_date=None):
    """
    Insere o pedido capturado via webscraping com status PENDING.
    Retorna o ID_ORDER gerado.
    """
    data_convertida = None
    if order_date:
        try:
            data_convertida = datetime.strptime(order_date, "%d/%m/%Y").date()
        except ValueError:
            pass

    cursor = conexao.cursor()

    try:
        sql = """
            INSERT INTO RMP.RPA_ORDER
            (ID_ORDER, ID_EXECUTION, ERP_NAME, ORDER_NUMBER,
             CUSTOMER_NAME, ORDER_DATE,
             STATUS, RAW_PAYLOAD, CREATED_AT, UPDATED_AT, CREATED_BY, UPDATED_BY)
            VALUES
            (RMP.SEQ_RPA_ORDER.NEXTVAL, :id_exec, :erp_name, :order_number,
             :customer_name, :order_date,
             'PENDING', :raw_payload, SYSTIMESTAMP, SYSTIMESTAMP, :created_by, :created_by)
            RETURNING ID_ORDER INTO :id_order
        """
        id_var = cursor.var(int)
        cursor.execute(sql, {
            "id_exec":       id_execucao,
            "erp_name":      "PORTO",
            "order_number":  numero_pedido or "SEM_NUMERO",
            "customer_name": customer_name or "PORTO SEGURO",
            "order_date":    data_convertida,
            "raw_payload":   raw_payload,
            "created_by":    nome_robo,
            "id_order":      id_var,
        })
        conexao.commit()
        return id_var.getvalue()[0]

    finally:
        cursor.close()


def atualizar_status_ordem(conexao, id_order, status, nome_robo):
    """
    Atualiza o status do pedido.
    Status: 'PENDING' | 'PROCESSED' | 'ERROR'
    """
    cursor = conexao.cursor()

    try:
        sql = """
            UPDATE RMP.RPA_ORDER
            SET STATUS       = :status,
                PROCESSED_AT = CASE WHEN :status = 'PROCESSED' THEN SYSTIMESTAMP ELSE PROCESSED_AT END,
                UPDATED_AT   = SYSTIMESTAMP,
                UPDATED_BY   = :updated_by
            WHERE ID_ORDER = :id_order
        """
        cursor.execute(sql, {
            "status":     status,
            "updated_by": nome_robo,
            "id_order":   id_order,
        })
        conexao.commit()

    finally:
        cursor.close()


# ══════════════════════════════════════════════
# RPA_ERROR_TECH
# ══════════════════════════════════════════════

def registrar_erro_tecnico(conexao, id_execucao, nome_robo, tipo, mensagem, excecao=None):
    """
    Registra erro técnico: exceção Python, timeout Selenium, falha de e-mail, etc.
    """
    cursor = conexao.cursor()

    try:
        stack = traceback.format_exc() if excecao else None

        sql = """
            INSERT INTO RMP.RPA_ERROR_TECH
            (ID_ERROR_TECH, ID_EXECUTION, ERROR_TYPE,
             ERROR_MESSAGE, STACK_TRACE, CREATED_AT, CREATED_BY)
            VALUES
            (RMP.SEQ_RPA_ERROR_TECH.NEXTVAL, :id_exec, :tipo,
             :mensagem, :stack_trace, SYSTIMESTAMP, :created_by)
        """
        cursor.execute(sql, {
            "id_exec":     id_execucao,
            "tipo":        tipo,
            "mensagem":    str(mensagem)[:4000],
            "stack_trace": stack,
            "created_by":  nome_robo,
        })
        conexao.commit()

    finally:
        cursor.close()


# ══════════════════════════════════════════════
# RPA_ERROR_BUSINESS
# ══════════════════════════════════════════════

def registrar_erro_negocio(conexao, id_order, regra_negocio, mensagem, nome_robo):
    """
    Registra erro de negócio vinculado a um pedido específico.
    """
    cursor = conexao.cursor()

    try:
        sql = """
            INSERT INTO RMP.RPA_ERROR_BUSINESS
            (ID_ERROR_BUSINESS, ID_ORDER, BUSINESS_RULE,
             ERROR_MESSAGE, CREATED_AT, CREATED_BY)
            VALUES
            (RMP.SEQ_RPA_ERROR_BUSINESS.NEXTVAL, :id_order, :regra,
             :mensagem, SYSTIMESTAMP, :created_by)
        """
        cursor.execute(sql, {
            "id_order":   id_order,
            "regra":      regra_negocio,
            "mensagem":   str(mensagem)[:4000],
            "created_by": nome_robo,
        })
        conexao.commit()

    finally:
        cursor.close()