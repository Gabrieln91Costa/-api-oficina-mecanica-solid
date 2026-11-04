# API Oficina Mecânica --- Tech Challenge Fase 2

Evolução da API da oficina mecânica da Fase 1, com foco em **Clean
Architecture, princípios SOLID, testes automatizados, Docker,
Kubernetes, Terraform e CI/CD**.

> **Importante sobre a origem:** os fontes da Fase 1 recebidos foram
> preservados em `legacy_phase1/` para consulta e rastreabilidade. A
> aplicação executável da Fase 2 está em `src/oficina`. O banco SQLite
> original, `.git`, ambientes virtuais, caches e arquivos de cobertura
> não foram incluídos no ZIP para evitar distribuir dados locais e
> artefatos gerados. Não existe migração automática dos registros do
> banco antigo nesta versão; faça backup e planeje a migração antes de
> usar dados reais.

## 1. O que foi implementado

-   Abertura de OS com cliente, veículo, serviços e peças cadastrados,
    retornando UUID.

-   Consulta detalhada e consulta específica de status da OS.

-   Estados: `RECEBIDA`, `DIAGNOSTICO`, `AGUARDANDO_APROVACAO`,
    `EM_EXECUCAO`, `FINALIZADA`, `ENTREGUE`.

-   Validação de transições de estado.

-   Criação de orçamento calculado a partir dos serviços e peças
    associados à OS.

-   Aprovação ou recusa de orçamento por endpoint externo protegido por
    token.

-   Listagem operacional com prioridade
    `EM_EXECUCAO > AGUARDANDO_APROVACAO > DIAGNOSTICO > RECEBIDA`, mais
    antigas primeiro; finalizadas, entregues e excluídas logicamente
    ficam fora da listagem.

-   Exclusão lógica da OS, sem apagar o registro.

-   Baixa de estoque de peças na abertura da OS.

-   Histórico de mudanças de status.

-   Webhook de atualização de status que pode ser chamado por automação
    de e-mail (Make, n8n, Zapier ou provedor equivalente), com token e
    idempotência por `event_id`.

-   Notificação SMTP de orçamento e decisão; quando SMTP não está
    configurado, a aplicação registra a notificação no log.

-   Health check para probes do Kubernetes.

## 2. Arquitetura

Foi adotada **Clean Architecture**, com dependências apontando para o
domínio.

``` mermaid

flowchart TB

    Client[Cliente / Postman / Swagger] --> API[Presentation - FastAPI]

    API --> UC[Application - Use Cases]

    UC --> Ports[Ports / Protocols]

    Ports --> Repo[Infrastructure - SQLAlchemy Repository]

    Repo --> DB[(PostgreSQL)]

    UC --> NotifyPort[Notification Port]

    NotifyPort --> SMTP[SMTP / Logging Adapter]

    Email[Automação de e-mail / Make / n8n] --> Webhook[Webhook autenticado]

    Webhook --> API

    subgraph Kubernetes

      API

      DB

      HPA[HPA CPU / Memória]

    end
```

### Organização de diretórios

``` text

src/oficina/

├── domain/                 # Entidades, enums e regras de negócio

├── application/

│   ├── ports/              # Contratos de repositório e notificação

│   └── use_cases/          # Orquestração dos casos de uso

├── infrastructure/

│   ├── persistence/        # SQLAlchemy, modelos e repositório

│   └── notifications/      # Adaptadores SMTP e logging

└── presentation/

    └── api/v1/             # FastAPI, schemas e rotas
```

### Aplicação dos princípios SOLID

-   **S --- Responsabilidade única:** domínio, casos de uso,
    persistência, notificações e HTTP estão separados.

-   **O --- Aberto/fechado:** novos adaptadores de repositório ou
    notificação podem ser adicionados sem alterar as regras de domínio.

-   **L --- Substituição de Liskov:** adaptadores concretos implementam
    contratos usados pela aplicação.

-   **I --- Segregação de interfaces:** contratos pequenos e específicos
    (`OficinaRepository` e `Notificador`).

-   **D --- Inversão de dependência:** casos de uso dependem de
    Protocols, não de FastAPI ou SQLAlchemy.

## 3. Endpoints

Base local: `http://localhost:8000/api/v1`

| Método \| Endpoint \| Finalidade \|

\|---\|---\|---\|

| POST \| `/clientes` \| Cadastrar cliente \|

| POST \| `/veiculos` \| Cadastrar veículo vinculado ao cliente \|

| POST \| `/servicos` \| Cadastrar serviço \|

| POST \| `/pecas` \| Cadastrar peça e estoque \|

| POST \| `/ordens-servico` \| Abrir OS \|

| GET \| `/ordens-servico` \| Listar OS operacionais priorizadas \|

| GET \| `/ordens-servico/{id}` \| Consultar OS \|

| GET \| `/ordens-servico/{id}/status` \| Consultar status \|

| PATCH \| `/ordens-servico/{id}/status` \| Atualizar status \|

| DELETE \| `/ordens-servico/{id}` \| Excluir logicamente \|

| POST \| `/ordens-servico/{id}/orcamentos` \| Criar orçamento \|

| POST \| `/orcamentos/{id}/aprovacao` \| Aprovar/recusar orçamento \|

| POST \| `/webhooks/email/status` \| Atualização externa via automação
  de e-mail \|

A documentação interativa fica em `http://localhost:8000/docs`. A
collection está em [`postman/collection.json`](postman/collection.json).

### Fluxo mínimo de uso

1.  Cadastrar cliente.

2.  Cadastrar veículo com `cliente_id`.

3.  Cadastrar serviço e peça.

4.  Abrir OS com `cliente_id`, `veiculo_id`, `servicos[]` e `pecas[]`.

5.  Alterar OS para `DIAGNOSTICO`.

6.  Criar orçamento; a OS passa para `AGUARDANDO_APROVACAO`.

7.  Chamar o endpoint de aprovação com `X-Webhook-Token`. Aprovado leva
    a `EM_EXECUCAO`; recusado retorna a `DIAGNOSTICO`.

8.  Finalizar e entregar usando o endpoint de atualização de status,
    respeitando as transições.

### Exemplo de abertura de OS

``` json

{

  "cliente_id": 1,

  "veiculo_id": 1,

  "servicos": [{"servico_id": 1}],

  "pecas": [{"peca_id": 1, "quantidade": 2}],

  "observacao": "Revisão preventiva"

}
```

A abertura utiliza os cadastros já existentes, preservando integridade
referencial. O identificador retornado é UUID.

## 4. Execução local

Requisitos: Python 3.11+, Docker Desktop (opcional para executar com
PostgreSQL).

### PowerShell --- ambiente Python

``` powershell

py -3.11 -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

python -m pip install -e ".[dev]"

Copy-Item .env.example .env
```

Para rodar rapidamente com SQLite, configure:

``` powershell

$env:DATABASE_URL = "sqlite:///./oficina.db"

$env:WEBHOOK_TOKEN = "local-dev-token"

uvicorn oficina.presentation.api.app:app --reload
```

Se estiver usando o modo `src`, execute `pip install -e ".[dev]"` antes
de iniciar.

### Docker Compose com PostgreSQL

``` powershell

Copy-Item .env.example .env

docker compose up --build -d

docker compose ps

docker compose logs -f api
```

A API estará em `http://localhost:8000/docs`. Para encerrar:

``` powershell

docker compose down
```

Para apagar também o volume local do banco (operação destrutiva):

``` powershell

docker compose down -v
```

## 5. Testes e qualidade

``` powershell

python -m pytest -q

python -m pytest --cov=oficina --cov-report=term-missing

ruff check src tests
```

Os testes cobrem regras de transição, abertura e consulta de OS, consumo
de estoque, ordenação por prioridade, exclusão lógica, orçamento
aprovado/recusado, duplicidade de orçamento e idempotência do webhook.

## 6. Docker

-   `Dockerfile`: imagem Python 3.11 slim, usuário não-root e health
    check.

-   `docker-compose.yml`: API + PostgreSQL com health check e volume
    persistente.

## 7. Kubernetes

Manifestos em `/k8s`:

-   `namespace.yaml`

-   `postgres.yaml` --- Service headless, StatefulSet e PVC do
    PostgreSQL

-   `configmap.yaml`

-   `secret.example.yaml` --- exemplo, **não aplicar sem substituir os
    valores**

-   `deployment.yaml` --- API com 2 réplicas, recursos e probes

-   `hpa.yaml` --- escala de 2 a 8 réplicas por CPU e memória

### Kind local

Pré-requisitos: Docker Desktop, `kind`, `kubectl` e Terraform 1.5+.

1.  Entre em `infra/terraform`.

2.  Crie o cluster primeiro:

``` powershell

terraform init

terraform apply -target=terraform_data.kind_cluster
```

3.  Crie namespace e segredo local. Use valores fortes e não versione o
    arquivo de segredo:

``` powershell

kubectl apply -f ../../k8s/namespace.yaml

kubectl -n oficina create secret generic oficina-secret `

  --from-literal=DATABASE_URL="postgresql+psycopg://oficina:SENHA@postgres:5432/oficina" `

  --from-literal=WEBHOOK_TOKEN="TOKEN_FORTE" `

  --from-literal=POSTGRES_DB="oficina" `

  --from-literal=POSTGRES_USER="oficina" `

  --from-literal=POSTGRES_PASSWORD="SENHA"
```

4.  Provisione o banco pelo Terraform:

``` powershell

terraform apply
```

5.  Instale o Metrics Server para que o HPA receba métricas. No Kind, o
    kubelet pode exigir a flag de TLS abaixo para ambiente local de
    demonstração:

``` powershell

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

kubectl patch deployment metrics-server -n kube-system --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

kubectl rollout status deployment/metrics-server -n kube-system

kubectl top nodes
```

6.  Construa e carregue a imagem local:

``` powershell

docker build -t oficina-api:2.0.0 .

kind load docker-image oficina-api:2.0.0 --name oficina-local
```

7.  Aplique aplicação, configuração e HPA:

``` powershell

kubectl apply -f ../../k8s/configmap.yaml

kubectl apply -f ../../k8s/deployment.yaml

kubectl apply -f ../../k8s/hpa.yaml

kubectl rollout status deployment/oficina-api -n oficina

kubectl port-forward svc/oficina-api 8000:80 -n oficina
```

8.  Verifique:

``` powershell

kubectl get pods,svc,hpa -n oficina

kubectl top pods -n oficina

kubectl get hpa oficina-api -n oficina --watch
```

O HPA só escala quando o Metrics Server está operacional e os Pods
possuem `requests` de CPU/memória. Para teste de carga, utilize
`scripts/k6-carga.js` com k6 instalado:

``` powershell

k6 run -e BASE_URL=http://localhost:8000 scripts/k6-carga.js
```

### Remover cluster

``` powershell

terraform destroy
```

## 8. Terraform --- infraestrutura como código

Os arquivos Terraform estão organizados em `infra/terraform`.

A configuração foi preparada para:

-   criar um cluster Kubernetes local Kind com um control-plane e dois
    workers;
-   aplicar os manifestos do PostgreSQL (StatefulSet, Service e PVC)
    após a disponibilidade do cluster;
-   disponibilizar outputs com o nome do cluster e o namespace.

A criação está dividida em etapas para permitir a criação do Secret com
valores locais antes da inicialização do PostgreSQL. O estado Terraform
é local neste exemplo e não deve ser versionado.

**Status da validação:** a presença dos arquivos e a configuração
descrita não substituem a execução de `terraform init`,
`terraform validate` e `terraform plan`. Execute esses comandos no
diretório `infra/terraform` e revise o plano antes de considerar o
provisionamento validado. Execute `terraform apply` somente após
confirmar os recursos que serão criados ou alterados.

Para ambientes em nuvem, adapte o provider e o backend remoto e
considere utilizar um serviço gerenciado de banco de dados.

## 9. CI/CD --- GitHub Actions

Workflow: `.github/workflows/ci-cd.yml`.

O pipeline está dividido em três jobs:

### 9.1. Qualidade e testes --- `quality-and-tests`

Executado em `ubuntu-latest`:

1.  Faz checkout do repositório.
2.  Configura Python 3.11 e instala as dependências de desenvolvimento.
3.  Executa `ruff check src tests`.
4.  Executa os testes com Pytest e relatório de cobertura.

### 9.2. Build e publicação --- `build-and-publish`

Executado após a aprovação dos testes e não executado em eventos de Pull
Request:

1.  Configura Docker Buildx.
2.  Autentica no GitHub Container Registry (GHCR) usando o token do
    GitHub Actions.
3.  Constrói a imagem Docker.
4.  Publica as tags `latest` e a identificação do commit (`github.sha`)
    no GHCR.

Imagem publicada no formato:

`ghcr.io/<proprietario>/<repositorio>:<tag>`

### 9.3. Deploy local --- `deploy`

Executado em runner self-hosted Windows (`self-hosted`, `Windows`,
`X64`), somente para push na branch `main` ou execução manual
(`workflow_dispatch`).

O runner precisa estar conectado ao GitHub e ter Docker Desktop, Kind e
kubectl disponíveis. Para o ambiente local utilizado no projeto, o
contexto Kubernetes esperado é `kind-oficina-local`. O processo executa:

1.  Valida Docker, Kind, contexto Kubernetes e disponibilidade dos nós.
2.  Constrói localmente a imagem `oficina-api:<commit-sha>`.
3.  Carrega a imagem no cluster Kind com `kind load docker-image`.
4.  Confirma a existência do Secret `oficina-secret` no namespace
    `oficina`.
5.  Aplica os manifestos do PostgreSQL e aguarda o StatefulSet.
6.  Aplica ConfigMap, Deployment e HPA.
7.  Atualiza a imagem do Deployment para a versão do commit e aguarda o
    rollout.
8.  Consulta Pods, Services e HPA e executa o health check em
    `http://localhost:8080/health`.

**Observação sobre as imagens:** o pipeline publica a imagem no GHCR
como artefato do CI. No deploy do cluster Kind local, o runner Windows
constrói a imagem localmente e a carrega diretamente no cluster;
portanto, essa etapa não depende de baixar a imagem do GHCR.

### 9.4. Configuração do runner

O runner self-hosted está instalado no ambiente Windows do projeto.
Quando iniciado de forma interativa com `run.cmd`, a janela do
PowerShell deve permanecer aberta enquanto o GitHub Actions precisar
executar o job de deploy.

O Secret `oficina-secret` deve existir previamente no namespace
`oficina` e conter as chaves exigidas pela aplicação, incluindo
configurações de banco, token de webhook e, quando utilizado,
credenciais SMTP. Não versione valores reais de Secrets, arquivos `.env`
ou kubeconfig.

O workflow foi executado com sucesso no histórico do projeto, incluindo
testes, build/publicação da imagem e deploy no cluster Kind local. A
execução bem-sucedida comprova o fluxo utilizado naquele ambiente; não
representa, por si só, deploy em cluster de nuvem.

## 10. Atualização de status via e-mail

A API disponibiliza `POST /api/v1/webhooks/email/status`, protegido por
`X-Webhook-Token` e `event_id` idempotente. O adaptador SMTP envia
notificações quando um orçamento é criado e quando recebe decisão.

O endpoint é a entrada de uma automação externa: configure um fluxo no
Make, n8n, Zapier ou provedor de e-mail para interpretar a
resposta/evento recebido e chamar o webhook com `ordem_servico_id`,
`status` e `event_id`. **A API não monitora uma caixa postal nem
interpreta e-mails por conta própria**; isso depende da
automação/provedor configurado. Para produção, configure TLS, rotação de
token e validação de assinatura do provedor.

## 11. Segurança e operação

-   Nunca versione `.env`, `k8s/secret.yaml`, senhas ou kubeconfig.

-   Troque `WEBHOOK_TOKEN` antes de habilitar integração.

-   O Secret Kubernetes é um objeto de configuração sensível; em
    produção, habilite criptografia em repouso e use um gerenciador de
    segredos.

-   Configure SMTP e credenciais via Secret.

-   O banco local usa PVC, mas StatefulSet com uma réplica não
    representa alta disponibilidade de banco. Em produção, prefira
    PostgreSQL gerenciado ou cluster com replicação, backup e
    recuperação testados.

-   A aplicação cria as tabelas via `metadata.create_all` na
    inicialização. Para evolução de schema em produção, adote Alembic e
    migrations versionadas.

-   Antes de produção, adicione autenticação/autorização aos endpoints
    de negócio, rate limiting, auditoria, observabilidade e testes de
    carga de ponta a ponta. O token de webhook protege somente os
    endpoints de integração externa.

## 12. Entrega FIAP --- itens de submissão

-   **Repositório:**
    https://github.com/Gabrieln91Costa/-api-oficina-mecanica-solid
-   **Acesso ao repositório:** confirmar o compartilhamento com
    `soat-architecture`.
-   **Vídeo demonstrativo:** pendente de gravação/publicação. O vídeo
    deve ter até 15 minutos e demonstrar deploy, CI/CD, consumo dos
    endpoints e comportamento do HPA sob carga.
-   **PDF de entrega:** arquivo preparado com o contexto do projeto e a
    arquitetura. Inserir o link público ou não listado do vídeo assim
    que estiver publicado.
-   **Diagrama de arquitetura:** desenho preparado como material de
    apoio; incluir no repositório ou no pacote de entrega final.
-   **Roteiro de conferência:** `docs/entrega-fase2.md`.

Antes da submissão, confirmar também a validação do Terraform, o
escalonamento efetivo do HPA e a coleção Postman em
`postman/collection.json`.

## 13. Limitações conhecidas desta entrega

Esta versão fornece uma base executável e testada para os fluxos
centrais da Fase 2, mas não deve ser confundida com uma implantação já
validada em cluster real. O ZIP preserva o código legado como
referência, mas não migra automaticamente o banco SQLite antigo nem
reativa todos os módulos acessórios da Fase 1 (usuários/autenticação,
unidades, funcionários, acompanhamento e tempo de execução). Esses
módulos devem ser portados para a nova arquitetura antes de afirmar
equivalência funcional integral com a Fase 1. O deploy em cluster, a
integração real com provedor de e-mail e a escalabilidade HPA precisam
ser demonstrados no ambiente do grupo.
