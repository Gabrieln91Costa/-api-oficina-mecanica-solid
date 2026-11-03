import re
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
from models.veiculo_model import VeiculoModel


router = APIRouter()


# ==========================================================
# VALIDAÇÃO DA PLACA
# ==========================================================

def validar_placa(placa: str) -> str:
    """
    Valida placas no padrão:

    Antigo:
        ABC1234

    Mercosul:
        ABC1D23

    Retorna a placa normalizada sem espaços ou hífens.
    """

    if not isinstance(placa, str):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A placa deve ser informada como texto"
        )

    # Remove espaços e hífens
    placa = placa.strip().upper().replace("-", "").replace(" ", "")

    # A placa brasileira possui 7 caracteres
    if len(placa) != 7:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A placa deve possuir 7 caracteres"
        )

    # ------------------------------------------------------
    # Placa antiga: ABC1234
    # ------------------------------------------------------

    placa_antiga = re.fullmatch(
        r"[A-Z]{3}[0-9]{4}",
        placa
    )

    # ------------------------------------------------------
    # Placa Mercosul: ABC1D23
    # ------------------------------------------------------

    placa_mercosul = re.fullmatch(
        r"[A-Z]{3}[0-9][A-Z][0-9]{2}",
        placa
    )

    if not placa_antiga and not placa_mercosul:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Placa inválida. "
                "Utilize o formato ABC1234 ou ABC1D23"
            )
        )

    return placa


# ==========================================================
# CADASTRAR VEÍCULO
# ==========================================================

@router.post(
    "/",
    response_model=VeiculoModel,
    status_code=status.HTTP_201_CREATED
)
async def criar_veiculo(
    veiculo: VeiculoModel,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Valida placa
    # ------------------------------------------------------

    veiculo.placa = validar_placa(
        veiculo.placa
    )

    # ------------------------------------------------------
    # Verifica cliente
    # ------------------------------------------------------

    result = await session.execute(
        select(ClienteModel).where(
            ClienteModel.id == veiculo.cliente_id
        )
    )

    cliente = result.scalar_one_or_none()

    if not cliente:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )

    # ------------------------------------------------------
    # Verifica se cliente está ativo
    # ------------------------------------------------------

    if not cliente.ativo:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cadastrar veículo para cliente inativo"
        )

    # ------------------------------------------------------
    # Verifica placa duplicada
    # ------------------------------------------------------

    result = await session.execute(
        select(VeiculoModel).where(
            VeiculoModel.placa == veiculo.placa
        )
    )

    veiculo_existente = result.scalar_one_or_none()

    if veiculo_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um veículo cadastrado com esta placa"
        )

    # ------------------------------------------------------
    # Valida ano
    # ------------------------------------------------------

    if veiculo.ano < 1900 or veiculo.ano > 2100:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ano do veículo inválido"
        )

    # ------------------------------------------------------
    # Cadastra veículo
    # ------------------------------------------------------

    session.add(veiculo)

    await session.commit()

    await session.refresh(veiculo)

    return veiculo


# ==========================================================
# LISTAR VEÍCULOS
# ==========================================================

@router.get(
    "/",
    response_model=List[VeiculoModel]
)
async def listar_veiculos(
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(VeiculoModel)
    )

    veiculos = result.scalars().all()

    return veiculos


# ==========================================================
# LISTAR VEÍCULOS DE UM CLIENTE
# ==========================================================

@router.get(
    "/cliente/{cliente_id}",
    response_model=List[VeiculoModel]
)
async def listar_veiculos_cliente(
    cliente_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Verifica cliente
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
    # Busca veículos
    # ------------------------------------------------------

    result = await session.execute(
        select(VeiculoModel).where(
            VeiculoModel.cliente_id == cliente_id
        )
    )

    veiculos = result.scalars().all()

    return veiculos


# ==========================================================
# BUSCAR VEÍCULO POR ID
# ==========================================================

@router.get(
    "/{veiculo_id}",
    response_model=VeiculoModel
)
async def buscar_veiculo(
    veiculo_id: int,
    current_user: dict = Depends(
        verificar_perfis(
            "GESTOR",
            "FUNCIONARIO"
        )
    ),
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(VeiculoModel).where(
            VeiculoModel.id == veiculo_id
        )
    )

    veiculo = result.scalar_one_or_none()

    if not veiculo:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )

    return veiculo


# ==========================================================
# ALTERAR VEÍCULO
# ==========================================================

@router.put(
    "/{veiculo_id}",
    response_model=VeiculoModel
)
async def atualizar_veiculo(
    veiculo_id: int,
    veiculo: VeiculoModel,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca veículo
    # ------------------------------------------------------

    result = await session.execute(
        select(VeiculoModel).where(
            VeiculoModel.id == veiculo_id
        )
    )

    veiculo_db = result.scalar_one_or_none()

    if not veiculo_db:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )

    # ------------------------------------------------------
    # Valida placa
    # ------------------------------------------------------

    placa = validar_placa(
        veiculo.placa
    )

    # ------------------------------------------------------
    # Verifica cliente
    # ------------------------------------------------------

    result = await session.execute(
        select(ClienteModel).where(
            ClienteModel.id == veiculo.cliente_id
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
            detail="Não é possível vincular o veículo a um cliente inativo"
        )

    # ------------------------------------------------------
    # Verifica placa em outro veículo
    # ------------------------------------------------------

    result = await session.execute(
        select(VeiculoModel).where(
            VeiculoModel.placa == placa,
            VeiculoModel.id != veiculo_id
        )
    )

    veiculo_existente = result.scalar_one_or_none()

    if veiculo_existente:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe outro veículo com esta placa"
        )

    # ------------------------------------------------------
    # Valida ano
    # ------------------------------------------------------

    if veiculo.ano < 1900 or veiculo.ano > 2100:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ano do veículo inválido"
        )

    # ------------------------------------------------------
    # Atualiza veículo
    # ------------------------------------------------------

    veiculo_db.placa = placa
    veiculo_db.marca = veiculo.marca
    veiculo_db.modelo = veiculo.modelo
    veiculo_db.ano = veiculo.ano
    veiculo_db.cliente_id = veiculo.cliente_id
    veiculo_db.ativo = veiculo.ativo

    session.add(veiculo_db)

    await session.commit()

    await session.refresh(veiculo_db)

    return veiculo_db


# ==========================================================
# DESATIVAR VEÍCULO
# ==========================================================

@router.delete(
    "/{veiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def desativar_veiculo(
    veiculo_id: int,
    current_user: dict = Depends(
        verificar_perfis("GESTOR")
    ),
    session: AsyncSession = Depends(get_session)
):

    # ------------------------------------------------------
    # Busca veículo
    # ------------------------------------------------------

    result = await session.execute(
        select(VeiculoModel).where(
            VeiculoModel.id == veiculo_id
        )
    )

    veiculo = result.scalar_one_or_none()

    if not veiculo:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )

    # ------------------------------------------------------
    # Desativa
    # ------------------------------------------------------

    veiculo.ativo = False

    session.add(veiculo)

    await session.commit()

    return None
