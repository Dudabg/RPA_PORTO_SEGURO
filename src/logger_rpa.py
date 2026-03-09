from datetime import datetime
import socket


def iniciar_execucao(conexao, nome_robo):

    cursor = conexao.cursor()

    sql = """
        INSERT INTO RMP.RPA_EXECUTION
        (ID_EXECUTION,
         ROBOT_NAME,
         START_AT,
         STATUS,
         HOSTNAME,
         CREATED_AT,
         CREATED_BY)
        VALUES
        (RMP.SEQ_RPA_EXECUTION.NEXTVAL,
         :robot_name,
         :start_at,
         :status,
         :hostname,
         :created_at,
         :created_by)
        RETURNING ID_EXECUTION INTO :id_exec
    """

    id_exec = cursor.var(int)

    cursor.execute(sql, {
        "robot_name": nome_robo,
        "start_at": datetime.now(),
        "status": "RUNNING",
        "hostname": socket.gethostname(),
        "created_at": datetime.now(),
        "created_by": nome_robo,
        "id_exec": id_exec
    })

    conexao.commit()

    return id_exec.getvalue()[0]


def finalizar_execucao(conexao, id_execucao, nome_robo):

    cursor = conexao.cursor()

    sql = """
        UPDATE RMP.RPA_EXECUTION
        SET
            END_AT = :end_at,
            STATUS = :status,
            UPDATED_AT = :updated_at,
            UPDATED_BY = :updated_by
        WHERE ID_EXECUTION = :id_exec
    """

    cursor.execute(sql, {
        "end_at": datetime.now(),
        "status": "STOPPED",
        "updated_at": datetime.now(),
        "updated_by": nome_robo,
        "id_exec": id_execucao
    })

    conexao.commit()


def registrar_erro_tecnico(conexao, id_execucao, tipo, mensagem):

    cursor = conexao.cursor()

    sql = """
        INSERT INTO RMP.RPA_ERROR_TECH
        (ID_ERROR_TECH,
         ID_EXECUTION,
         ERROR_TYPE,
         ERROR_MESSAGE,
         CREATED_AT,
         CREATED_BY)
        VALUES
        (RMP.SEQ_RPA_ERROR_TECH.NEXTVAL,
         :id_exec,
         :tipo,
         :mensagem,
         :created_at,
         :created_by)
    """

    cursor.execute(sql, {
        "id_exec": id_execucao,
        "tipo": tipo,
        "mensagem": mensagem,
        "created_at": datetime.now(),
        "created_by": "RPA_PORTO"
    })

    conexao.commit()