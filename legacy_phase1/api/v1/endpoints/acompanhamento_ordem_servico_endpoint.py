from datetime import date
from datetime import time
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session

from models.acompanhamento_ordem_servico_model import (
    AcompanhamentoOrdemServicoModel
)

from models.ordem_servico_model import (
    OrdemServicoModel
)


router = APIRouter()


# ==========================================================
# CONSULTAR PROGRESSO DA ORDEM DE SERVIÇO
# ==========================================================

@router.get(
    "/{numero_ordem}",
    response_model=List[AcompanhamentoOrdemServicoModel]
)
async def consultar_progresso(
    numero_ordem: str,
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca ordem de serviço
    # ------------------------------------------------------

    result = await session.execute(
        select(OrdemServicoModel).where(
            OrdemServicoModel.numero_ordem == numero_ordem
        )
    )

    ordem_servico = result.scalar_one_or_none()

    if not ordem_servico:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    # ------------------------------------------------------
    # Busca histórico de acompanhamento
    # ------------------------------------------------------

    result = await session.execute(
        select(
            AcompanhamentoOrdemServicoModel
        )
        .where(
            AcompanhamentoOrdemServicoModel.ordem_servico_id
            == ordem_servico.id
        )
        .order_by(
            AcompanhamentoOrdemServicoModel.data,
            AcompanhamentoOrdemServicoModel.hora
        )
    )

    acompanhamentos = result.scalars().all()

    return acompanhamentos


# ==========================================================
# ADICIONAR ATUALIZAÇÃO DO PROGRESSO
# ==========================================================

@router.post(
    "/",
    response_model=AcompanhamentoOrdemServicoModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_acompanhamento(
    acompanhamento: AcompanhamentoOrdemServicoModel,
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Verifica se a OS existe
    # ------------------------------------------------------

    result = await session.execute(
        select(OrdemServicoModel).where(
            OrdemServicoModel.id
            == acompanhamento.ordem_servico_id
        )
    )

    ordem_servico = result.scalar_one_or_none()

    if not ordem_servico:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    # ------------------------------------------------------
    # Valida percentual
    # ------------------------------------------------------

    if acompanhamento.percentual < 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Percentual não pode ser menor que 0"
        )

    if acompanhamento.percentual > 100:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Percentual não pode ser maior que 100"
        )

    # ------------------------------------------------------
    # Salva acompanhamento
    # ------------------------------------------------------

    session.add(acompanhamento)

    await session.commit()

    await session.refresh(acompanhamento)

    return acompanhamento