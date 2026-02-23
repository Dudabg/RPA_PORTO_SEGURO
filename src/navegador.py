from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import Config

def criar_navegador():
    options=Options()

    if Config.HEADLESS:
        options.add_argument("--headless")

        
    options.add_argument("start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver