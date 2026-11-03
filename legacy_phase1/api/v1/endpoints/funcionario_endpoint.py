from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import select

from core.database import get_session
from core.security import verificar_perfis

from models.funcionario_model import FuncionarioModel
from models.unidade_model import UnidadeModel


router = APIRouter()


# ==========================================================
# CRIAR FUNCIONÁRIO
# ==========================================================

@router.post(
    "/",
    response_model=FuncionarioModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_funcionario(
    funcionario: FuncionarioModel,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Verifica se a unidade existe
    # ------------------------------------------------------

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == funcionario.unidade_id
        )
    )

    unidade = result.scalar_one_or_none()

    if not unidade:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )

    # ------------------------------------------------------
    # Verifica CPF duplicado
    # ------------------------------------------------------

    result = await session.execute(
        select(FuncionarioModel).where(
            FuncionarioModel.cpf == funcionario.cpf
        )
    )

    funcionario_existente = result.scalar_one_or_none()

    if funcionario_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um funcionário cadastrado com este CPF"
        )

    # ------------------------------------------------------
    # Salva funcionário
    # ------------------------------------------------------

    session.add(funcionario)

    await session.commit()

    await session.refresh(funcionario)

    return funcionario


# ==========================================================
# LISTAR FUNCIONÁRIOS
# ==========================================================

@router.get(
    "/",
    response_model=List[FuncionarioModel]
)
async def listar_funcionarios(
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(FuncionarioModel).where(
            FuncionarioModel.ativo == True
        )
    )

    funcionarios = result.scalars().all()

    return funcionarios


# ==========================================================
# BUSCAR FUNCIONÁRIO POR ID
# ==========================================================

@router.get(
    "/{funcionario_id}",
    response_model=FuncionarioModel
)
async def buscar_funcionario(
    funcionario_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(FuncionarioModel).where(
            FuncionarioModel.id == funcionario_id
        )
    )

    funcionario = result.scalar_one_or_none()

    if not funcionario:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )

    return funcionario


# ==========================================================
# ATUALIZAR FUNCIONÁRIO
# ==========================================================

@router.put(
    "/{funcionario_id}",
    response_model=FuncionarioModel
)
async def atualizar_funcionario(
    funcionario_id: int,
    dados: FuncionarioModel,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca funcionário
    # ------------------------------------------------------

    result = await session.execute(
        select(FuncionarioModel).where(
            FuncionarioModel.id == funcionario_id
        )
    )

    funcionario = result.scalar_one_or_none()

    if not funcionario:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )

    # ------------------------------------------------------
    # Verifica unidade
    # ------------------------------------------------------

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == dados.unidade_id
        )
    )

    unidade = result.scalar_one_or_none()

    if not unidade:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )

    # ------------------------------------------------------
    # Atualiza dados
    # ------------------------------------------------------

    funcionario.nome = dados.nome
    funcionario.cpf = dados.cpf
    funcionario.telefone = dados.telefone
    funcionario.email = dados.email
    funcionario.cargo = dados.cargo
    funcionario.unidade_id = dados.unidade_id
    funcionario.ativo = dados.ativo

    session.add(funcionario)

    await session.commit()

    await session.refresh(funcionario)

    return funcionario


# ==========================================================
# INATIVAR FUNCIONÁRIO
# ==========================================================

@router.patch(
    "/{funcionario_id}/inativar",
    response_model=FuncionarioModel
)
async def inativar_funcionario(
    funcionario_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(FuncionarioModel).where(
            FuncionarioModel.id == funcionario_id
        )
    )

    funcionario = result.scalar_one_or_none()

    if not funcionario:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )

    funcionario.ativo = False

    session.add(funcionario)

    await session.commit()

    await session.refresh(funcionario)

    return funcionario
