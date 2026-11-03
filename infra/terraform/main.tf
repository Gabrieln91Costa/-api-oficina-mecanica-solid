resource "terraform_data" "kind_cluster" {
  input = var.cluster_name

  provisioner "local-exec" {
    command     = "C:/Users/gabri/AppData/Local/Microsoft/WinGet/Packages/Kubernetes.kind_Microsoft.Winget.Source_8wekyb3d8bbwe/kind.exe create cluster --name ${var.cluster_name} --config kind-config.yaml"
    working_dir = path.module
  }

  provisioner "local-exec" {
    when    = destroy
    command = "C:/Users/gabri/AppData/Local/Microsoft/WinGet/Packages/Kubernetes.kind_Microsoft.Winget.Source_8wekyb3d8bbwe/kind.exe delete cluster --name ${self.input}"
  }
}

resource "terraform_data" "postgres_database" {
  depends_on = [terraform_data.kind_cluster]
  input      = var.namespace

  provisioner "local-exec" {
    command     = "kubectl apply -f ../../k8s/namespace.yaml -f ../../k8s/postgres.yaml"
    working_dir = path.module
  }

  provisioner "local-exec" {
    command     = "kubectl rollout status statefulset/postgres -n ${var.namespace} --timeout=180s"
    working_dir = path.module
  }
}