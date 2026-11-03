from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from oficina.domain.enums import StatusOS

class ClienteIn(BaseModel):
    nome: str = Field(min_length=2, max_length=160)
    cpf_cnpj: str = Field(min_length=11, max_length=20)
    telefone: str = Field(min_length=8, max_length=30)
    email: str | None = None
    endereco: str | None = None
class VeiculoIn(BaseModel):
    cliente_id: int
    placa: str = Field(min_length=7, max_length=10)
    marca: str
    modelo: str
    ano: int = Field(ge=1950, le=2100)
class ServicoIn(BaseModel):
    nome: str
    descricao: str | None = None
    valor: Decimal = Field(ge=0)
class PecaIn(BaseModel):
    nome: str
    codigo: str
    quantidade_estoque: int = Field(ge=0)
    valor_unitario: Decimal = Field(ge=0)
class ItemServicoIn(BaseModel):
    servico_id: int
class ItemPecaIn(BaseModel):
    peca_id: int
    quantidade: int = Field(gt=0)
class OrdemServicoIn(BaseModel):
    cliente_id: int
    veiculo_id: int
    servicos: list[ItemServicoIn] = Field(min_length=1)
    pecas: list[ItemPecaIn] = []
    observacao: str | None = None
class StatusUpdateIn(BaseModel):
    status: StatusOS
class OrcamentoIn(BaseModel):
    desconto: Decimal = Field(default=Decimal('0'), ge=0)
    acrescimo: Decimal = Field(default=Decimal('0'), ge=0)
    validade: str | None = None
    observacao: str | None = None
class DecisaoOrcamentoIn(BaseModel):
    aprovado: bool
    ator: str = Field(default='CLIENTE', min_length=1, max_length=160)
class WebhookStatusIn(BaseModel):
    event_id: str = Field(min_length=4, max_length=160)
    ordem_servico_id: UUID
    status: StatusOS
    origem: str = 'EMAIL'
class ClienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; nome: str; cpf_cnpj: str; telefone: str; email: str | None; endereco: str | None; ativo: bool
class VeiculoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; cliente_id: int; placa: str; marca: str; modelo: str; ano: int; ativo: bool
class CatalogoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; nome: str; ativo: bool
class OrcamentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; ordem_servico_id: str; valor_servicos: Decimal; valor_pecas: Decimal; desconto: Decimal; acrescimo: Decimal; valor_total: Decimal; validade: str | None; status: str; observacao: str | None
class OrdemServicoOut(BaseModel):
    id: str; numero_ordem: str; cliente_id: int; veiculo_id: int; status: str; criado_em: datetime; excluida: bool; observacao: str | None
    @classmethod
    def from_model(cls, obj):
        return cls(id=obj.id, numero_ordem=obj.numero_ordem, cliente_id=obj.cliente_id, veiculo_id=obj.veiculo_id,
            status=obj.status, criado_em=obj.criado_em, excluida=obj.excluida, observacao=obj.observacao)
