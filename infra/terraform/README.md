# Terraform local (Kind)

O módulo cria o cluster Kind e aplica os manifestos do PostgreSQL. Para manter senhas fora do state, o Secret Kubernetes é criado manualmente entre as duas etapas de `terraform apply`. Consulte o passo a passo no README raiz.

Pré-requisitos: Docker, Kind, kubectl e Terraform >= 1.5. O nome do cluster definido em `kind-config.yaml` deve acompanhar a variável `cluster_name` se alterada.
