from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class UsuarioModel(SQLModel, table=True):

    __tablename__ = "usuario"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    usuario: str = Field(
        nullable=False,
        index=True
    )

    senha: str = Field(
        nullable=False
    )

    nome: str = Field(
        nullable=False
    )

    perfil: str = Field(
        nullable=False
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )