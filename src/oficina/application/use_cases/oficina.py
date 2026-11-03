from uuid import UUID
from ..ports.repositories import OficinaRepository
from ..ports.notifications import Notificador
from ...domain.enums import StatusOS
from ...domain.exceptions import NotFoundError, ValidationError

class OficinaUseCases:
    """Orquestra casos de uso; depende de abstrações, não de FastAPI ou SQLAlchemy."""
    def __init__(self, repositorio: OficinaRepository, notificador: Notificador):
        self._repositorio = repositorio
        self._notificador = notificador

    def abrir_os(self, dados: dict):
        if not dados.get("servicos"):
            raise ValidationError("Informe ao menos um serviço para abrir a OS.")
        if not dados.get("pecas", []):
            dados["pecas"] = []
        return self._repositorio.abrir_os(dados)

    def consultar_status(self, ordem_id: UUID):
        ordem = self._repositorio.buscar_os(ordem_id)
        if ordem is None:
            raise NotFoundError("Ordem de serviço não encontrada.")
        return ordem

    def listar_os(self):
        return self._repositorio.listar_os_operacionais()

    def atualizar_status(self, ordem_id: UUID, novo_status: StatusOS, origem: str = "API"):
        ordem = self._repositorio.atualizar_status(ordem_id, novo_status.value, origem)
        if ordem is None:
            raise NotFoundError("Ordem de serviço não encontrada.")
        return ordem

    def criar_orcamento(self, ordem_id: UUID, dados: dict):
        resultado = self._repositorio.criar_orcamento(ordem_id, dados)
        ordem = self._repositorio.buscar_os(ordem_id)
        if ordem and ordem.cliente.email:
            try:
                self._notificador.enviar(ordem.cliente.email, "Orçamento aguardando aprovação",
                    f"O orçamento {resultado.id} da OS {ordem.numero_ordem} está disponível para aprovação.")
            except Exception:
                # A falha de e-mail não desfaz a criação do orçamento.
                import logging
                logging.getLogger(__name__).exception("Falha ao enviar notificação de orçamento")
        return resultado

    def decidir_orcamento(self, orcamento_id: int, aprovado: bool, ator: str):
        resultado = self._repositorio.decidir_orcamento(orcamento_id, aprovado, ator)
        if resultado is None:
            raise NotFoundError("Orçamento não encontrado.")
        from uuid import UUID
        ordem = self._repositorio.buscar_os(UUID(resultado.ordem_servico_id))
        if ordem and ordem.cliente.email:
            try:
                decisao = "aprovado" if aprovado else "recusado"
                self._notificador.enviar(ordem.cliente.email, "Decisão do orçamento",
                    f"O orçamento {resultado.id} foi {decisao}. Status atual da OS: {ordem.status}.")
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Falha ao enviar notificação da decisão do orçamento")
        return resultado
