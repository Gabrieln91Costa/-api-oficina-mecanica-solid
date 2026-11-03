# API Oficina Mecânica

Obs.:
Usuario e Senha padrao adm/adm -> 
Utilizar Rota 01  para criação do usuario padrão -> -> POST /api/v1/auth/default

Videos Pasta /videos na raiz desse repositorio
DDD Url -> https://miro.com/app/board/uXjVHsnlPhY=/
Doc Word -> Pasta docs


API REST para gerenciamento integrado de uma oficina mecânica, desenvolvida como MVP para o **Tech Challenge – Fase 1**.

O sistema tem como objetivo organizar o processo de atendimento da oficina, permitindo o gerenciamento de clientes, veículos, serviços, peças, ordens de serviço e orçamentos, além do acompanhamento do ciclo de execução dos serviços.

---

## 1. Objetivo

O projeto foi desenvolvido para solucionar problemas encontrados no processo operacional de uma oficina mecânica de médio porte, como:

* Erros na priorização dos atendimentos;
* Falhas no controle de peças e insumos;
* Dificuldade no acompanhamento do status dos serviços;
* Perda do histórico de clientes e veículos;
* Ineficiência no processo de orçamento e aprovação;
* Falta de padronização dos processos internos.

A API disponibiliza recursos para centralizar essas informações e estabelecer um fluxo estruturado desde o recebimento do veículo até a conclusão e entrega do serviço.

### Principais funcionalidades

* Autenticação de usuários;
* Controle de acesso por perfil;
* Cadastro de unidades;
* Cadastro de funcionários;
* Cadastro de clientes;
* Cadastro de veículos;
* Cadastro de serviços;
* Cadastro de peças e controle de estoque;
* Criação e consulta de ordens de serviço;
* Criação de orçamentos;
* Aprovação e rejeição de orçamentos;
* Controle do status da ordem de serviço;
* API REST documentada automaticamente pelo Swagger.

---

# 2. Arquitetura

O projeto utiliza uma arquitetura de **monólito organizado em camadas**, adequada ao escopo de um MVP.

A aplicação foi desenvolvida utilizando:

* Python;
* FastAPI;
* SQLModel;
* SQLAlchemy;
* SQLite;
* JWT;
* Docker;
* Docker Compose.

### Estrutura simplificada

```text
api-oficina-mecanica/
│
├── api/
│   └── v1/
│       ├── api.py
│       └── endpoints/
│           ├── auth_endpoint.py
│           ├── cliente_endpoint.py
│           ├── funcionario_endpoint.py
│           ├── unidade_endpoint.py
│           ├── veiculo_endpoint.py
│           ├── servico_endpoint.py
│           ├── peca_endpoint.py
│           ├── ordem_servico_endpoint.py
│           └── orcamento_endpoint.py
│
├── models/
│   ├── __all_models.py
│   ├── cliente_model.py
│   ├── funcionario_model.py
│   ├── unidade_model.py
│   ├── veiculo_model.py
│   ├── servico_model.py
│   ├── peca_model.py
│   ├── ordem_servico_model.py
│   └── orcamento_model.py
│
├── core/
│   ├── database.py
│   ├── security.py
│   └── configs.py
│
├── tests/
│
├── criar_tabelas.py
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md
```

---

# 3. Domain Driven Design – DDD

O projeto utiliza conceitos de **Domain Driven Design (DDD)** para organizar o domínio da oficina mecânica.

O objetivo é representar no sistema os principais conceitos existentes no negócio utilizando uma linguagem próxima à utilizada pelos usuários da oficina.

## 3.1 Domínio principal

O domínio principal é o **atendimento e execução de serviços automotivos**.

O fluxo principal pode ser representado da seguinte forma:

```text
Cliente
   │
   ▼
Veículo
   │
   ▼
Ordem de Serviço
   │
   ├── Serviço
   │
   ├── Peça
   │
   ▼
Orçamento
   │
   ▼
Aprovação
   │
   ▼
Execução
   │
   ▼
Finalização
   │
   ▼
Entrega
```

## 3.2 Principais entidades

### Cliente

Representa o proprietário/responsável pelo veículo.

Principais informações:

* Nome;
* CPF/CNPJ;
* Telefone;
* E-mail;
* Status ativo.

### Veículo

Representa o veículo pertencente a um cliente.

Principais informações:

* Placa;
* Marca;
* Modelo;
* Ano;
* Cliente responsável.

### Serviço

Representa um serviço oferecido pela oficina.

Exemplos:

* Troca de óleo;
* Alinhamento;
* Balanceamento;
* Revisão;
* Troca de pastilhas.

### Peça

Representa uma peça ou insumo utilizado pela oficina.

Principais informações:

* Nome;
* Descrição;
* Código;
* Quantidade em estoque;
* Estoque mínimo;
* Valor unitário;
* Unidade.

### Ordem de Serviço

Representa o atendimento realizado para um veículo.

Relaciona:

* Unidade;
* Cliente;
* Serviço;
* Peça;
* Data;
* Hora;
* Número da OS;
* Status.

### Orçamento

Representa a proposta financeira associada a uma Ordem de Serviço.

Relaciona:

* Ordem de Serviço;
* Valor dos serviços;
* Valor das peças;
* Desconto;
* Acréscimo;
* Valor total;
* Validade;
* Status;
* Observações;
* Aprovação.

---

# 4. Linguagem Ubíqua

Os principais termos utilizados no projeto são:

| Termo            | Significado                                    |
| ---------------- | ---------------------------------------------- |
| Cliente          | Pessoa responsável pelo veículo                |
| Veículo          | Automóvel pertencente ao cliente               |
| Unidade          | Unidade física da oficina                      |
| Serviço          | Atividade de manutenção realizada              |
| Peça             | Item utilizado na manutenção                   |
| Ordem de Serviço | Registro do atendimento                        |
| Orçamento        | Proposta de valores da OS                      |
| Aprovação        | Autorização do cliente                         |
| Diagnóstico      | Análise necessária para identificar o problema |
| Execução         | Realização dos serviços autorizados            |
| Finalização      | Conclusão dos serviços                         |
| Entrega          | Devolução do veículo ao cliente                |

Essa padronização permite que os nomes utilizados no código estejam alinhados ao domínio do negócio.

---

# 5. Fluxo da Ordem de Serviço

O fluxo esperado para uma Ordem de Serviço é:

```text
RECEBIDA
    │
    ▼
EM DIAGNÓSTICO
    │
    ▼
AGUARDANDO APROVAÇÃO
    │
    ├──────────────► REJEITADA
    │
    ▼
EM EXECUÇÃO
    │
    ▼
FINALIZADA
    │
    ▼
ENTREGUE
```

O orçamento é associado à Ordem de Serviço e pode ser:

```text
AGUARDANDO_APROVACAO
        │
        ├──────► APROVADO
        │
        └──────► REJEITADO
```

---

# 6. Como executar localmente

## Pré-requisitos

Para executar o projeto localmente é necessário possuir:

* Python 3.11;
* pip;
* Git.

Recomenda-se utilizar um ambiente virtual.

## Criar ambiente virtual

Windows:

```bash
python -m venv .venv
```

Ativar:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
```

Ativar:

```bash
source .venv/bin/activate
```

---

# 7. Instalar dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

---

# 8. Configuração

As configurações da aplicação devem ser mantidas em variáveis de ambiente sempre que possível.

Exemplo de `.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./oficina.db
API_V1_STR=/api/v1

SECRET_KEY=sua-chave-secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Banco de dados

O projeto utiliza:

```text
SQLite
```

Com SQLModel/SQLAlchemy utilizando conexão assíncrona:

```text
sqlite+aiosqlite:///./oficina.db
```

> O arquivo `.env` não deve ser versionado no Git. Utilize `.env.example` para disponibilizar um modelo de configuração.

---

# 9. Criar as tabelas

O projeto possui o script:

```text
criar_tabelas.py
```

Execute:

```bash
python criar_tabelas.py
```

Esse processo cria as tabelas necessárias para execução da aplicação.

---

# 10. Executar a API

A aplicação pode ser iniciada através do:

```bash
python main.py
```

A API ficará disponível em:

```text
http://localhost:8000
```

Também é possível executar diretamente com Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

# 11. Swagger

Após iniciar a aplicação, a documentação pode ser acessada em:

```text
http://localhost:8000/docs
```

A documentação disponibiliza:

* Endpoints;
* Schemas;
* Request bodies;
* Responses;
* Autenticação;
* Testes das APIs diretamente pelo navegador.

Também está disponível o ReDoc:

```text
http://localhost:8000/redoc
```

---

# 12. Endpoints

Base URL:

```text
/api/v1
```

## Autenticação

```text
POST /api/v1/auth/
```

Responsável pela autenticação dos usuários e geração do token JWT.

---

## Unidades

```text
POST   /api/v1/unidades/
GET    /api/v1/unidades/
GET    /api/v1/unidades/{id}
PUT    /api/v1/unidades/{id}
DELETE /api/v1/unidades/{id}
```

---

## Funcionários

```text
POST   /api/v1/funcionarios/
GET    /api/v1/funcionarios/
GET    /api/v1/funcionarios/{id}
PUT    /api/v1/funcionarios/{id}
DELETE /api/v1/funcionarios/{id}
```

---

## Clientes

```text
POST   /api/v1/clientes/
GET    /api/v1/clientes/
GET    /api/v1/clientes/{id}
PUT    /api/v1/clientes/{id}
DELETE /api/v1/clientes/{id}
```

---

## Veículos

```text
POST   /api/v1/veiculos/
GET    /api/v1/veiculos/
GET    /api/v1/veiculos/{id}
PUT    /api/v1/veiculos/{id}
DELETE /api/v1/veiculos/{id}
```

Um veículo está relacionado a um cliente através de:

```text
cliente_id
```

---

## Serviços

```text
POST   /api/v1/servicos/
GET    /api/v1/servicos/
GET    /api/v1/servicos/{id}
PUT    /api/v1/servicos/{id}
DELETE /api/v1/servicos/{id}
```

---

## Peças / Estoque

```text
POST   /api/v1/pecas/
GET    /api/v1/pecas/
GET    /api/v1/pecas/{id}
PUT    /api/v1/pecas/{id}
DELETE /api/v1/pecas/{id}
```

As peças estão relacionadas a uma unidade através de:

```text
unidade_id
```

---

## Ordens de Serviço

```text
POST /api/v1/ordens-servico/
GET  /api/v1/ordens-servico/
GET  /api/v1/ordens-servico/{id}
```

A Ordem de Serviço possui relacionamento com:

```text
unidade_id
cliente_id
servico_id
peca_id
```

Além dos dados:

```text
numero_ordem
data
hora
status
ativo
```

---

## Orçamentos

```text
POST /api/v1/orcamentos/
GET  /api/v1/orcamentos/
GET  /api/v1/orcamentos/{id}
```

### Aprovar orçamento

```text
PATCH /api/v1/orcamentos/{id}/aprovar
```

### Rejeitar orçamento

```text
PATCH /api/v1/orcamentos/{id}/rejeitar
```

O orçamento utiliza a Ordem de Serviço como chave estrangeira:

```text
ordem_servico_id
```

Os valores financeiros são calculados pela API com base nos serviços e peças associados à OS.

---

# 13. Autenticação e Segurança

A API administrativa utiliza autenticação baseada em:

```text
JWT - JSON Web Token
```

Após autenticação, o cliente recebe um token que deve ser enviado nas requisições protegidas.

Exemplo:

```http
Authorization: Bearer <TOKEN>
```

A aplicação também possui controle de acesso por perfil.

Exemplo:

```text
GESTOR
FUNCIONARIO
```

Os endpoints administrativos utilizam dependências de segurança para verificar o perfil do usuário autenticado.

---

# 14. Banco de Dados – SQLite

Para o MVP foi escolhido o **SQLite**.

## Motivos da escolha

O SQLite é adequado ao projeto nesta primeira versão porque:

* Possui configuração simples;
* Não exige servidor de banco separado;
* Facilita a execução local;
* Facilita a execução em Docker;
* Possui baixo custo operacional;
* É suficiente para demonstração e validação do MVP;
* Permite manter o foco no desenvolvimento do domínio e das APIs.

A aplicação utiliza SQLModel, permitindo que a camada de persistência seja posteriormente adaptada para outro banco, como PostgreSQL, caso o sistema evolua para um ambiente de produção com maior volume e concorrência.

---

# 15. Docker

O projeto possui configuração para execução utilizando Docker.

Arquivos principais:

```text
Dockerfile
docker-compose.yml
```

## Construir e iniciar

Execute:

```bash
docker compose up --build
```

Ou, dependendo da versão instalada:

```bash
docker-compose up --build
```

A API estará disponível em:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 16. Docker Compose

O Docker Compose é responsável por orquestrar os serviços necessários para execução do projeto.

Fluxo:

```text
Docker Compose
      │
      ├── criar-tabelas
      │       │
      │       └── cria/atualiza estrutura do banco
      │
      └── api
              │
              └── inicia FastAPI
```

O serviço da API depende da conclusão da criação das tabelas.

Exemplo conceitual:

```yaml
services:

  criar-tabelas:
    build: .
    command: python criar_tabelas.py

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      criar-tabelas:
        condition: service_completed_successfully
```

---

# 17. Persistência do SQLite no Docker

O banco SQLite deve ser armazenado em um volume ou diretório montado para evitar a perda dos dados quando o container for recriado.

Exemplo:

```yaml
volumes:
  - ./data:/app/data
```

Nesse cenário:

```text
./data/oficina.db
```

permanece no host mesmo quando o container é removido.

---

# 18. Testes

Os testes automatizados devem ficar organizados no diretório:

```text
tests/
```

Estrutura recomendada:

```text
tests/
│
├── unit/
│   ├── test_cliente.py
│   ├── test_veiculo.py
│   ├── test_peca.py
│   ├── test_ordem_servico.py
│   └── test_orcamento.py
│
└── integration/
    ├── test_auth.py
    ├── test_ordem_servico.py
    └── test_orcamento.py
```

## Executar testes

Com `pytest` instalado:

```bash
pytest
```

Para visualizar a cobertura:

```bash
pytest --cov=. --cov-report=term-missing
```

Para gerar relatório HTML:

```bash
pytest --cov=. --cov-report=html
```

O relatório será gerado em:

```text
htmlcov/
```

### Meta do projeto

O requisito do Tech Challenge estabelece:

```text
Cobertura mínima de 80%
```

nos domínios críticos da aplicação.

Os principais fluxos que devem possuir cobertura são:

* Autenticação;
* Cliente;
* Veículo;
* Peças/estoque;
* Ordem de Serviço;
* Orçamento;
* Aprovação/rejeição;
* Controle de status.

---

# 19. Qualidade de Software

O projeto busca aplicar boas práticas de desenvolvimento, incluindo:

* Separação de responsabilidades;
* Organização em camadas;
* Modelos utilizando SQLModel;
* Endpoints RESTful;
* Validação de dados;
* Tratamento de exceções;
* Controle de acesso;
* Autenticação JWT;
* Testes automatizados;
* Documentação via Swagger;
* Containerização;
* Versionamento utilizando Git.

---

# 20. Análise de Vulnerabilidades

Como parte dos requisitos do Tech Challenge, deve ser realizado um processo de análise de vulnerabilidades.

Recomenda-se executar ferramentas de análise estática e de dependências.

Exemplo:

```bash
pip install bandit
```

Executar:

```bash
bandit -r . -x .venv
```

Também pode ser utilizado:

```bash
pip install pip-audit
```

Executar:

```bash
pip-audit
```

Os resultados dos scans devem ser registrados no relatório de entrega, incluindo:

* Vulnerabilidades encontradas;
* Severidade;
* Componente afetado;
* Medidas adotadas;
* Vulnerabilidades corrigidas;
* Vulnerabilidades aceitas/mitigadas, quando aplicável.

---

# 21. Event Storming

A documentação DDD do projeto deve contemplar Event Storming dos principais fluxos.

### Criação da Ordem de Serviço

Exemplo de fluxo:

```text
Cliente identificado
        ↓
Veículo identificado
        ↓
OS criada
        ↓
Serviço adicionado
        ↓
Peça adicionada
        ↓
Orçamento gerado
        ↓
Orçamento enviado
        ↓
Aguardando aprovação
```

### Acompanhamento da OS

```text
OS recebida
      ↓
Diagnóstico realizado
      ↓
Orçamento criado
      ↓
Aguardando aprovação
      ↓
Orçamento aprovado
      ↓
Serviço iniciado
      ↓
Serviço finalizado
      ↓
Veículo entregue
```

### Gestão de peças

```text
Peça cadastrada
      ↓
Entrada no estoque
      ↓
Peça vinculada à OS
      ↓
Peça utilizada
      ↓
Estoque atualizado
```

Esses fluxos devem ser representados visualmente no Miro ou ferramenta equivalente utilizada pelo grupo.

---

# 22. Entregáveis do Tech Challenge

O projeto deve ser acompanhado dos seguintes entregáveis:

## Código-fonte

Repositório privado contendo:

* Código da API;
* Models;
* Endpoints;
* Dockerfile;
* docker-compose.yml;
* requirements.txt;
* README.md;
* Testes;
* Arquivos de configuração necessários.

## Documentação DDD

Deve conter:

* Event Storming;
* Diagramas;
* Linguagem Ubíqua;
* Fluxos de criação e acompanhamento da OS;
* Gestão de peças e insumos.

## Relatório de segurança

Deve conter:

* Resultado dos scans;
* Vulnerabilidades encontradas;
* Correções realizadas;
* Medidas de segurança adotadas.

## Documento PDF

Deve conter:

* Nome do grupo;
* Participantes;
* Usernames no Discord;
* Link da documentação;
* Link do repositório;
* Relatório de vulnerabilidades.

## Vídeo

Vídeo de até:

```text
15 minutos
```

Demonstrando os principais recursos da aplicação.

---

# 23. Demonstração recomendada

Para a apresentação, recomenda-se demonstrar o seguinte fluxo:

```text
1. Login
      ↓
2. Obtenção do JWT
      ↓
3. Cadastro/consulta do cliente
      ↓
4. Cadastro do veículo
      ↓
5. Cadastro do serviço
      ↓
6. Cadastro da peça
      ↓
7. Criação da Ordem de Serviço
      ↓
8. Geração do orçamento
      ↓
9. Aprovação do orçamento
      ↓
10. Atualização da OS
      ↓
11. Finalização
      ↓
12. Entrega
```

Durante a apresentação também devem ser demonstrados:

* Swagger;
* Autenticação;
* Docker;
* Banco SQLite;
* Testes automatizados;
* Arquitetura;
* Documentação DDD.

---

# 24. Status do Projeto

### Implementado

* [x] API REST com FastAPI
* [x] Swagger
* [x] Autenticação JWT
* [x] Controle de perfis
* [x] Unidades
* [x] Funcionários
* [x] Clientes
* [x] Veículos
* [x] Serviços
* [x] Peças / estoque
* [x] Ordens de Serviço
* [x] Orçamentos
* [x] Aprovação de orçamento
* [x] Rejeição de orçamento
* [x] SQLite
* [x] SQLModel
* [x] Docker Compose

### Em evolução

* [ ] Fluxo completo e automático de status da OS
* [ ] Múltiplos serviços por OS
* [ ] Múltiplas peças por OS
* [ ] Baixa automática de estoque
* [ ] Consulta da OS pelo cliente
* [ ] Monitoramento do tempo médio de execução
* [ ] Testes unitários
* [ ] Testes de integração
* [ ] Cobertura mínima de 80%
* [ ] Dockerfile definitivo
* [ ] Scan de vulnerabilidades
* [ ] Event Storming
* [ ] Diagramas DDD
* [ ] Relatório de segurança

---

# 25. Licença

Projeto acadêmico desenvolvido para o **Tech Challenge – Fase 1**.

Uso destinado à avaliação acadêmica e demonstração dos conceitos estudados durante a fase.
