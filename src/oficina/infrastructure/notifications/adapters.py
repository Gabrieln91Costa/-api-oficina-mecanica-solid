import logging
import smtplib
from email.message import EmailMessage
from oficina.config import get_settings

logger = logging.getLogger(__name__)

class LoggingNotifier:
    def enviar(self, destinatario: str, assunto: str, mensagem: str) -> None:
        logger.info('Notificação para %s | %s | %s', destinatario, assunto, mensagem)

class SMTPNotifier:
    def __init__(self): self.settings = get_settings()
    def enviar(self, destinatario: str, assunto: str, mensagem: str) -> None:
        s = self.settings
        if not all([s.smtp_host, s.smtp_from]):
            LoggingNotifier().enviar(destinatario, assunto, mensagem); return
        msg = EmailMessage(); msg['Subject'] = assunto; msg['From'] = s.smtp_from; msg['To'] = destinatario; msg.set_content(mensagem)
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=15) as server:
            if s.smtp_starttls: server.starttls()
            if s.smtp_user: server.login(s.smtp_user, s.smtp_password or '')
            server.send_message(msg)
