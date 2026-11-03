from typing import Protocol

class Notificador(Protocol):
    def enviar(self, destinatario: str, assunto: str, mensagem: str) -> None: ...
