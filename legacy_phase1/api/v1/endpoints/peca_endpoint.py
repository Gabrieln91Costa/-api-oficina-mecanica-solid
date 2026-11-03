from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.security import verificar_perfis

from models.peca_model import PecaModel
from models.unidade_model import UnidadeModel


router = APIRouter()


# ==========================================================
# CADASTRAR PEÇA
# ==========================================================

@router.post(
    "/",
    response_model=PecaModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_peca(
    peca: PecaModel,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Valida quantidade
    # ------------------------------------------------------

    if peca.quantidade_estoque < 0:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Quantidade em estoque não pode ser negativa"
        )

    # ------------------------------------------------------
    # Valida estoque mínimo
    # ------------------------------------------------------

    if peca.estoque_minimo < 0:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Estoque mínimo não pode ser negativo"
        )

    # ------------------------------------------------------
    # Valida valor
    # ------------------------------------------------------

    if peca.valor_unitario < 0:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Valor unitário não pode ser negativo"
        )

    # ------------------------------------------------------
    # Verifica unidade
    # ------------------------------------------------------

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == peca.unidade_id
        )
    )

    unidade = result.scalar_one_or_none()

    if not unidade:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )

    # ------------------------------------------------------
    # Verifica unidade ativa
    # ------------------------------------------------------

    if not unidade.ativo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Não é possível cadastrar peça "
                "em uma unidade inativa"
            )
        )

    # ------------------------------------------------------
    # Verifica código duplicado dentro da unidade
    # ------------------------------------------------------

    result = await session.execute(
        select(PecaModel).where(
            PecaModel.codigo == peca.codigo,
            PecaModel.unidade_id == peca.unidade_id
        )
    )

    peca_existente = result.scalar_one_or_none()

    if peca_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Já existe uma peça com este código "
                "nesta unidade"
            )
        )

    # ------------------------------------------------------
    # Cadastra peça
    # ------------------------------------------------------

    session.add(peca)

    await session.commit()

    await session.refresh(peca)

    return peca


# ==========================================================
# LISTAR PEÇAS
# ==========================================================

@router.get(
    "/",
    response_model=List[PecaModel]
)
async def listar_pecas(
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(PecaModel)
    )

    pecas = result.scalars().all()

    return pecas


# ==========================================================
# BUSCAR PEÇA POR ID
# ==========================================================

@router.get(
    "/{peca_id}",
    response_model=PecaModel
)
async def buscar_peca(
    peca_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(PecaModel).where(
            PecaModel.id == peca_id
        )
    )

    peca = result.scalar_one_or_none()

    if not peca:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )

    return peca


# ==========================================================
# LISTAR PEÇAS DE UMA UNIDADE
# ==========================================================

@router.get(
    "/unidade/{unidade_id}",
    response_model=List[PecaModel]
)
async def listar_pecas_unidade(
    unidade_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Verifica unidade
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Busca peças
    # ------------------------------------------------------

    result = await session.execute(
        select(PecaModel).where(
            PecaModel.unidade_id == unidade_id
        )
    )

    pecas = result.scalars().all()

    return pecas


# ==========================================================
# ALTERAR PEÇA
# ==========================================================

@router.put(
    "/{peca_id}",
    response_model=PecaModel
)
async def atualizar_peca(
    peca_id: int,
    peca: PecaModel,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca peça
    # ------------------------------------------------------

    result = await session.execute(
        select(PecaModel).where(
            PecaModel.id == peca_id
        )
    )

    peca_db = result.scalar_one_or_none()

    if not peca_db:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )

    # ------------------------------------------------------
    # Valida quantidade
    # ------------------------------------------------------

    if peca.quantidade_estoque < 0:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Quantidade em estoque não pode ser negativa"
        )

    # ------------------------------------------------------
    # Valida estoque mínimo
    # ------------------------------------------------------

    if peca.estoque_minimo < 0:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Estoque mínimo não pode ser negativo"
        )

    # ------------------------------------------------------
    # Valida valor
    # ------------------------------------------------------

    if peca.valor_unitario < 0:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Valor unitário não pode ser negativo"
        )

    # ------------------------------------------------------
    # Verifica unidade
    # ------------------------------------------------------

    result = await session.execute(
        select(UnidadeModel).where(
            UnidadeModel.id == peca.unidade_id
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
            detail=(
                "Não é possível vincular a peça "
                "a uma unidade inativa"
            )
        )

    # ------------------------------------------------------
    # Verifica código duplicado
    # ------------------------------------------------------

    result = await session.execute(
        select(PecaModel).where(
            PecaModel.codigo == peca.codigo,
            PecaModel.unidade_id == peca.unidade_id,
            PecaModel.id != peca_id
        )
    )

    peca_existente = result.scalar_one_or_none()

    if peca_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Já existe outra peça com este código "
                "nesta unidade"
            )
        )

    # ------------------------------------------------------
    # Atualiza
    # ------------------------------------------------------

    peca_db.nome = peca.nome
    peca_db.descricao = peca.descricao
    peca_db.codigo = peca.codigo
    peca_db.quantidade_estoque = peca.quantidade_estoque
    peca_db.estoque_minimo = peca.estoque_minimo
    peca_db.valor_unitario = peca.valor_unitario
    peca_db.unidade_id = peca.unidade_id
    peca_db.ativo = peca.ativo

    session.add(peca_db)

    await session.commit()

    await session.refresh(peca_db)

    return peca_db


# ==========================================================
# DESATIVAR PEÇA
# ==========================================================

@router.delete(
    "/{peca_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def desativar_peca(
    peca_id: int,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca peça
    # ------------------------------------------------------

    result = await session.execute(
        select(PecaModel).where(
            PecaModel.id == peca_id
        )
    )

    peca = result.scalar_one_or_none()

    if not peca:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )

    # ------------------------------------------------------
    # Desativa
    # ------------------------------------------------------

    peca.ativo = False

    session.add(peca)

    await session.commit()

    return None