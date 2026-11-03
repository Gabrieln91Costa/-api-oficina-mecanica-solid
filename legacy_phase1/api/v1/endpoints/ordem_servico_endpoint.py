from datetime import date, time
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.security import verificar_perfis

from models.ordem_servico_model import OrdemServicoModel
from models.unidade_model import UnidadeModel
from models.cliente_model import ClienteModel
from models.servico_model import ServicoModel
from models.peca_model import PecaModel


router = APIRouter()


# ==========================================================
# CRIAR ORDEM DE SERVIÇO
# ==========================================================

@router.post(
    "/",
    response_model=OrdemServicoModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_ordem_servico(
    ordem: OrdemServicoModel,
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
            UnidadeModel.id == ordem.unidade_id
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
            detail="A unidade está inativa"
        )

    # ------------------------------------------------------
    # Verifica se o cliente existe
    # ------------------------------------------------------

    result = await session.execute(
        select(ClienteModel).where(
            ClienteModel.id == ordem.cliente_id
        )
    )

    cliente = result.scalar_one_or_none()

    if not cliente:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    if not cliente.ativo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O cliente está inativo"
        )

    # ------------------------------------------------------
    # Verifica se cliente pertence à unidade
    # ------------------------------------------------------

    if cliente.unidade_id != ordem.unidade_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O cliente não pertence à unidade informada"
        )

    # ------------------------------------------------------
    # Verifica se o serviço existe
    # ------------------------------------------------------

    result = await session.execute(
        select(ServicoModel).where(
            ServicoModel.id == ordem.servico_id
        )
    )

    servico = result.scalar_one_or_none()

    if not servico:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

    if not servico.ativo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O serviço está inativo"
        )

    # ------------------------------------------------------
    # Verifica se serviço pertence à unidade
    # ------------------------------------------------------

    if servico.unidade_id != ordem.unidade_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O serviço não pertence à unidade informada"
        )

    # ------------------------------------------------------
    # Verifica peça, caso informada
    # ------------------------------------------------------

    if ordem.peca_id is not None:

        result = await session.execute(
            select(PecaModel).where(
                PecaModel.id == ordem.peca_id
            )
        )

        peca = result.scalar_one_or_none()

        if not peca:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peça não encontrada"
            )

        if not peca.ativo:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A peça está inativa"
            )

        if peca.unidade_id != ordem.unidade_id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A peça não pertence à unidade informada"
            )

        if peca.quantidade_estoque <= 0:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A peça não possui estoque disponível"
            )

    # ------------------------------------------------------
    # Verifica número da OS duplicado
    # ------------------------------------------------------

    result = await session.execute(
        select(OrdemServicoModel).where(
            OrdemServicoModel.numero_ordem
            == ordem.numero_ordem
        )
    )

    ordem_existente = result.scalar_one_or_none()

    if ordem_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma ordem de serviço com este número"
        )

    # ------------------------------------------------------
    # Define status inicial
    # ------------------------------------------------------

    ordem.status = "A SER APROVADA"

    # ------------------------------------------------------
    # Salva OS
    # ------------------------------------------------------

    session.add(ordem)

    await session.commit()

    await session.refresh(ordem)

    return ordem


# ==========================================================
# LISTAR ORDENS DE SERVIÇO
# ==========================================================

@router.get(
    "/",
    response_model=List[OrdemServicoModel]
)
async def listar_ordens_servico(
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(OrdemServicoModel)
    )

    return result.scalars().all()


# ==========================================================
# BUSCAR ORDEM DE SERVIÇO
# ==========================================================

@router.get(
    "/{ordem_id}",
    response_model=OrdemServicoModel
)
async def buscar_ordem_servico(
    ordem_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(OrdemServicoModel).where(
            OrdemServicoModel.id == ordem_id
        )
    )

    ordem = result.scalar_one_or_none()

    if not ordem:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    return ordem


# ==========================================================
# ALTERAR STATUS
# ==========================================================

@router.patch(
    "/{ordem_id}/status",
    response_model=OrdemServicoModel
)
async def alterar_status_ordem(
    ordem_id: int,
    novo_status: str,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    status_permitidos = [
        "A SER APROVADA",
        "RECEBIDA",
        "EM DIAGNOSTICO",
        "AGUARDANDO APROVACAO",
        "EM EXECUCAO",
        "FINALIZADA",
        "ENTREGUE"
    ]

    if novo_status not in status_permitidos:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status inválido"
        )

    result = await session.execute(
        select(OrdemServicoModel).where(
            OrdemServicoModel.id == ordem_id
        )
    )

    ordem = result.scalar_one_or_none()

    if not ordem:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    ordem.status = novo_status

    session.add(ordem)

    await session.commit()

    await session.refresh(ordem)

    return ordem


# ==========================================================
# DESATIVAR ORDEM DE SERVIÇO
# ==========================================================

@router.delete(
    "/{ordem_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def desativar_ordem_servico(
    ordem_id: int,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(OrdemServicoModel).where(
            OrdemServicoModel.id == ordem_id
        )
    )

    ordem = result.scalar_one_or_none()

    if not ordem:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    ordem.ativo = False

    session.add(ordem)

    await session.commit()

    return None