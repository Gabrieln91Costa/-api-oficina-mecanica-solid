from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.security import verificar_perfis

from models.unidade_model import UnidadeModel


router = APIRouter()


# ==========================================================
# CADASTRAR UNIDADE
# ==========================================================

@router.post(
    "/",
    response_model=UnidadeModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_unidade(
    unidade: UnidadeModel,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # Verifica se já existe uma unidade com o mesmo CNPJ
    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.cnpj == unidade.cnpj
        )
    )

    unidade_existente = result.scalar_one_or_none()

    if unidade_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma unidade com este CNPJ"
        )

    session.add(unidade)

    await session.commit()

    await session.refresh(unidade)

    return unidade


# ==========================================================
# LISTAR UNIDADES
# ==========================================================

@router.get(
    "/",
    response_model=List[UnidadeModel]
)
async def listar_unidades(
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(UnidadeModel)
    )

    unidades = result.scalars().all()

    return unidades


# ==========================================================
# BUSCAR UNIDADE POR ID
# ==========================================================

@router.get(
    "/{unidade_id}",
    response_model=UnidadeModel
)
async def buscar_unidade(
    unidade_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

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

    return unidade


# ==========================================================
# ALTERAR UNIDADE
# ==========================================================

@router.put(
    "/{unidade_id}",
    response_model=UnidadeModel
)
async def atualizar_unidade(
    unidade_id: int,
    unidade: UnidadeModel,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == unidade_id
        )
    )

    unidade_db = result.scalar_one_or_none()

    if not unidade_db:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )

    unidade_db.nome = unidade.nome
    unidade_db.cnpj = unidade.cnpj
    unidade_db.endereco = unidade.endereco
    unidade_db.cidade = unidade.cidade
    unidade_db.estado = unidade.estado
    unidade_db.telefone = unidade.telefone
    unidade_db.ativo = unidade.ativo

    session.add(unidade_db)

    await session.commit()

    await session.refresh(unidade_db)

    return unidade_db


# ==========================================================
# DESATIVAR UNIDADE
# ==========================================================

@router.delete(
    "/{unidade_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def desativar_unidade(
    unidade_id: int,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

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

    unidade.ativo = False

    session.add(unidade)

    await session.commit()

    return None
