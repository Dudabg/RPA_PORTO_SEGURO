import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config


class NotificadorEmail:

    @staticmethod
    def enviar_alerta(dados):

        try:
            # ===== DESTINATÁRIOS =====
            destinatario = Config.EMAIL_CANAL_TEAMS

            if isinstance(destinatario, str):
                destinatarios = [d.strip() for d in destinatario.split(",")]
            else:
                destinatarios = destinatario

            # ===== PERMITE REPOSIÇÃO — cor e texto =====
            permite_reposicao = dados.get('permite_reposicao')

            if permite_reposicao == "Não":
                reposicao_html = '<span style="color:red;"><b>Não</b></span>'
            elif permite_reposicao == "Sim":
                reposicao_html = '<span style="color:green;"><b>Sim</b></span>'
            else:
                reposicao_html = '<span style="color:gray;">—</span>'

            # ===== MONTA MENSAGEM =====
            msg = MIMEMultipart("alternative")
            msg["From"]    = Config.EMAIL_REMETENTE
            msg["To"]      = ", ".join(destinatarios)
            msg["Subject"] = f"🚨 Novo Pedido - Sinistro {dados.get('numero_sinistro', '')}"

            corpo_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color:#d9534f;">🚨 Novo Pedido Recebido</h2>

                    <p><b>Atendente:</b> {dados.get('nome_usuario', '')}</p>

                    <hr style="border: none; border-top: 1px solid #eee;">

                    <p><b>Número Sinistro:</b> {dados.get('numero_sinistro', '')}</p>
                    <p><b>Número Pedido:</b> {dados.get('numero_pedido', '')}</p>
                    <p><b>Data Solicitação:</b> {dados.get('data_solicitacao', '')}</p>
                    <p><b>Data Pedido:</b> {dados.get('data_pedido', '')}</p>

                    <hr style="border: none; border-top: 1px solid #eee;">

                    <p><b>Marca:</b> {dados.get('marca', '')}</p>
                    <p><b>Veículo:</b> {dados.get('veiculo', '')}</p>
                    <p><b>Modelo:</b> {dados.get('modelo', '')}</p>
                    <p><b>Placa:</b> {dados.get('placa', '')}</p>
                    <p><b>Chassi:</b> {dados.get('chassi', '')}</p>
                    <p><b>Ano:</b> {dados.get('ano', '')}</p>

                    <hr style="border: none; border-top: 1px solid #eee;">

                    <p><b>Permite Reposição:</b> {reposicao_html}</p>

                    <p><b>Criticidade:</b>
                       <span style="color:red;">
                       <b>{dados.get('criticidade', '')}</b>
                       </span>
                    </p>

                    <hr>
                    <p style="font-size:12px;color:gray;">
                        Mensagem automática enviada pelo RPA Porto Seguro
                    </p>

                </body>
            </html>
            """

            msg.attach(MIMEText(corpo_html, "html", "utf-8"))

            # ===== ENVIO VIA AWS SES SMTP (STARTTLS porta 587) =====
            with smtplib.SMTP(Config.SMTP_SERVIDOR, Config.SMTP_PORTA, timeout=30) as servidor:

                servidor.ehlo()
                servidor.starttls()
                servidor.ehlo()
                servidor.login(Config.SMTP_USER, Config.SMTP_PASS)
                servidor.sendmail(
                    Config.EMAIL_REMETENTE,
                    destinatarios,
                    msg.as_string()
                )

            print(f"✅ Email enviado com sucesso para: {', '.join(destinatarios)}")

        except smtplib.SMTPException as e:
            print(f"❌ Erro SMTP ao enviar email: {str(e)}")

        except Exception as e:
            print(f"❌ Erro inesperado ao enviar email: {str(e)}")