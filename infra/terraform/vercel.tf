# infra/terraform/vercel.tf — el proyecto de Vercel, sus dominios y sus variables (módulo 86)
# Los despliegues NO los hace Terraform: los hace GitHub Actions con la CLI (desplegar.yml y preview.yml).

resource "vercel_project" "gastos" {
  name           = "gastos"
  root_directory = "frontend" # el framework y los comandos, en frontend/vercel.json (una sola fuente)
  # Conectado al repositorio solo para que el dominio de staging pueda ir "a la rama main". Vercel no despliega
  # nada por su cuenta: vercel.json lleva git.deploymentEnabled = false. Quien despliega es GitHub Actions.
  git_repository = {
    type = "github"
    repo = var.github_repo
  }
  git_comments = {
    on_commit       = false
    on_pull_request = false # el enlace de la preview lo comenta el workflow
  }
  # Las previews y staging, solo para quien tenga sesión en tu equipo de Vercel; producción, pública
  vercel_authentication = {
    deployment_type = "standard_protection_new"
  }
  enable_preview_feedback = false # la barra de Vercel en las previews: su script lo bloquearía nuestra CSP
}

# ── Dominios ──
resource "vercel_project_domain" "produccion" {
  project_id = vercel_project.gastos.id
  domain     = "gastos.${var.dominio}"
}

# Con rama: un dominio SIN rama se asigna solo a cada despliegue de PRODUCCIÓN. Además, el workflow lo
# asigna explícitamente (vercel alias set) a cada despliegue de staging.
resource "vercel_project_domain" "staging" {
  project_id = vercel_project.gastos.id
  domain     = "staging.gastos.${var.dominio}"
  git_branch = "main"
}

# Qué CNAME pide Vercel para cada subdominio (uno propio por proyecto: xxxx.vercel-dns-0xx.com)
data "vercel_domain_config" "produccion" {
  domain             = vercel_project_domain.produccion.domain
  project_id_or_name = vercel_project.gastos.id
}

data "vercel_domain_config" "staging" {
  domain             = vercel_project_domain.staging.domain
  project_id_or_name = vercel_project.gastos.id
}

# ── Variables de entorno: las lee vercel.json EN CADA PETICIÓN (routes → "env") ──
# Producción habla con la API de producción; las previews (y staging, que es una preview), con la de staging.
resource "vercel_project_environment_variable" "api_produccion" {
  project_id = vercel_project.gastos.id
  key        = "API_ORIGEN"
  value      = "https://api.gastos.${var.dominio}"
  target     = ["production"]
  sensitive  = false
}

resource "vercel_project_environment_variable" "api_staging" {
  project_id = vercel_project.gastos.id
  key        = "API_ORIGEN"
  value      = "https://api.staging.gastos.${var.dominio}"
  target     = ["preview"]
  sensitive  = false
}

resource "vercel_project_environment_variable" "secreto_produccion" {
  project_id       = vercel_project.gastos.id
  key              = "ORIGEN_SECRETO"
  value_wo         = var.origen_secreto_produccion # write-only: ni en el estado ni en el plan
  value_wo_version = var.version_secretos
  target           = ["production"]
  sensitive        = true # ni la API ni el panel de Vercel lo vuelven a mostrar
}

resource "vercel_project_environment_variable" "secreto_staging" {
  project_id       = vercel_project.gastos.id
  key              = "ORIGEN_SECRETO"
  value_wo         = var.origen_secreto_staging
  value_wo_version = var.version_secretos
  target           = ["preview"]
  sensitive        = true
}
