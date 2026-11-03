from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.security import verificar_perfis

from models.cliente_model import ClienteModel
from models.unidade_model import UnidadeModel


router = APIRouter()


# ==========================================================
# CADASTRAR CLIENTE
# ==========================================================

@router.post(
    "/",
    response_model=ClienteModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_cliente(
    cliente: ClienteModel,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Verifica se a unidade existe
    # ------------------------------------------------------

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == cliente.unidade_id
        )
    )

    unidade = result.scalar_one_or_none()

    if not unidade:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )

    # ------------------------------------------------------
    # Verifica se a unidade está ativa
    # ------------------------------------------------------

    if not unidade.ativo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cadastrar cliente em uma unidade inativa"
        )

    # ------------------------------------------------------
    # Verifica CPF/CNPJ duplicado
    # ------------------------------------------------------

    result = await session.execute(
        select(ClienteModel).where(
            ClienteModel.cpf_cnpj == cliente.cpf_cnpj
        )
    )

    cliente_existente = result.scalar_one_or_none()

    if cliente_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um cliente com este CPF/CNPJ"
        )

    # ------------------------------------------------------
    # Cadastra cliente
    # ------------------------------------------------------

    session.add(cliente)

    await session.commit()

    await session.refresh(cliente)

    return cliente


# ==========================================================
# LISTAR CLIENTES
# ==========================================================

@router.get(
    "/",
    response_model=List[ClienteModel]
)
async def listar_clientes(
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(ClienteModel)
    )

    clientes = result.scalars().all()

    return clientes


# ==========================================================
# BUSCAR CLIENTE POR ID
# ==========================================================

@router.get(
    "/{cliente_id}",
    response_model=ClienteModel
)
async def buscar_cliente(
    cliente_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(ClienteModel).where(
            ClienteModel.id == cliente_id
        )
    )

    cliente = result.scalar_one_or_none()

    if not cliente:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    return cliente


# ==========================================================
# ALTERAR CLIENTE
# ==========================================================

@router.put(
    "/{cliente_id}",
    response_model=ClienteModel
)
async def atualizar_cliente(
    cliente_id: int,
    cliente: ClienteModel,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca cliente
    # ------------------------------------------------------

    result = await session.execute(
        select(ClienteModel).where(
            ClienteModel.id == cliente_id
        )
    )

    cliente_db = result.scalar_one_or_none()

    if not cliente_db:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    # ------------------------------------------------------
    # Verifica unidade
    # ------------------------------------------------------

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == cliente.unidade_id
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
            detail="Não é possível vincular o cliente a uma unidade inativa"
        )

    # ------------------------------------------------------
    # Verifica CPF/CNPJ em outro cliente
    # ------------------------------------------------------

    result = await session.execute(
        select(ClienteModel).where(
            ClienteModel.cpf_cnpj == cliente.cpf_cnpj,
            ClienteModel.id != cliente_id
        )
    )

    cliente_existente = result.scalar_one_or_none()

    if cliente_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe outro cliente com este CPF/CNPJ"
        )

    # ------------------------------------------------------
    # Atualiza dados
    # ------------------------------------------------------

    cliente_db.nome = cliente.nome
    cliente_db.cpf_cnpj = cliente.cpf_cnpj
    cliente_db.telefone = cliente.telefone
    cliente_db.email = cliente.email
    cliente_db.endereco = cliente.endereco
    cliente_db.cidade = cliente.cidade
    cliente_db.estado = cliente.estado
    cliente_db.unidade_id = cliente.unidade_id
    cliente_db.ativo = cliente.ativo

    session.add(cliente_db)

    await session.commit()

    await session.refresh(cliente_db)

    return cliente_db


# ==========================================================
# DESATIVAR CLIENTE
# ==========================================================

@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def desativar_cliente(
    cliente_id: int,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca cliente
    # ------------------------------------------------------

    result = await session.execute(
        select(ClienteModel).where(
            ClienteModel.id == cliente_id
        )
    )

    cliente = result.scalar_one_or_none()

    if not cliente:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    # ------------------------------------------------------
    # Desativa cliente
    # ------------------------------------------------------

    cliente.ativo = False

    session.add(cliente)

    await session.commit()

    return None