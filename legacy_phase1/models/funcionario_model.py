from typing import Optional

from sqlmodel import Field, SQLModel


class FuncionarioModel(SQLModel, table=True):

    __tablename__ = "funcionario"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    nome: str = Field(
        nullable=False,
        index=True
    )

    cpf: str = Field(
        nullable=False,
        index=True
    )

    telefone: Optional[str] = Field(
        default=None
    )

    email: Optional[str] = Field(
        default=None
    )

    cargo: str = Field(
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
