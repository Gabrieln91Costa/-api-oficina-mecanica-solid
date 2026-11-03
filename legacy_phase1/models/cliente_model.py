from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class ClienteModel(SQLModel, table=True):

    __tablename__ = "cliente"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    nome: str = Field(
        nullable=False,
        index=True
    )

    cpf_cnpj: str = Field(
        nullable=False,
        index=True
    )

    telefone: str = Field(
        nullable=False
    )

    email: Optional[str] = Field(
        default=None
    )

    endereco: Optional[str] = Field(
        default=None
    )

    cidade: Optional[str] = Field(
        default=None
    )

    estado: Optional[str] = Field(
        default=None
    )

    # FK para a unidade da oficina
    unidade_id: int = Field(
        foreign_key="unidade.id",
        nullable=False,
        index=True
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )