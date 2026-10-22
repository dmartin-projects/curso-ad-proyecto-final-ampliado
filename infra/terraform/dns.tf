# infra/terraform/dns.tf — los cuatro registros en el DNS de Hostinger (módulo 86)
# Solo se crean nombres NUEVOS bajo gastos.: el provider reemplaza, como mucho, los registros con el MISMO nombre
# y tipo. La raíz (@), www, el correo (MX) y lo demás de tudominio.com no se tocan.
# El dominio tiene que usar los nameservers de Hostinger; si no, crea estos registros donde esté su DNS.

locals {
  ip_vm = oci_core_public_ip.gastos.ip_address
}

resource "hostinger_dns_record" "front_produccion" {
  zone  = var.dominio
  name  = "gastos"
  type  = "CNAME"
  value = trimsuffix(data.vercel_domain_config.produccion.recommended_cname, ".")
  ttl   = 3600
}

resource "hostinger_dns_record" "front_staging" {
  zone  = var.dominio
  name  = "staging.gastos"
  type  = "CNAME"
  value = trimsuffix(data.vercel_domain_config.staging.recommended_cname, ".")
  ttl   = 3600
}

resource "hostinger_dns_record" "api_produccion" {
  zone  = var.dominio
  name  = "api.gastos"
  type  = "A"
  value = local.ip_vm
  ttl   = 3600
}

resource "hostinger_dns_record" "api_staging" {
  zone  = var.dominio
  name  = "api.staging.gastos"
  type  = "A"
  value = local.ip_vm
  ttl   = 3600
}
