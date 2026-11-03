from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from oficina.config import get_settings
from oficina.domain.exceptions import DomainError, NotFoundError, ConflictError, InvalidTransitionError, ValidationError
from oficina.infrastructure.persistence.database import get_db
from oficina.infrastructure.persistence.repository import SqlAlchemyOficinaRepository
from oficina.infrastructure.notifications.adapters import SMTPNotifier
from oficina.application.use_cases.oficina import OficinaUseCases
from .schemas import (ClienteIn, VeiculoIn, ServicoIn, PecaIn, OrdemServicoIn, StatusUpdateIn,
    OrcamentoIn, DecisaoOrcamentoIn, WebhookStatusIn, OrdemServicoOut)

router = APIRouter()

def get_use_cases(db: Session = Depends(get_db)):
    return OficinaUseCases(SqlAlchemyOficinaRepository(db), SMTPNotifier())

def validate_webhook_token(x_webhook_token: str | None = Header(default=None)):
    expected = get_settings().webhook_token
    if not expected or expected == 'change-me':
        raise HTTPException(status_code=503, detail='Configure WEBHOOK_TOKEN antes de habilitar webhooks.')
    if x_webhook_token != expected:
        raise HTTPException(status_code=401, detail='Token de webhook inválido.')

def _handle_domain_error(exc: DomainError):
    if isinstance(exc, NotFoundError): code = 404
    elif isinstance(exc, ConflictError): code = 409
    elif isinstance(exc, InvalidTransitionError): code = 422
    elif isinstance(exc, ValidationError): code = 400
    else: code = 400
    raise HTTPException(status_code=code, detail=str(exc))

@router.post('/clientes', status_code=201)
def criar_cliente(payload: ClienteIn, db: Session = Depends(get_db)):
    try: return SqlAlchemyOficinaRepository(db).criar_cliente(payload.model_dump())
    except DomainError as exc: _handle_domain_error(exc)

@router.get('/clientes')
def listar_clientes(db: Session = Depends(get_db)):
    return SqlAlchemyOficinaRepository(db).listar_clientes()

@router.post('/veiculos', status_code=201)
def criar_veiculo(payload: VeiculoIn, db: Session = Depends(get_db)):
    try: return SqlAlchemyOficinaRepository(db).criar_veiculo(payload.model_dump())
    except DomainError as exc: _handle_domain_error(exc)

@router.get('/veiculos')
def listar_veiculos(cliente_id: int | None = None, db: Session = Depends(get_db)):
    return SqlAlchemyOficinaRepository(db).listar_veiculos(cliente_id)

@router.post('/servicos', status_code=201)
def criar_servico(payload: ServicoIn, db: Session = Depends(get_db)):
    return SqlAlchemyOficinaRepository(db).criar_servico(payload.model_dump())

@router.get('/servicos')
def listar_servicos(db: Session = Depends(get_db)):
    return SqlAlchemyOficinaRepository(db).listar_servicos()

@router.post('/pecas', status_code=201)
def criar_peca(payload: PecaIn, db: Session = Depends(get_db)):
    return SqlAlchemyOficinaRepository(db).criar_peca(payload.model_dump())

@router.get('/pecas')
def listar_pecas(db: Session = Depends(get_db)):
    return SqlAlchemyOficinaRepository(db).listar_pecas()

@router.post('/ordens-servico', status_code=201)
def abrir_os(payload: OrdemServicoIn, uc: OficinaUseCases = Depends(get_use_cases)):
    try:
        dados = payload.model_dump()
        ordem = uc.abrir_os(dados)
        return {'id': ordem.id, 'numero_ordem': ordem.numero_ordem, 'status': ordem.status, 'criado_em': ordem.criado_em}
    except DomainError as exc: _handle_domain_error(exc)

@router.get('/ordens-servico')
def listar_os(uc: OficinaUseCases = Depends(get_use_cases)):
    return [OrdemServicoOut.from_model(x) for x in uc.listar_os()]

@router.get('/ordens-servico/{ordem_id}')
def consultar_os(ordem_id: UUID, uc: OficinaUseCases = Depends(get_use_cases)):
    try:
        obj = uc.consultar_status(ordem_id)
        return {'id': obj.id, 'numero_ordem': obj.numero_ordem, 'status': obj.status, 'criado_em': obj.criado_em,
            'cliente': {'id': obj.cliente.id, 'nome': obj.cliente.nome, 'cpf_cnpj': obj.cliente.cpf_cnpj},
            'veiculo': {'id': obj.veiculo.id, 'placa': obj.veiculo.placa, 'marca': obj.veiculo.marca, 'modelo': obj.veiculo.modelo},
            'servicos': [{'id': x.servico.id, 'nome': x.servico.nome, 'valor': x.valor_unitario} for x in obj.servicos],
            'pecas': [{'id': x.peca.id, 'nome': x.peca.nome, 'quantidade': x.quantidade, 'valor_unitario': x.valor_unitario} for x in obj.pecas]}
    except DomainError as exc: _handle_domain_error(exc)

@router.get('/ordens-servico/{ordem_id}/status')
def consultar_status(ordem_id: UUID, uc: OficinaUseCases = Depends(get_use_cases)):
    try:
        obj = uc.consultar_status(ordem_id)
        return {'ordem_servico_id': obj.id, 'status': obj.status}
    except DomainError as exc: _handle_domain_error(exc)

@router.patch('/ordens-servico/{ordem_id}/status')
def atualizar_status(ordem_id: UUID, payload: StatusUpdateIn, uc: OficinaUseCases = Depends(get_use_cases)):
    try:
        obj = uc.atualizar_status(ordem_id, payload.status)
        return {'ordem_servico_id': obj.id, 'status': obj.status}
    except DomainError as exc: _handle_domain_error(exc)

@router.delete('/ordens-servico/{ordem_id}', status_code=204)
def excluir_os_logicamente(ordem_id: UUID, db: Session = Depends(get_db)):
    if not SqlAlchemyOficinaRepository(db).excluir_logicamente(ordem_id): raise HTTPException(404, 'OS não encontrada.')

@router.post('/ordens-servico/{ordem_id}/orcamentos', status_code=201)
def criar_orcamento(ordem_id: UUID, payload: OrcamentoIn, uc: OficinaUseCases = Depends(get_use_cases)):
    try: return uc.criar_orcamento(ordem_id, payload.model_dump())
    except DomainError as exc: _handle_domain_error(exc)

@router.post('/orcamentos/{orcamento_id}/aprovacao')
def decidir_orcamento(orcamento_id: int, payload: DecisaoOrcamentoIn, db: Session = Depends(get_db), _auth=Depends(validate_webhook_token)):
    try:
        obj = OficinaUseCases(SqlAlchemyOficinaRepository(db), SMTPNotifier()).decidir_orcamento(orcamento_id, payload.aprovado, payload.ator)
        return {'id': obj.id, 'status': obj.status, 'ordem_servico_id': obj.ordem_servico_id}
    except DomainError as exc: _handle_domain_error(exc)

@router.post('/webhooks/email/status')
def webhook_email_status(payload: WebhookStatusIn, db: Session = Depends(get_db), _auth=Depends(validate_webhook_token)):
    repo = SqlAlchemyOficinaRepository(db)
    if repo.evento_existe(payload.event_id): return {'recebido': True, 'duplicado': True}
    try:
        obj = repo.atualizar_status(payload.ordem_servico_id, payload.status.value, payload.origem)
        if obj is None: raise HTTPException(404, 'OS não encontrada.')
        repo.registrar_evento(payload.event_id, payload.model_dump(mode='json'))
        return {'recebido': True, 'duplicado': False, 'ordem_servico_id': obj.id, 'status': obj.status}
    except DomainError as exc: _handle_domain_error(exc)
