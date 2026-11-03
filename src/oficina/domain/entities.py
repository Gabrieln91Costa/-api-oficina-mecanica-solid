from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from .enums import StatusOS, StatusOrcamento, TRANSICOES_PERMITIDAS
from .exceptions import InvalidTransitionError, ValidationError

@dataclass
class OrdemServico:
    id: UUID
    cliente_id: int
    veiculo_id: int
    status: StatusOS
    criado_em: datetime
    excluida: bool = False

    def alterar_status(self, novo_status: StatusOS) -> None:
        if novo_status not in TRANSICOES_PERMITIDAS[self.status]:
            raise InvalidTransitionError(
                f"Transição não permitida: {self.status.value} -> {novo_status.value}"
            )
        self.status = novo_status

@dataclass
class Orcamento:
    id: int
    ordem_servico_id: UUID
    valor_total: Decimal
    status: StatusOrcamento

    def decidir(self, aprovado: bool) -> None:
        if self.status != StatusOrcamento.AGUARDANDO_APROVACAO:
            raise InvalidTransitionError("Orçamento já recebeu uma decisão.")
        self.status = StatusOrcamento.APROVADO if aprovado else StatusOrcamento.RECUSADO

def validar_valor(valor: Decimal) -> None:
    if valor < Decimal("0"):
        raise ValidationError("Valores não podem ser negativos.")
