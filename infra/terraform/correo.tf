# infra/terraform/correo.tf — el correo de Gastos con tu dominio: Resend desde gastos.tudominio.com (módulo 86)
# Los valores los da Resend (Domains → Add domain → gastos.tudominio.com). Hasta que los pongas en
# terraform.tfvars, estos registros no se crean (count = 0).
# Ninguno está EN gastos.tudominio.com (ese nombre es un CNAME a Vercel y un CNAME no admite otros registros):
# van en send.gastos (SPF y rebotes), resend._domainkey.gastos (DKIM) y _dmarc.gastos (DMARC).

variable "resend_mx" {
  type        = string
  default     = ""
  description = "El MX de 'send' que muestra Resend, p. ej. feedback-smtp.eu-west-1.amazonses.com"
}
variable "resend_dkim" {
  type        = string
  default     = ""
  description = "El valor TXT de resend._domainkey (p=MIGfMA0…)"
}
variable "dmarc_informes" {
  type        = string
  default     = ""
  description = "Buzón para los informes DMARC (rua), p. ej. dmarc@tudominio.com"
}

locals {
  correo = var.resend_mx != "" && var.resend_dkim != "" ? 1 : 0
}

resource "hostinger_dns_record" "correo_mx" {
  count = local.correo
  zone  = var.dominio
  name  = "send.gastos"
  type  = "MX"
  value = "10 ${var.resend_mx}"
  ttl   = 3600
}

resource "hostinger_dns_record" "correo_spf" {
  count = local.correo
  zone  = var.dominio
  name  = "send.gastos"
  type  = "TXT"
  value = "v=spf1 include:amazonses.com ~all"
  ttl   = 3600
}

resource "hostinger_dns_record" "correo_dkim" {
  count = local.correo
  zone  = var.dominio
  name  = "resend._domainkey.gastos"
  type  = "TXT"
  value = var.resend_dkim
  ttl   = 3600
}

# DMARC: empieza en p=none (solo informa) y, con los informes limpios unas semanas, sube a p=quarantine
resource "hostinger_dns_record" "correo_dmarc" {
  count = local.correo
  zone  = var.dominio
  name  = "_dmarc.gastos"
  type  = "TXT"
  value = var.dmarc_informes != "" ? "v=DMARC1; p=none; rua=mailto:${var.dmarc_informes}" : "v=DMARC1; p=none"
  ttl   = 3600
}
