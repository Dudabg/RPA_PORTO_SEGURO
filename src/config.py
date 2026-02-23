import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class Config:
    PORTO_URL = os.getenv("PORTO_URL")
    PORTO_USER = os.getenv("PORTO_USER")
    PORTO_PASSWORD = os.getenv("PORTO_PASSWORD")
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(BASE_DIR, "logs")