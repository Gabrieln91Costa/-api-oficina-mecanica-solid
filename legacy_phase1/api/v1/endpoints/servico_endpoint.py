from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.security import verificar_perfis

from models.servico_model import ServicoModel
from models.unidade_model import UnidadeModel


router = APIRouter()


# ==========================================================
# CADASTRAR SERVIÇO
# ==========================================================

@router.post(
    "/",
    response_model=ServicoModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_servico(
    servico: ServicoModel,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ======================================================
    # VERIFICA SE A UNIDADE EXISTE
    # ======================================================

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == servico.unidade_id
        )
    )

    unidade = result.scalar_one_or_none()

    if not unidade:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )

    # ======================================================
    # VERIFICA SE A UNIDADE ESTÁ ATIVA
    # ======================================================

    if not unidade.ativo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cadastrar serviço em uma unidade inativa"
        )

    # ======================================================
    # CADASTRA SERVIÇO
    # ======================================================

    session.add(servico)

    await session.commit()

    await session.refresh(servico)

    return servico


# ==========================================================
# LISTAR SERVIÇOS
# ==========================================================

@router.get(
    "/",
    response_model=List[ServicoModel]
)
async def listar_servicos(
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(ServicoModel).where(
            ServicoModel.ativo.is_(True)
        )
    )

    servicos = result.scalars().all()

    return servicos


# ==========================================================
# LISTAR SERVIÇOS DE UMA UNIDADE
# ==========================================================

@router.get(
    "/unidade/{unidade_id}",
    response_model=List[ServicoModel]
)
async def listar_servicos_unidade(
    unidade_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ======================================================
    # VERIFICA UNIDADE
    # ======================================================

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == unidade_id
        )
    )

    unidade = result.scalar_one_or_none()

    if not unidade:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )

    # ======================================================
    # BUSCA SERVIÇOS
    # ======================================================

    result = await session.execute(
        select(ServicoModel).where(
            ServicoModel.unidade_id == unidade_id,
            ServicoModel.ativo.is_(True)
        )
    )

    servicos = result.scalars().all()

    return servicos


# ==========================================================
# BUSCAR SERVIÇO POR ID
# ==========================================================

@router.get(
    "/{servico_id}",
    response_model=ServicoModel
)
async def buscar_servico(
    servico_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

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

    return servico


# ==========================================================
# ALTERAR SERVIÇO
# ==========================================================

@router.put(
    "/{servico_id}",
    response_model=ServicoModel
)
async def atualizar_servico(
    servico_id: int,
    servico: ServicoModel,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    # ======================================================
    # BUSCA SERVIÇO
    # ======================================================

    result = await session.execute(
        select(ServicoModel).where(
            ServicoModel.id == servico_id
        )
    )

    servico_db = result.scalar_one_or_none()

    if not servico_db:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

    # ======================================================
    # VERIFICA UNIDADE
    # ======================================================

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == servico.unidade_id
        )
    )

    unidade = result.scalar_one_or_none()

    if not unidade:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )

    if not unidade.ativo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A unidade informada está inativa"
        )

    # ======================================================
    # ATUALIZA
    # ======================================================

    servico_db.nome = servico.nome
    servico_db.descricao = servico.descricao
    servico_db.valor = servico.valor
    servico_db.tempo_estimado = servico.tempo_estimado
    servico_db.unidade_id = servico.unidade_id
    servico_db.ativo = servico.ativo

    session.add(servico_db)

    await session.commit()

    await session.refresh(servico_db)

    return servico_db


# ==========================================================
# DESATIVAR SERVIÇO
# ==========================================================

@router.delete(
    "/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def desativar_servico(
    servico_id: int,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

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

    servico.ativo = False

    session.add(servico)

    await session.commit()

    return None