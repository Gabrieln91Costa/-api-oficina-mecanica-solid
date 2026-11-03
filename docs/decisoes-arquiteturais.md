# Decisões arquiteturais

1. Clean Architecture em quatro camadas para manter regras de negócio independentes de framework e persistência.
2. Protocols Python como portas para repositório e notificação, permitindo substituir SQLAlchemy/SMTP.
3. SQLAlchemy 2 e PostgreSQL para persistência relacional.
4. UUID para identificação pública da OS.
5. Histórico de status para auditoria.
6. Exclusão lógica para manter rastreabilidade.
7. Webhook com token e event_id para integração externa idempotente.
8. API stateless e HPA para escalar réplicas; banco mantém estado em volume persistente.
9. Terraform provisiona Kind e aplica manifestos de banco. O Secret é criado fora do state Terraform.
10. GitHub Actions separa qualidade/testes, publicação de imagem e deploy opcional.
