from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)
from jose import JWTError, jwt
from passlib.context import CryptContext


# ==========================================================
# JWT
# ==========================================================

SECRET_KEY = "oficina-mecanica-secret-key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ==========================================================
# SENHA
# ==========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Gera o hash da senha.
    """

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verifica se a senha informada corresponde
    ao hash armazenado.
    """

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ==========================================================
# CPF / CNPJ
# ==========================================================

def somente_digitos(documento: str) -> str:
    """
    Remove máscara e mantém somente os números.

    Exemplo:

    529.982.247-25
    ->
    52998224725
    """

    return "".join(
        char for char in documento
        if char.isdigit()
    )


def validar_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro.

    Aceita CPF com ou sem máscara.
    """

    cpf = somente_digitos(cpf)

    # CPF precisa ter 11 dígitos
    if len(cpf) != 11:
        return False

    # Rejeita sequências como:
    # 11111111111
    # 22222222222
    # etc.
    if cpf == cpf[0] * 11:
        return False

    # ------------------------------------------------------
    # Primeiro dígito verificador
    # ------------------------------------------------------

    soma = 0

    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    resto = soma % 11

    if resto < 2:
        digito_1 = 0
    else:
        digito_1 = 11 - resto

    if int(cpf[9]) != digito_1:
        return False

    # ------------------------------------------------------
    # Segundo dígito verificador
    # ------------------------------------------------------

    soma = 0

    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    resto = soma % 11

    if resto < 2:
        digito_2 = 0
    else:
        digito_2 = 11 - resto

    if int(cpf[10]) != digito_2:
        return False

    return True


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ brasileiro.

    Aceita CNPJ com ou sem máscara.
    """

    cnpj = somente_digitos(cnpj)

    # CNPJ precisa ter 14 dígitos
    if len(cnpj) != 14:
        return False

    # Rejeita sequências como:
    # 11111111111111
    # 22222222222222
    # etc.
    if cnpj == cnpj[0] * 14:
        return False

    # ------------------------------------------------------
    # Primeiro dígito verificador
    # ------------------------------------------------------

    pesos_1 = [
        5, 4, 3, 2,
        9, 8, 7, 6,
        5, 4, 3, 2
    ]

    soma = 0

    for i in range(12):
        soma += int(cnpj[i]) * pesos_1[i]

    resto = soma % 11

    if resto < 2:
        digito_1 = 0
    else:
        digito_1 = 11 - resto

    if int(cnpj[12]) != digito_1:
        return False

    # ------------------------------------------------------
    # Segundo dígito verificador
    # ------------------------------------------------------

    pesos_2 = [
        6, 5, 4, 3, 2,
        9, 8, 7, 6, 5,
        4, 3, 2
    ]

    soma = 0

    for i in range(13):
        soma += int(cnpj[i]) * pesos_2[i]

    resto = soma % 11

    if resto < 2:
        digito_2 = 0
    else:
        digito_2 = 11 - resto

    if int(cnpj[13]) != digito_2:
        return False

    return True


def validar_cpf_cnpj(documento: str) -> bool:
    """
    Identifica automaticamente se o documento
    é CPF ou CNPJ e valida.

    CPF:
    11 dígitos

    CNPJ:
    14 dígitos
    """

    documento = somente_digitos(documento)

    if len(documento) == 11:
        return validar_cpf(documento)

    if len(documento) == 14:
        return validar_cnpj(documento)

    return False


def normalizar_cpf_cnpj(documento: str) -> str:
    """
    Remove máscara do CPF/CNPJ.

    Exemplo:

    529.982.247-25
    ->
    52998224725
    """

    return somente_digitos(documento)


# ==========================================================
# JWT - CRIAÇÃO
# ==========================================================

def create_access_token(
    data: dict
) -> str:
    """
    Cria um token JWT com tempo de expiração.
    """

    to_encode = data.copy()

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================================================
# JWT - VALIDAÇÃO
# ==========================================================

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
) -> dict:
    """
    Valida o token JWT enviado no header Authorization.

    Formato esperado:

    Authorization: Bearer <token>
    """

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        usuario = payload.get("sub")
        perfil = payload.get("perfil")

        if usuario is None:
            raise credentials_exception

        if perfil is None:
            raise credentials_exception

        return {
            "usuario": usuario,
            "perfil": perfil
        }

    except JWTError:

        raise credentials_exception


# ==========================================================
# AUTORIZAÇÃO POR PERFIL
# ==========================================================

def verificar_perfis(*perfis_permitidos):

    async def verificar(
        current_user: dict = Depends(
            get_current_user
        )
    ) -> dict:

        if current_user["perfil"] not in perfis_permitidos:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Usuário sem permissão "
                    "para realizar esta operação"
                )
            )

        return current_user

    return verificar
