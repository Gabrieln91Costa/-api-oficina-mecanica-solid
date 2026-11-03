from datetime import date, time
from typing import Optional

from sqlmodel import Field, SQLModel


class OrdemServicoModel(SQLModel, table=True):

    __tablename__ = "ordem_servico"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    numero_ordem: str = Field(
        nullable=False,
        index=True
    )

    unidade_id: int = Field(
        nullable=False,
        foreign_key="unidade.id",
        index=True
    )

    cliente_id: int = Field(
        nullable=False,
        foreign_key="cliente.id",
        index=True
    )

    servico_id: int = Field(
        nullable=False,
        foreign_key="servico.id",
        index=True
    )

    peca_id: Optional[int] = Field(
        default=None,
        foreign_key="peca.id",
        index=True
    )

    data: date = Field(
        nullable=False
    )

    hora: time = Field(
        nullable=False
    )

    status: str = Field(
        default="RECEBIDA",
        nullable=False,
        index=True
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )