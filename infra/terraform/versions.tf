# infra/terraform/versions.tf — Terraform y sus providers (módulo 86)
terraform {
  required_version = ">= 1.12" # 1.10: ephemeral; 1.11: atributos write-only; 1.12: backend "oci"

  required_providers {
    oci       = { source = "oracle/oci", version = "~> 9.11" }
    vercel    = { source = "vercel/vercel", version = "~> 5.24" }
    hostinger = { source = "hostinger/hostinger", version = "~> 0.1.7" } # 0.x: versión fija, revisa antes de subir
  }

  # El estado, en Object Storage de Oracle (Always Free), con bloqueo: dos "apply" a la vez no se pisan.
  # Configuración parcial: bucket, namespace y región en estado.oci.hcl (terraform init -backend-config=…).
  backend "oci" {}
}

provider "oci" {
  region              = var.oci_region
  config_file_profile = var.oci_perfil # ~/.oci/config: la API key de tu usuario de Oracle
}

provider "vercel" {
  team = var.vercel_equipo # el token, en VERCEL_API_TOKEN
}

provider "hostinger" {} # el token, en HOSTINGER_API_TOKEN (hPanel → API)
