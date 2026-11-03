from datetime import date
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.security import verificar_perfis

from models.orcamento_model import OrcamentoModel
from models.ordem_servico_model import OrdemServicoModel
from models.servico_model import ServicoModel
from models.peca_model import PecaModel


router = APIRouter()


# ==========================================================
# CRIAR ORÇAMENTO
# ==========================================================

@router.post(
    "/",
    response_model=OrcamentoModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_orcamento(
    orcamento: OrcamentoModel,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca ordem de serviço
    # ------------------------------------------------------

    result = await session.execute(
        select(OrdemServicoModel).where(
            OrdemServicoModel.id == orcamento.ordem_servico_id
        )
    )

    ordem = result.scalar_one_or_none()

    if not ordem:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )

    # ------------------------------------------------------
    # Verifica se a OS está ativa
    # ------------------------------------------------------

    if not ordem.ativo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível criar orçamento para uma OS inativa"
        )

    # ------------------------------------------------------
    # Verifica se já existe orçamento para a OS
    # ------------------------------------------------------

    result = await session.execute(
        select(OrcamentoModel).where(
            OrcamentoModel.ordem_servico_id
            == orcamento.ordem_servico_id
        )
    )

    orcamento_existente = result.scalar_one_or_none()

    if orcamento_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um orçamento para esta ordem de serviço"
        )

    # ------------------------------------------------------
    # Busca serviço da OS
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
            detail="Serviço da ordem de serviço não encontrado"
        )

    # ------------------------------------------------------
    # Verifica se o serviço pertence à mesma unidade da OS
    # ------------------------------------------------------

    if servico.unidade_id != ordem.unidade_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O serviço não pertence à unidade da ordem de serviço"
        )

    # ------------------------------------------------------
    # Calcula valor dos serviços
    # ------------------------------------------------------

    valor_servicos = float(
        servico.valor
    )

    # ------------------------------------------------------
    # Calcula valor da peça
    # ------------------------------------------------------

    valor_pecas = 0.0

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
                detail="Peça da ordem de serviço não encontrada"
            )

        # --------------------------------------------------
        # Verifica se a peça pertence à mesma unidade
        # --------------------------------------------------

        if peca.unidade_id != ordem.unidade_id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A peça não pertence à unidade da ordem de serviço"
            )

        # --------------------------------------------------
        # Valor correto da peça
        # --------------------------------------------------

        valor_pecas = float(
            peca.valor_unitario
        )

    # ------------------------------------------------------
    # Valida desconto
    # ------------------------------------------------------

    if float(orcamento.desconto) < 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O desconto não pode ser negativo"
        )

    # ------------------------------------------------------
    # Valida acréscimo
    # ------------------------------------------------------

    if float(orcamento.acrescimo) < 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O acréscimo não pode ser negativo"
        )

    # ------------------------------------------------------
    # Calcula valor total
    # ------------------------------------------------------

    valor_total = (
        valor_servicos
        + valor_pecas
        + float(orcamento.acrescimo)
        - float(orcamento.desconto)
    )

    # ------------------------------------------------------
    # Impede valor total negativo
    # ------------------------------------------------------

    if valor_total < 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O valor total do orçamento não pode ser negativo"
        )

    # ------------------------------------------------------
    # Valida validade do orçamento
    # ------------------------------------------------------

    if orcamento.validade < date.today():

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A validade do orçamento não pode ser anterior à data atual"
        )

    # ------------------------------------------------------
    # Preenche valores calculados
    # ------------------------------------------------------

    orcamento.valor_servicos = valor_servicos

    orcamento.valor_pecas = valor_pecas

    orcamento.valor_total = valor_total

    orcamento.status = "AGUARDANDO_APROVACAO"

    # ------------------------------------------------------
    # Campos controlados pelo sistema
    # ------------------------------------------------------

    orcamento.data_aprovacao = None
    orcamento.aprovado_por = None

    # ------------------------------------------------------
    # Salva orçamento
    # ------------------------------------------------------

    session.add(orcamento)

    await session.commit()

    await session.refresh(orcamento)

    return orcamento


# ==========================================================
# LISTAR ORÇAMENTOS
# ==========================================================

@router.get(
    "/",
    response_model=List[OrcamentoModel]
)
async def listar_orcamentos(
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(OrcamentoModel)
    )

    orcamentos = result.scalars().all()

    return orcamentos


# ==========================================================
# BUSCAR ORÇAMENTO POR ID
# ==========================================================

@router.get(
    "/{orcamento_id}",
    response_model=OrcamentoModel
)
async def buscar_orcamento(
    orcamento_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(OrcamentoModel).where(
            OrcamentoModel.id == orcamento_id
        )
    )

    orcamento = result.scalar_one_or_none()

    if not orcamento:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )

    return orcamento


# ==========================================================
# APROVAR ORÇAMENTO
# ==========================================================

@router.patch(
    "/{orcamento_id}/aprovar",
    response_model=OrcamentoModel
)
async def aprovar_orcamento(
    orcamento_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(OrcamentoModel).where(
            OrcamentoModel.id == orcamento_id
        )
    )

    orcamento = result.scalar_one_or_none()

    if not orcamento:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )

    if orcamento.status != "AGUARDANDO_APROVACAO":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Orçamento não está aguardando aprovação"
        )

    orcamento.status = "APROVADO"

    orcamento.data_aprovacao = date.today()

    orcamento.aprovado_por = current_user["usuario"]

    session.add(orcamento)

    await session.commit()

    await session.refresh(orcamento)

    return orcamento


# ==========================================================
# REJEITAR ORÇAMENTO
# ==========================================================

@router.patch(
    "/{orcamento_id}/rejeitar",
    response_model=OrcamentoModel
)
async def rejeitar_orcamento(
    orcamento_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(OrcamentoModel).where(
            OrcamentoModel.id == orcamento_id
        )
    )

    orcamento = result.scalar_one_or_none()

    if not orcamento:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )

    if orcamento.status != "AGUARDANDO_APROVACAO":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Orçamento não está aguardando aprovação"
        )

    orcamento.status = "REJEITADO"

    session.add(orcamento)

    await session.commit()

    await session.refresh(orcamento)

    return orcamento
