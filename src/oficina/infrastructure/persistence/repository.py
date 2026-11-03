from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from oficina.domain.enums import StatusOS, StatusOrcamento, PRIORIDADE_STATUS
from oficina.domain.entities import OrdemServico
from oficina.domain.exceptions import NotFoundError, ConflictError, ValidationError
from .models import (ClienteModel, VeiculoModel, ServicoModel, PecaModel, OrdemServicoModel,
    OrdemServicoServicoModel, OrdemServicoPecaModel, OrcamentoModel, HistoricoStatusModel, WebhookEventoModel)

class SqlAlchemyOficinaRepository:
    """Adaptador de persistência. Implementa a porta OficinaRepository."""
    def __init__(self, session: Session):
        self.session = session

    def criar_cliente(self, dados):
        obj = ClienteModel(**dados); self.session.add(obj); self.session.commit(); self.session.refresh(obj); return obj

    def criar_veiculo(self, dados):
        if not self.session.get(ClienteModel, dados['cliente_id']): raise NotFoundError('Cliente não encontrado.')
        obj = VeiculoModel(**dados); self.session.add(obj); self.session.commit(); self.session.refresh(obj); return obj

    def criar_servico(self, dados):
        obj = ServicoModel(**dados); self.session.add(obj); self.session.commit(); self.session.refresh(obj); return obj

    def criar_peca(self, dados):
        obj = PecaModel(**dados); self.session.add(obj); self.session.commit(); self.session.refresh(obj); return obj

    def abrir_os(self, dados):
        cliente = self.session.get(ClienteModel, dados['cliente_id'])
        veiculo = self.session.get(VeiculoModel, dados['veiculo_id'])
        if not cliente or not cliente.ativo: raise NotFoundError('Cliente não encontrado ou inativo.')
        if not veiculo or not veiculo.ativo or veiculo.cliente_id != cliente.id:
            raise ValidationError('Veículo inválido ou não pertence ao cliente informado.')
        if not dados.get('servicos'): raise ValidationError('Informe ao menos um serviço.')
        os_id = str(uuid4())
        ordem = OrdemServicoModel(id=os_id, numero_ordem=f'OS-{datetime.now(timezone.utc):%Y%m%d}-{os_id[:8].upper()}',
            cliente_id=cliente.id, veiculo_id=veiculo.id, status=StatusOS.RECEBIDA.value,
            observacao=dados.get('observacao'))
        for item in dados['servicos']:
            servico = self.session.get(ServicoModel, item['servico_id'])
            if not servico or not servico.ativo: raise NotFoundError(f"Serviço {item['servico_id']} não encontrado ou inativo.")
            ordem.servicos.append(OrdemServicoServicoModel(servico_id=servico.id, valor_unitario=servico.valor))
        for item in dados.get('pecas', []):
            peca = self.session.get(PecaModel, item['peca_id'])
            quantidade = item['quantidade']
            if quantidade <= 0: raise ValidationError('Quantidade de peça deve ser maior que zero.')
            if not peca or not peca.ativo: raise NotFoundError(f"Peça {item['peca_id']} não encontrada ou inativa.")
            if peca.quantidade_estoque < quantidade: raise ConflictError(f'Estoque insuficiente para a peça {peca.nome}.')
            ordem.pecas.append(OrdemServicoPecaModel(peca_id=peca.id, quantidade=quantidade, valor_unitario=peca.valor_unitario))
            peca.quantidade_estoque -= quantidade
        self.session.add(ordem)
        self.session.add(HistoricoStatusModel(ordem_servico_id=os_id, status_anterior=None, status_novo=StatusOS.RECEBIDA.value, origem='ABERTURA'))
        self.session.commit(); return self.buscar_os(UUID(os_id))

    def buscar_os(self, ordem_id: UUID):
        stmt = select(OrdemServicoModel).options(joinedload(OrdemServicoModel.cliente), joinedload(OrdemServicoModel.veiculo),
            joinedload(OrdemServicoModel.servicos).joinedload(OrdemServicoServicoModel.servico),
            joinedload(OrdemServicoModel.pecas).joinedload(OrdemServicoPecaModel.peca)).where(OrdemServicoModel.id == str(ordem_id))
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def listar_os_operacionais(self):
        stmt = select(OrdemServicoModel).options(joinedload(OrdemServicoModel.cliente), joinedload(OrdemServicoModel.veiculo)).where(
            OrdemServicoModel.excluida.is_(False), OrdemServicoModel.status.in_([s.value for s in PRIORIDADE_STATUS]))
        items = list(self.session.execute(stmt).unique().scalars().all())
        return sorted(items, key=lambda x: (PRIORIDADE_STATUS[StatusOS(x.status)], x.criado_em))

    def atualizar_status(self, ordem_id, status, origem='API'):
        ordem = self.buscar_os(ordem_id)
        if not ordem: return None
        atual = StatusOS(ordem.status); novo = StatusOS(status)
        entidade = OrdemServico(UUID(ordem.id), ordem.cliente_id, ordem.veiculo_id, atual, ordem.criado_em, ordem.excluida)
        entidade.alterar_status(novo)
        ordem.status = entidade.status.value
        self.session.add(HistoricoStatusModel(ordem_servico_id=ordem.id, status_anterior=atual.value, status_novo=novo.value, origem=origem))
        self.session.commit(); return self.buscar_os(UUID(ordem.id))

    def criar_orcamento(self, ordem_id, dados):
        ordem = self.buscar_os(ordem_id)
        if not ordem: raise NotFoundError('Ordem de serviço não encontrada.')
        if ordem.status != StatusOS.DIAGNOSTICO.value: raise ConflictError('A OS precisa estar em DIAGNOSTICO para receber orçamento.')
        pendente = self.session.scalar(select(OrcamentoModel).where(OrcamentoModel.ordem_servico_id == str(ordem_id), OrcamentoModel.status == StatusOrcamento.AGUARDANDO_APROVACAO.value))
        if pendente: raise ConflictError('Já existe orçamento aguardando aprovação para esta OS.')
        servicos = sum((x.valor_unitario for x in ordem.servicos), Decimal('0.00'))
        pecas = sum((x.valor_unitario * x.quantidade for x in ordem.pecas), Decimal('0.00'))
        desconto = Decimal(str(dados.get('desconto', 0))); acrescimo = Decimal(str(dados.get('acrescimo', 0)))
        if desconto < 0 or acrescimo < 0: raise ValidationError('Desconto e acréscimo não podem ser negativos.')
        total = servicos + pecas + acrescimo - desconto
        if total < 0: raise ValidationError('Total do orçamento não pode ser negativo.')
        obj = OrcamentoModel(ordem_servico_id=str(ordem_id), valor_servicos=servicos, valor_pecas=pecas,
            desconto=desconto, acrescimo=acrescimo, valor_total=total, validade=dados.get('validade'), observacao=dados.get('observacao'))
        ordem.status = StatusOS.AGUARDANDO_APROVACAO.value
        self.session.add(obj); self.session.add(HistoricoStatusModel(ordem_servico_id=ordem.id, status_anterior=StatusOS.DIAGNOSTICO.value,
            status_novo=StatusOS.AGUARDANDO_APROVACAO.value, origem='ORCAMENTO'))
        self.session.commit(); self.session.refresh(obj); return obj

    def decidir_orcamento(self, orcamento_id, aprovado, ator):
        obj = self.session.get(OrcamentoModel, orcamento_id)
        if not obj: return None
        if obj.status != StatusOrcamento.AGUARDANDO_APROVACAO.value: raise ConflictError('Orçamento já decidido.')
        ordem = self.session.get(OrdemServicoModel, obj.ordem_servico_id)
        if not ordem: raise NotFoundError('OS vinculada ao orçamento não encontrada.')
        obj.status = StatusOrcamento.APROVADO.value if aprovado else StatusOrcamento.RECUSADO.value
        obj.data_aprovacao = datetime.now(timezone.utc); obj.aprovado_por = ator
        anterior = StatusOS(ordem.status)
        if anterior != StatusOS.AGUARDANDO_APROVACAO:
            raise ConflictError('A OS não está aguardando aprovação do orçamento.')
        proximo = StatusOS.EM_EXECUCAO if aprovado else StatusOS.DIAGNOSTICO
        ordem.status = proximo.value
        self.session.add(HistoricoStatusModel(ordem_servico_id=ordem.id, status_anterior=anterior.value, status_novo=proximo.value, origem='APROVACAO_ORCAMENTO'))
        self.session.commit(); self.session.refresh(obj); return obj

    def registrar_evento(self, event_id, payload):
        if self.session.scalar(select(WebhookEventoModel).where(WebhookEventoModel.event_id == event_id)):
            return False
        self.session.add(WebhookEventoModel(event_id=event_id, payload=payload)); self.session.commit(); return True

    def excluir_logicamente(self, ordem_id):
        ordem = self.session.get(OrdemServicoModel, str(ordem_id))
        if not ordem: return False
        ordem.excluida = True; self.session.commit(); return True

    def listar_clientes(self):
        return list(self.session.scalars(select(ClienteModel).where(ClienteModel.ativo.is_(True))).all())

    def listar_veiculos(self, cliente_id=None):
        stmt = select(VeiculoModel).where(VeiculoModel.ativo.is_(True))
        if cliente_id is not None: stmt = stmt.where(VeiculoModel.cliente_id == cliente_id)
        return list(self.session.scalars(stmt).all())

    def listar_servicos(self):
        return list(self.session.scalars(select(ServicoModel).where(ServicoModel.ativo.is_(True))).all())

    def listar_pecas(self):
        return list(self.session.scalars(select(PecaModel).where(PecaModel.ativo.is_(True))).all())

    def evento_existe(self, event_id):
        return self.session.scalar(select(WebhookEventoModel).where(WebhookEventoModel.event_id == event_id)) is not None
