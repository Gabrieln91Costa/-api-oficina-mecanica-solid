def abrir_os(client, cadastro):
    return client.post('/api/v1/ordens-servico', json={
        'cliente_id':cadastro['cliente']['id'],'veiculo_id':cadastro['veiculo']['id'],
        'servicos':[{'servico_id':cadastro['servico']['id']}],
        'pecas':[{'peca_id':cadastro['peca']['id'],'quantidade':2}]
    })

def test_abertura_consulta_status_e_pecas(client, cadastro_basico):
    response = abrir_os(client, cadastro_basico)
    assert response.status_code == 201
    os_id = response.json()['id']
    assert response.json()['status'] == 'RECEBIDA'
    detalhe = client.get(f'/api/v1/ordens-servico/{os_id}')
    assert detalhe.status_code == 200
    assert detalhe.json()['cliente']['nome'] == 'Cliente Teste'
    assert len(detalhe.json()['pecas']) == 1
    assert client.get(f'/api/v1/ordens-servico/{os_id}/status').json()['status'] == 'RECEBIDA'

def test_lista_prioriza_status_e_exclui_finalizadas(client, cadastro_basico):
    r1 = abrir_os(client, cadastro_basico).json()['id']
    r2 = abrir_os(client, cadastro_basico).json()['id']
    client.patch(f'/api/v1/ordens-servico/{r1}/status', json={'status':'DIAGNOSTICO'})
    client.patch(f'/api/v1/ordens-servico/{r1}/status', json={'status':'FINALIZADA'})
    lista = client.get('/api/v1/ordens-servico').json()
    ids = [x['id'] for x in lista]
    assert r1 not in ids and r2 in ids

def test_orcamento_aprovado_altera_status_para_execucao(client, cadastro_basico):
    os_id = abrir_os(client, cadastro_basico).json()['id']
    client.patch(f'/api/v1/ordens-servico/{os_id}/status', json={'status':'DIAGNOSTICO'})
    budget = client.post(f'/api/v1/ordens-servico/{os_id}/orcamentos', json={'desconto':'10','acrescimo':'0'})
    assert budget.status_code == 201
    assert float(budget.json()['valor_total']) == 340.0
    decision = client.post(f"/api/v1/orcamentos/{budget.json()['id']}/aprovacao", headers={'X-Webhook-Token':'test-token'}, json={'aprovado':True,'ator':'cliente-teste'})
    assert decision.status_code == 200
    assert client.get(f'/api/v1/ordens-servico/{os_id}/status').json()['status'] == 'EM_EXECUCAO'

def test_recusa_orcamento_retorna_para_diagnostico(client, cadastro_basico):
    os_id = abrir_os(client, cadastro_basico).json()['id']
    client.patch(f'/api/v1/ordens-servico/{os_id}/status', json={'status':'DIAGNOSTICO'})
    budget = client.post(f'/api/v1/ordens-servico/{os_id}/orcamentos', json={}).json()
    response = client.post(f"/api/v1/orcamentos/{budget['id']}/aprovacao", headers={'X-Webhook-Token':'test-token'}, json={'aprovado':False})
    assert response.status_code == 200
    assert client.get(f'/api/v1/ordens-servico/{os_id}/status').json()['status'] == 'DIAGNOSTICO'

def test_webhook_email_e_idempotente(client, cadastro_basico):
    os_id = abrir_os(client, cadastro_basico).json()['id']
    payload = {'event_id':'evt-1234','ordem_servico_id':os_id,'status':'DIAGNOSTICO','origem':'EMAIL'}
    headers = {'X-Webhook-Token':'test-token'}
    assert client.post('/api/v1/webhooks/email/status', json=payload, headers=headers).status_code == 200
    again = client.post('/api/v1/webhooks/email/status', json=payload, headers=headers)
    assert again.status_code == 200 and again.json()['duplicado'] is True

def test_transicao_invalida_retorna_422(client, cadastro_basico):
    os_id = abrir_os(client, cadastro_basico).json()['id']
    response = client.patch(f'/api/v1/ordens-servico/{os_id}/status', json={'status':'ENTREGUE'})
    assert response.status_code == 422

def test_exclusao_logica_nao_apaga_registro(client, cadastro_basico):
    os_id = abrir_os(client, cadastro_basico).json()['id']
    response = client.delete(f'/api/v1/ordens-servico/{os_id}')
    assert response.status_code == 204
    assert client.get(f'/api/v1/ordens-servico/{os_id}/status').status_code == 200
    assert all(x['id'] != os_id for x in client.get('/api/v1/ordens-servico').json())

def test_prioridade_status_diagnostico_antes_de_recebida(client, cadastro_basico):
    os_recebida = abrir_os(client, cadastro_basico).json()['id']
    os_diagnostico = abrir_os(client, cadastro_basico).json()['id']
    client.patch(f'/api/v1/ordens-servico/{os_diagnostico}/status', json={'status':'DIAGNOSTICO'})
    lista = client.get('/api/v1/ordens-servico').json()
    ids = [item['id'] for item in lista]
    assert ids.index(os_diagnostico) < ids.index(os_recebida)

def test_nao_permite_dois_orcamentos_pendentes(client, cadastro_basico):
    os_id = abrir_os(client, cadastro_basico).json()['id']
    client.patch(f'/api/v1/ordens-servico/{os_id}/status', json={'status':'DIAGNOSTICO'})
    primeiro = client.post(f'/api/v1/ordens-servico/{os_id}/orcamentos', json={})
    segundo = client.post(f'/api/v1/ordens-servico/{os_id}/orcamentos', json={})
    assert primeiro.status_code == 201
    assert segundo.status_code == 409

def test_mesmo_status_ordena_os_mais_antiga_primeiro(client, cadastro_basico):
    import time
    primeira = abrir_os(client, cadastro_basico).json()['id']
    time.sleep(0.01)
    segunda = abrir_os(client, cadastro_basico).json()['id']
    client.patch(f'/api/v1/ordens-servico/{primeira}/status', json={'status':'DIAGNOSTICO'})
    client.patch(f'/api/v1/ordens-servico/{segunda}/status', json={'status':'DIAGNOSTICO'})
    ids = [item['id'] for item in client.get('/api/v1/ordens-servico').json()]
    assert ids.index(primeira) < ids.index(segunda)

def test_webhook_rejeita_token_invalido(client, cadastro_basico):
    os_id = abrir_os(client, cadastro_basico).json()['id']
    response = client.post('/api/v1/webhooks/email/status', headers={'X-Webhook-Token':'errado'}, json={
        'event_id':'evt-invalid','ordem_servico_id':os_id,'status':'DIAGNOSTICO','origem':'EMAIL'
    })
    assert response.status_code == 401
