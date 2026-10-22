# infra/terraform/outputs.tf (módulo 86)
output "ip_vm" {
  description = "La IP pública reservada de la VM (registros A de api.gastos y api.staging.gastos)"
  value       = oci_core_public_ip.gastos.ip_address
}

output "ssh" {
  value = "ssh ubuntu@${oci_core_public_ip.gastos.ip_address}"
}

output "vercel_project_id" {
  description = "Para GitHub: variable VERCEL_PROJECT_ID"
  value       = vercel_project.gastos.id
}

output "vercel_team_id" {
  description = "Para GitHub: variable VERCEL_ORG_ID"
  value       = vercel_project.gastos.team_id
}

output "urls" {
  value = {
    produccion = "https://gastos.${var.dominio}  →  https://api.gastos.${var.dominio}"
    staging    = "https://staging.gastos.${var.dominio}  →  https://api.staging.gastos.${var.dominio}"
  }
}
