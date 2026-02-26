from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config import Config
import os


def criar_navegador():
    options = Options()

    if Config.HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")

    caminho_driver = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "driver",
        "chromedriver.exe"
    )

    service = Service(caminho_driver)
    driver = webdriver.Chrome(service=service, options=options)

    return driver