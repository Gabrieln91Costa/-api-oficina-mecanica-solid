from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class ClienteModel(Base):
    __tablename__ = "clientes"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(160))
    cpf_cnpj: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

class VeiculoModel(Base):
    __tablename__ = "veiculos"
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    placa: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    marca: Mapped[str] = mapped_column(String(80))
    modelo: Mapped[str] = mapped_column(String(100))
    ano: Mapped[int] = mapped_column(Integer)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

class ServicoModel(Base):
    __tablename__ = "servicos"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(12,2))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

class PecaModel(Base):
    __tablename__ = "pecas"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    quantidade_estoque: Mapped[int] = mapped_column(Integer, default=0)
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(12,2))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

class OrdemServicoModel(Base):
    __tablename__ = "ordens_servico"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    numero_ordem: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    veiculo_id: Mapped[int] = mapped_column(ForeignKey("veiculos.id"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="RECEBIDA", index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    excluida: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    cliente: Mapped[ClienteModel] = relationship()
    veiculo: Mapped[VeiculoModel] = relationship()
    servicos: Mapped[list["OrdemServicoServicoModel"]] = relationship(cascade="all, delete-orphan")
    pecas: Mapped[list["OrdemServicoPecaModel"]] = relationship(cascade="all, delete-orphan")

class OrdemServicoServicoModel(Base):
    __tablename__ = "ordem_servico_servicos"
    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[str] = mapped_column(ForeignKey("ordens_servico.id"))
    servico_id: Mapped[int] = mapped_column(ForeignKey("servicos.id"))
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(12,2))
    servico: Mapped[ServicoModel] = relationship()

class OrdemServicoPecaModel(Base):
    __tablename__ = "ordem_servico_pecas"
    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[str] = mapped_column(ForeignKey("ordens_servico.id"))
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id"))
    quantidade: Mapped[int] = mapped_column(Integer)
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(12,2))
    peca: Mapped[PecaModel] = relationship()

class OrcamentoModel(Base):
    __tablename__ = "orcamentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[str] = mapped_column(ForeignKey("ordens_servico.id"), index=True)
    valor_servicos: Mapped[Decimal] = mapped_column(Numeric(12,2))
    valor_pecas: Mapped[Decimal] = mapped_column(Numeric(12,2))
    desconto: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    acrescimo: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12,2))
    validade: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="AGUARDANDO_APROVACAO", index=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_aprovacao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    aprovado_por: Mapped[str | None] = mapped_column(String(160), nullable=True)

class HistoricoStatusModel(Base):
    __tablename__ = "historico_status_os"
    id: Mapped[int] = mapped_column(primary_key=True)
    ordem_servico_id: Mapped[str] = mapped_column(ForeignKey("ordens_servico.id"), index=True)
    status_anterior: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status_novo: Mapped[str] = mapped_column(String(40))
    origem: Mapped[str] = mapped_column(String(60), default="API")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class WebhookEventoModel(Base):
    __tablename__ = "webhook_eventos"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    recebido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
