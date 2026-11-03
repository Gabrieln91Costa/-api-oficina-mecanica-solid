from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class OrcamentoModel(SQLModel, table=True):

    __tablename__ = "orcamento"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    ordem_servico_id: int = Field(
        nullable=False,
        foreign_key="ordem_servico.id",
        index=True
    )

    valor_servicos: float = Field(
        default=0.0,
        nullable=False
    )

    valor_pecas: float = Field(
        default=0.0,
        nullable=False
    )

    desconto: float = Field(
        default=0.0,
        nullable=False
    )

    acrescimo: float = Field(
        default=0.0,
        nullable=False
    )

    valor_total: float = Field(
        default=0.0,
        nullable=False
    )

    validade: Optional[date] = Field(
        default=None
    )

    status: str = Field(
        default="AGUARDANDO_APROVACAO",
        nullable=False,
        index=True
    )

    observacao: Optional[str] = Field(
        default=None
    )

    data_aprovacao: Optional[datetime] = Field(
        default=None
    )

    aprovado_por: Optional[str] = Field(
        default=None
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )