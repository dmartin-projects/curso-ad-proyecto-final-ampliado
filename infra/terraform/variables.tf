# infra/terraform/variables.tf (módulo 86). Los valores, en terraform.tfvars (plantilla: terraform.tfvars.example)

# ── Oracle Cloud ──
variable "oci_region" {
  type        = string
  description = "La región de origen de tu cuenta (la Always Free solo vale ahí), p. ej. eu-madrid-1"
}
variable "oci_perfil" {
  type    = string
  default = "DEFAULT"
}
variable "compartment_ocid" {
  type        = string
  description = "Compartimento donde crear la red y la VM (el raíz es el OCID de la tenancy)"
}
variable "ssh_clave_publica" {
  type        = string
  description = "Contenido de ~/.ssh/id_ed25519.pub"
}
variable "ssh_desde" {
  type        = string
  default     = "0.0.0.0/0"
  description = "Desde dónde se permite SSH. Mejor tu IP/32 (y GitHub Actions entra por SSH: ver el módulo)"
}

# ── Nombres ──
variable "dominio" {
  type        = string
  description = "Tu dominio en Hostinger, p. ej. tudominio.com. Se crean gastos., staging.gastos., api.gastos. y api.staging.gastos."
}

# ── Vercel ──
variable "vercel_equipo" {
  type        = string
  description = "Slug de tu equipo (scope) de Vercel: el que aparece en sus URLs, p. ej. davids-projects"
}
variable "github_repo" {
  type        = string
  description = "usuario/repositorio en GitHub (solo para asignar el dominio de staging a la rama main)"
}
# Los secretos de Vercel → Caddy: los mismos valores que ORIGEN_SECRETO en infra/secretos/<entorno>.env.
# ephemeral + value_wo: Terraform los envía a Vercel pero NO los guarda ni en el estado ni en el plan.
#   export TF_VAR_origen_secreto_produccion=$(sops decrypt --extract '["ORIGEN_SECRETO"]' ../secretos/produccion.env)
variable "origen_secreto_produccion" {
  type      = string
  sensitive = true
  ephemeral = true
}
variable "origen_secreto_staging" {
  type      = string
  sensitive = true
  ephemeral = true
}
variable "version_secretos" {
  type        = number
  default     = 1
  description = "Súbelo (2, 3…) al rotar los secretos: los atributos write-only no se comparan, solo se reenvían si cambia esto"
}
