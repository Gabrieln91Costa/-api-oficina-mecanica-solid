import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from oficina.infrastructure.persistence.database import Base, get_db
from oficina.infrastructure.persistence import models  # noqa
from oficina.presentation.api.app import create_app

@pytest.fixture
def client(monkeypatch):
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)
    def override_get_db():
        db = TestingSession()
        try: yield db
        finally: db.close()
    app = create_app(database_engine=engine, initialize_schema=False)
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setenv('WEBHOOK_TOKEN', 'test-token')
    from oficina.config import get_settings
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def cadastro_basico(client):
    cliente = client.post('/api/v1/clientes', json={
        'nome':'Cliente Teste','cpf_cnpj':'12345678901','telefone':'11999999999','email':'cliente@example.com'
    }).json()
    veiculo = client.post('/api/v1/veiculos', json={
        'cliente_id':cliente['id'],'placa':'ABC1D23','marca':'Fiat','modelo':'Argo','ano':2022
    }).json()
    servico = client.post('/api/v1/servicos', json={'nome':'Revisão','valor':'250.00'}).json()
    peca = client.post('/api/v1/pecas', json={'nome':'Filtro','codigo':'FLT-01','quantidade_estoque':10,'valor_unitario':'50.00'}).json()
    return {'cliente':cliente,'veiculo':veiculo,'servico':servico,'peca':peca}
