from datetime import date
from datetime import time
from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class AcompanhamentoOrdemServicoModel(SQLModel, table=True):

    __tablename__ = "acompanhamento_ordem_servico"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    ordem_servico_id: int = Field(
        foreign_key="ordem_servico.id",
        nullable=False,
        index=True
    )

    status: str = Field(
        nullable=False,
        index=True
    )

    percentual: int = Field(
        default=0,
        nullable=False
    )

    observacao: Optional[str] = Field(
        default=None
    )

    data: date = Field(
        nullable=False
    )

    hora: time = Field(
        nullable=False
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )