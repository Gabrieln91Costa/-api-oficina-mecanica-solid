from typing import Optional

from sqlalchemy import Column
from sqlalchemy import String
from sqlmodel import Field
from sqlmodel import SQLModel


class UnidadeModel(SQLModel, table=True):

    __tablename__ = "unidade"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    nome: str = Field(
        nullable=False
    )

    cnpj: str = Field(
        sa_column=Column(
            String,
            nullable=False,
            unique=True,
            index=True
        )
    )

    endereco: str = Field(
        nullable=False
    )

    cidade: str = Field(
        nullable=False
    )

    estado: str = Field(
        nullable=False
    )

    telefone: str = Field(
        nullable=False
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )