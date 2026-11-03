variable "cluster_name" {
  description = "Nome do cluster Kind local."
  type        = string
  default     = "oficina-local"
}
variable "namespace" {
  description = "Namespace Kubernetes da aplicação."
  type        = string
  default     = "oficina"
}
