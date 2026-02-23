from config import Config

class PortoAutomacao:

    def __init__(self,driver):
        self.driver = driver

    def acessar_portal(self):
        print("Acessando o portal...")
        self.driver.get(Config.PORTO_URL)

    def realizar_login(self):
        print("Realizando login...")
        #Aqui depois começara depois o selenium
        pass

    def acessar_atender_pedido(self):
        print("Acessando menu atender pedido...")

    def verificar_pedidos_pendentes(self):
        print("Verificando pedidos pendentes...")
        pass    
        