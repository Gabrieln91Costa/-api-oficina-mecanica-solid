from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class ServicoModel(SQLModel, table=True):

    __tablename__ = "servico"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    nome: str = Field(
        nullable=False
    )

    descricao: Optional[str] = Field(
        default=None,
        nullable=True
    )

    valor: float = Field(
        nullable=False
    )

    tempo_estimado: Optional[int] = Field(
        default=None,
        nullable=True
    )

    unidade_id: int = Field(
        nullable=False,
        foreign_key="unidade.id",
        index=True
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )