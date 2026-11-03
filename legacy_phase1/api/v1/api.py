from fastapi import APIRouter

from api.v1.endpoints import auth_endpoint
from api.v1.endpoints import unidade_endpoint
from api.v1.endpoints import funcionario_endpoint
from api.v1.endpoints import servico_endpoint
from api.v1.endpoints import cliente_endpoint
from api.v1.endpoints import veiculo_endpoint
from api.v1.endpoints import peca_endpoint
from api.v1.endpoints import ordem_servico_endpoint
from api.v1.endpoints import orcamento_endpoint
from api.v1.endpoints import acompanhamento_ordem_servico_endpoint
from api.v1.endpoints import tempo_execucao_servico_endpoint


api_router = APIRouter()


# ==========================================================
# 01 - AUTENTICAÇÃO
# ==========================================================

api_router.include_router(
    auth_endpoint.router,
    prefix="/auth",
    tags=["ordem_01 - Autenticação"]
)


# ==========================================================
# 02 - UNIDADES
# ==========================================================

api_router.include_router(
    unidade_endpoint.router,
    prefix="/unidades",
    tags=["ordem_02 - Unidades"]
)


# ==========================================================
# 03 - FUNCIONÁRIOS
# ==========================================================

api_router.include_router(
    funcionario_endpoint.router,
    prefix="/funcionarios",
    tags=["ordem_03 - Funcionários"]
)


# ==========================================================
# 04 - SERVIÇOS
# ==========================================================

api_router.include_router(
    servico_endpoint.router,
    prefix="/servicos",
    tags=["ordem_04 - Serviços"]
)


# ==========================================================
# 05 - CLIENTES
# ==========================================================

api_router.include_router(
    cliente_endpoint.router,
    prefix="/clientes",
    tags=["ordem_05 - Clientes"]
)


# ==========================================================
# 06 - VEÍCULOS
# ==========================================================

api_router.include_router(
    veiculo_endpoint.router,
    prefix="/veiculos",
    tags=["ordem_06 - Veículos"]
)


# ==========================================================
# 07 - PEÇAS / ESTOQUE
# ==========================================================

api_router.include_router(
    peca_endpoint.router,
    prefix="/pecas",
    tags=["ordem_07 - Peças / Estoque"]
)


# ==========================================================
# 08 - ORDENS DE SERVIÇO
# ==========================================================

api_router.include_router(
    ordem_servico_endpoint.router,
    prefix="/ordens-servico",
    tags=["ordem_08 - Ordens de Serviço"]
)


# ==========================================================
# 09 - ORÇAMENTOS
# ==========================================================

api_router.include_router(
    orcamento_endpoint.router,
    prefix="/orcamentos",
    tags=["ordem_09 - Orçamentos"]
)


# ==========================================================
# 10 - ACOMPANHAMENTO DA ORDEM DE SERVIÇO
# ==========================================================

api_router.include_router(
    acompanhamento_ordem_servico_endpoint.router,
    prefix="/acompanhamento",
    tags=["ordem_10 - Acompanhamento da Ordem de Serviço"]
)


# ==========================================================
# 11 - MONITORAMENTO DO TEMPO DE EXECUÇÃO DOS SERVIÇOS
# ==========================================================

api_router.include_router(
    tempo_execucao_servico_endpoint.router,
    prefix="/tempo-execucao",
    tags=["ordem_11 - Tempo de Execução dos Serviços"]
)