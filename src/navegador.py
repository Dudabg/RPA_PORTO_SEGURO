from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from config import Config
import os
import subprocess


def criar_navegador():

    options = Options()

    rodando_no_docker = os.path.exists("/.dockerenv")

    if Config.HEADLESS or rodando_no_docker:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")

    # ✅ No Docker usa o chromedriver do sistema
    # Em Windows local usa o .exe da pasta driver/
    rodando_no_docker = os.path.exists("/.dockerenv")

    if rodando_no_docker:
        # chromedriver instalado junto com o google-chrome-stable
        service = Service("/usr/bin/chromedriver")
    else:
        service = Service(os.path.join("driver", "chromedriver.exe"))

    driver = webdriver.Chrome(service=service, options=options)

    return driver