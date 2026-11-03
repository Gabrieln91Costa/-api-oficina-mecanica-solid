from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class VeiculoModel(SQLModel, table=True):

    __tablename__ = "veiculo"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    placa: str = Field(
        nullable=False,
        index=True
    )

    marca: str = Field(
        nullable=False
    )

    modelo: str = Field(
        nullable=False
    )

    ano: int = Field(
        nullable=False
    )

    cliente_id: int = Field(
        nullable=False,
        foreign_key="cliente.id",
        index=True
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )
