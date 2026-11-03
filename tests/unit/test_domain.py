from datetime import datetime, timezone
from uuid import uuid4
import pytest
from oficina.domain.entities import OrdemServico
from oficina.domain.enums import StatusOS
from oficina.domain.exceptions import InvalidTransitionError

def test_transicao_valida_recebida_para_diagnostico():
    os = OrdemServico(uuid4(), 1, 1, StatusOS.RECEBIDA, datetime.now(timezone.utc))
    os.alterar_status(StatusOS.DIAGNOSTICO)
    assert os.status == StatusOS.DIAGNOSTICO

def test_transicao_invalida_nao_e_permitida():
    os = OrdemServico(uuid4(), 1, 1, StatusOS.RECEBIDA, datetime.now(timezone.utc))
    with pytest.raises(InvalidTransitionError): os.alterar_status(StatusOS.ENTREGUE)
