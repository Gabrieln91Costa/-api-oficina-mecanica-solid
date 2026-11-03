# Arquitetura da solução

```mermaid
flowchart LR
    A[Postman / Cliente] --> P[FastAPI]
    P --> U[Casos de uso]
    U --> D[Domínio]
    U --> R[Porta Repository]
    R --> SQL[Adaptador SQLAlchemy]
    SQL --> PG[(PostgreSQL)]
    U --> N[Porta Notificador]
    N --> SMTP[SMTP / Logs]
    E[Automação externa de e-mail] --> W[Webhook com token]
    W --> P
    subgraph K8s
      P
      PG
      H[HPA CPU/Memória]
    end
```

## Decisões
- Domínio não importa framework, banco ou transporte.
- Application orquestra regras de caso de uso por interfaces.
- Infrastructure implementa persistência e notificação.
- Presentation contém schemas HTTP e roteamento.
- PostgreSQL é persistente; API é stateless e pode escalar horizontalmente.
- HPA utiliza métricas de CPU e memória; requests/limits são definidos no Deployment.
