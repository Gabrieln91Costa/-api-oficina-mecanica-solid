from datetime import date
from datetime import time
from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class TempoExecucaoServicoModel(SQLModel, table=True):

    __tablename__ = "tempo_execucao_servico"

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    servico_id: int = Field(
        foreign_key="servico.id",
        nullable=False,
        index=True
    )

    ordem_servico_id: int = Field(
        foreign_key="ordem_servico.id",
        nullable=False,
        index=True
    )

    data_inicio: date = Field(
        nullable=False
    )

    hora_inicio: time = Field(
        nullable=False
    )

    data_fim: Optional[date] = Field(
        default=None
    )

    hora_fim: Optional[time] = Field(
        default=None
    )

    tempo_execucao_minutos: Optional[int] = Field(
        default=None,
        nullable=True
    )

    ativo: bool = Field(
        default=True,
        nullable=False
    )