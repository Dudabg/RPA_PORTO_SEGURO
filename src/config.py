import os
from dotenv import load_dotenv

# ✅ Acha o .env na raiz independente de onde o script é rodado
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))


class Config:

    # -------------------------
    # PORTO
    # -------------------------
    PORTO_URL = os.getenv("PORTO_URL")
    HEADLESS  = os.getenv("HEADLESS", "False").lower() == "true"

    # -------------------------
    # CICLO
    # -------------------------
    TEMPO_ESPERA = 300

    # -------------------------
    # SEGURANÇA
    # -------------------------
    CRYPTO_KEY = os.getenv("CRYPTO_KEY")

    # -------------------------
    # EMAIL
    # -------------------------
    EMAIL_REMETENTE   = os.getenv("EMAIL_REMETENTE")
    EMAIL_SENHA       = os.getenv("EMAIL_SENHA")
    EMAIL_CANAL_TEAMS = os.getenv("EMAIL_CANAL_TEAMS")
    SMTP_SERVIDOR = os.getenv("SMTP_SERVIDOR")
    SMTP_PORTA    = int(os.getenv("SMTP_PORTA"))
    SMTP_USER     = os.getenv("SMTP_USER")   # ✅ novo
    SMTP_PASS     = os.getenv("SMTP_PASS")   # ✅ novo

    # -------------------------
    # DIRETÓRIOS
    # -------------------------
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR  = os.path.join(BASE_DIR, "logs")