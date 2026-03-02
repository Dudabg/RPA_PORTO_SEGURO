import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config


class NotificadorEmail:

    @staticmethod
    def enviar_alerta(dados):

        try:
            # ===== MONTA MENSAGEM =====
            msg = MIMEMultipart("alternative")
            msg["From"] = Config.EMAIL_REMETENTE
            msg["To"] = Config.EMAIL_CANAL_TEAMS
            msg["Subject"] = f"🚨 Novo Pedido - Sinistro {dados.get('numero_sinistro', '')}"

            corpo_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color:#d9534f;">🚨 Novo Pedido Recebido</h2>
                    <hr>
                    <p><b>Número Sinistro:</b> {dados.get('numero_sinistro', '')}</p>
                    <p><b>Número Pedido:</b> {dados.get('numero_pedido', '')}</p>
                    <p><b>Data Solicitação:</b> {dados.get('data_solicitacao', '')}</p>
                    <p><b>Marca:</b> {dados.get('marca', '')}</p>
                    <p><b>Veículo:</b> {dados.get('veiculo', '')}</p>
                    <p><b>Modelo:</b> {dados.get('modelo', '')}</p>
                    <p><b>Placa:</b> {dados.get('placa', '')}</p>
                    <p><b>Criticidade:</b> 
                       <span style="color:red;"><b>{dados.get('criticidade', '')}</b></span>
                    </p>
                    <hr>
                    <p style="font-size:12px;color:gray;">
                        Mensagem automática enviada pelo RPA
                    </p>
                </body>
            </html>
            """

            msg.attach(MIMEText(corpo_html, "html", "utf-8"))

            # ===== ENVIO SMTP =====
            servidor = smtplib.SMTP(
                Config.SMTP_SERVIDOR,
                int(Config.SMTP_PORTA),
                timeout=30
            )

            servidor.starttls()
            servidor.login(Config.EMAIL_REMETENTE, Config.EMAIL_SENHA)
            servidor.sendmail(
                Config.EMAIL_REMETENTE,
                Config.EMAIL_CANAL_TEAMS,
                msg.as_string()
            )
            servidor.quit()

            print("✅ Email enviado com sucesso!")

        except Exception as e:
            print("❌ Erro ao enviar email:", str(e))