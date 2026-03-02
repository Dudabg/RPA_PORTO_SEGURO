import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # -------------------------
    # PORTO (MANTIDO)
    # -------------------------
    PORTO_URL = os.getenv("PORTO_URL")
    PORTO_USER = os.getenv("PORTO_USER")
    PORTO_PASSWORD = os.getenv("PORTO_PASSWORD")
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"

    # -------------------------
    # LISTA DE CPFs PARA MONITORAMENTO
    # -------------------------
    CNPJS = [
        {"usuario": "13510527054", "senha": "vendas10"},
        {"usuario": "04527072005", "senha": "vendas10"},
        {"usuario": "31466498021", "senha": "vendas10"},
        {"usuario": "45619945057", "senha": "vendas10"},
        {"usuario": "26408028012", "senha": "vendas10"},
        {"usuario": "51983079049", "senha": "vendas10"},
        {"usuario": "26572696057", "senha": "batata14"},
        {"usuario": "82366330049", "senha": "vendas20"},
        {"usuario": "82489673017", "senha": "vendas20"},
        {"usuario": "56022821061", "senha": "vendas20"},
        {"usuario": "45650126003", "senha": "vendas20"},
        {"usuario": "57474628066", "senha": "vendas20"},
        {"usuario": "69922686007", "senha": "vendas20"},
        {"usuario": "83296553002", "senha": "vendas20"},
    ]

    # Tempo de espera entre cada ciclo completo (em segundos)
    TEMPO_ESPERA = 300  # 5 minutos

    # -------------------------
    # EMAIL (MANTIDO)
    # -------------------------
    EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
    EMAIL_SENHA = os.getenv("EMAIL_SENHA")
    EMAIL_CANAL_TEAMS = os.getenv("EMAIL_CANAL_TEAMS")
    SMTP_SERVIDOR = os.getenv("SMTP_SERVIDOR")
    SMTP_PORTA = int(os.getenv("SMTP_PORTA"))

    # ==============================
    # DIRETÓRIOS
    # ==============================
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(BASE_DIR, "logs")