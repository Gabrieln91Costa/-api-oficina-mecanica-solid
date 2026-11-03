# Matriz de rastreabilidade

| Requisito | Implementação | Evidência / ressalva |
|---|---|---|
| Clean Code / SOLID | `src/oficina` | Camadas e Protocols; revisar lint no ambiente alvo |
| Clean Architecture | `domain`, `application`, `infrastructure`, `presentation` | Diagrama em README |
| Testes automatizados | `tests/unit`, `tests/integration` | 11 testes executados localmente nesta geração |
| Abrir OS | `POST /api/v1/ordens-servico` | UUID, cliente, veículo, serviços, peças |
| Consultar status | `GET /api/v1/ordens-servico/{id}/status` | Enum de seis estados |
| Aprovar/recusar orçamento | `POST /api/v1/orcamentos/{id}/aprovacao` | Token externo; aprovado vai para execução, recusado retorna ao diagnóstico |
| Listar priorizado | `GET /api/v1/ordens-servico` | Prioridade + antiguidade; finalizada/entregue fora |
| Exclusão lógica | `DELETE /api/v1/ordens-servico/{id}` | Flag excluida |
| Atualização por e-mail | `POST /api/v1/webhooks/email/status` | Integração depende de automação/provedor externo |
| Dockerfile / Compose | raiz | API + PostgreSQL |
| K8s Deployment / Service | `k8s/deployment.yaml` | API |
| ConfigMap / Secret | `k8s/configmap.yaml`, `k8s/secret.example.yaml` | Valores reais são externos |
| HPA CPU/memória | `k8s/hpa.yaml` | Requer Metrics Server operacional |
| Terraform cluster | `infra/terraform` | Kind local |
| Terraform banco | `terraform_data.postgres_database` aplica `k8s/postgres.yaml` | StatefulSet + PVC |
| CI/CD | `.github/workflows/ci-cd.yml` | Deploy exige secrets, cluster acessível e habilitação |
| README / Collection | `README.md`, `postman/collection.json` | Swagger também disponível |
| Vídeo e PDF final | pendentes | dependem de gravação, publicação e compartilhamento GitHub |
| Equivalência completa Fase 1 | parcial | módulos acessórios e migração de banco ainda pendentes |
