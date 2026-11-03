from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class PecaModel(SQLModel, table=True):

    __tablename__ = "peca"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    nome: str = Field(
        nullable=False,
        index=True
    )

    descricao: Optional[str] = Field(
        default=None
    )

    codigo: str = Field(
        nullable=False,
        index=True
    )

    quantidade_estoque: int = Field(
        default=0,
        nullable=False
    )

    estoque_minimo: int = Field(
        default=0,
        nullable=False
    )

    valor_unitario: float = Field(
        nullable=False
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