from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.security import (
    create_access_token,
    hash_password,
    verify_password
)
from models.usuario_model import UsuarioModel


router = APIRouter()


@router.post("/default")
async def criar_usuario_default(
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(UsuarioModel).where(
            UsuarioModel.usuario == "adm"
        )
    )

    usuario = result.scalar_one_or_none()

    if usuario:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Usuário adm já existe"
        )

    usuario = UsuarioModel(
        usuario="adm",
        senha=hash_password("adm"),
        nome="Administrador",
        perfil="GESTOR",
        ativo=True
    )

    session.add(usuario)

    await session.commit()

    return {
        "message": "Usuário padrão criado com sucesso",
        "usuario": "adm",
        "perfil": "GESTOR"
    }


@router.post("/login")
async def login(
    usuario: str,
    senha: str,
    session: AsyncSession = Depends(get_session)
):

    result = await session.execute(
        select(UsuarioModel).where(
            UsuarioModel.usuario == usuario
        )
    )

    usuario_db = result.scalar_one_or_none()

    if not usuario_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos"
        )

    if not usuario_db.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    if not verify_password(
        senha,
        usuario_db.senha
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos"
        )

    access_token = create_access_token(
        {
            "sub": usuario_db.usuario,
            "perfil": usuario_db.perfil
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }