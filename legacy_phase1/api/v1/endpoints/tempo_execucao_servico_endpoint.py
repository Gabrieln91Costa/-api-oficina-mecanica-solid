from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select

from core.database import get_session

from models.tempo_execucao_servico_model import (
    TempoExecucaoServicoModel
)

from models.servico_model import ServicoModel

from models.ordem_servico_model import OrdemServicoModel


router = APIRouter()


# ==========================================================
# REGISTRAR TEMPO DE EXECUÇÃO
# ==========================================================

@router.post(
    "/",
    response_model=TempoExecucaoServicoModel,
    status_code=status.HTTP_201_CREATED
)
async def registrar_tempo_execucao(
    tempo: TempoExecucaoServicoModel,
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Verifica serviço
    # ------------------------------------------------------

    result = await session.execute(
        select(ServicoModel).where(
            ServicoModel.id == tempo.servico_id
        )
    )

    servico = result.scalar_one_or_none()

    if not servico:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

    # ------------------------------------------------------
    # Verifica ordem de serviço
    # ------------------------------------------------------

    result = await session.execute(
        select(OrdemServicoModel).where(
            OrdemServicoModel.id == tempo.ordem_servico_id
        )
    )

    ordem = result.scalar_one_or_none()

    if not ordem:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    # ------------------------------------------------------
    # Salva registro
    # ------------------------------------------------------

    session.add(tempo)

    await session.commit()

    await session.refresh(tempo)

    return tempo


# ==========================================================
# LISTAR TEMPOS DE EXECUÇÃO
# ==========================================================

@router.get(
    "/",
    response_model=List[TempoExecucaoServicoModel]
)
async def listar_tempos_execucao(
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(TempoExecucaoServicoModel)
    )

    tempos = result.scalars().all()

    return tempos


# ==========================================================
# TEMPO MÉDIO DE UM SERVIÇO
# ==========================================================

@router.get(
    "/servico/{servico_id}/media"
)
async def tempo_medio_servico(
    servico_id: int,
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Verifica serviço
    # ------------------------------------------------------

    result = await session.execute(
        select(ServicoModel).where(
            ServicoModel.id == servico_id
        )
    )

    servico = result.scalar_one_or_none()

    if not servico:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

    # ------------------------------------------------------
    # Calcula média
    # ------------------------------------------------------

    result = await session.execute(
        select(
            func.avg(
                TempoExecucaoServicoModel.tempo_execucao_minutos
            )
        ).where(
            TempoExecucaoServicoModel.servico_id == servico_id,
            TempoExecucaoServicoModel.tempo_execucao_minutos.is_not(None)
        )
    )

    media = result.scalar()

    if media is None:

        return {
            "servico_id": servico_id,
            "servico": servico.nome,
            "tempo_medio_minutos": 0,
            "quantidade_execucoes": 0
        }

    # ------------------------------------------------------
    # Quantidade de execuções
    # ------------------------------------------------------

    result = await session.execute(
        select(
            func.count(TempoExecucaoServicoModel.id)
        ).where(
            TempoExecucaoServicoModel.servico_id == servico_id,
            TempoExecucaoServicoModel.tempo_execucao_minutos.is_not(None)
        )
    )

    quantidade = result.scalar()

    return {
        "servico_id": servico_id,
        "servico": servico.nome,
        "tempo_medio_minutos": round(float(media), 2),
        "quantidade_execucoes": quantidade
    }


# ==========================================================
# TEMPO MÉDIO GERAL
# ==========================================================

@router.get(
    "/media"
)
async def tempo_medio_geral(
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(
            func.avg(
                TempoExecucaoServicoModel.tempo_execucao_minutos
            )
        ).where(
            TempoExecucaoServicoModel.tempo_execucao_minutos.is_not(None)
        )
    )

    media = result.scalar()

    result = await session.execute(
        select(
            func.count(TempoExecucaoServicoModel.id)
        ).where(
            TempoExecucaoServicoModel.tempo_execucao_minutos.is_not(None)
        )
    )

    quantidade = result.scalar()

    return {
        "tempo_medio_minutos": (
            round(float(media), 2)
            if media is not None
            else 0
        ),
        "quantidade_execucoes": quantidade
    }