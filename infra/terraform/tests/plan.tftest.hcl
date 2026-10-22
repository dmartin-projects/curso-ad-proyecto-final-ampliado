# infra/terraform/tests/plan.tftest.hcl — terraform test, SIN credenciales ni red (módulo 86): los providers
# son simulados (mock_provider) y se comprueba lo que se va a crear: nombres DNS, IPs, variables por entorno.

mock_provider "oci" {
  override_data {
    target = data.oci_core_images.ubuntu
    values = { images = [{ id = "ocid1.image.oc1..ubuntu2404" }] }
  }
  override_data {
    target = data.oci_identity_availability_domains.ads
    values = { availability_domains = [{ name = "AD-1" }] }
  }
  override_data {
    target = data.oci_core_vnic_attachments.gastos
    values = { vnic_attachments = [{ vnic_id = "ocid1.vnic.oc1..x" }] }
  }
  override_data {
    target = data.oci_core_private_ips.gastos
    values = { private_ips = [{ id = "ocid1.privateip.oc1..x" }] }
  }
  override_resource {
    target = oci_core_public_ip.gastos
    values = { ip_address = "203.0.113.10" }
  }
}

mock_provider "vercel" {
  override_data {
    target = data.vercel_domain_config.produccion
    values = { recommended_cname = "d1d4fc829fe7bc7c.vercel-dns-017.com." }
  }
  override_data {
    target = data.vercel_domain_config.staging
    values = { recommended_cname = "d1d4fc829fe7bc7c.vercel-dns-017.com." }
  }
}

mock_provider "hostinger" {}

variables {
  oci_region                = "eu-madrid-1"
  compartment_ocid          = "ocid1.tenancy.oc1..x"
  ssh_clave_publica         = "ssh-ed25519 AAAA prueba"
  dominio                   = "tudominio.com"
  vercel_equipo             = "davids-projects"
  github_repo               = "david/gastos"
  origen_secreto_produccion = "secreto-de-produccion"
  origen_secreto_staging    = "secreto-de-staging"
}

run "dns_y_vercel" {
  command = apply # con providers simulados: no toca nada real

  assert {
    condition     = hostinger_dns_record.api_produccion.name == "api.gastos" && hostinger_dns_record.api_produccion.value == "203.0.113.10"
    error_message = "api.gastos debe apuntar (A) a la IP reservada de la VM"
  }
  assert {
    condition     = hostinger_dns_record.api_staging.name == "api.staging.gastos" && hostinger_dns_record.api_staging.type == "A"
    error_message = "api.staging.gastos: registro A a la VM"
  }
  assert {
    condition     = hostinger_dns_record.front_produccion.type == "CNAME" && hostinger_dns_record.front_produccion.value == "d1d4fc829fe7bc7c.vercel-dns-017.com"
    error_message = "gastos: CNAME al valor que recomienda Vercel, sin el punto final"
  }
  assert {
    condition     = alltrue([for r in [hostinger_dns_record.front_produccion, hostinger_dns_record.front_staging, hostinger_dns_record.api_produccion, hostinger_dns_record.api_staging] : r.zone == "tudominio.com" && r.name != "@" && r.name != "www"])
    error_message = "Nunca se tocan la raíz ni www del dominio"
  }
  assert {
    condition     = vercel_project_environment_variable.api_produccion.target == toset(["production"]) && vercel_project_environment_variable.api_produccion.value == "https://api.gastos.tudominio.com"
    error_message = "Producción (Vercel) → API de producción"
  }
  assert {
    condition     = vercel_project_environment_variable.api_staging.target == toset(["preview"]) && vercel_project_environment_variable.api_staging.value == "https://api.staging.gastos.tudominio.com"
    error_message = "Previews y staging (Vercel) → API de staging"
  }
  assert {
    condition     = vercel_project_domain.staging.git_branch == "main" && vercel_project_domain.produccion.git_branch == null
    error_message = "El dominio de staging, de la rama main (si no, Vercel lo asignaría a producción)"
  }
  assert {
    condition     = length(hostinger_dns_record.correo_mx) == 0
    error_message = "Sin los valores de Resend, no se crean registros de correo"
  }
}

run "correo" {
  command = apply
  variables {
    resend_mx      = "feedback-smtp.eu-west-1.amazonses.com"
    resend_dkim    = "p=MIGfMA0prueba"
    dmarc_informes = "dmarc@tudominio.com"
  }
  assert {
    condition     = hostinger_dns_record.correo_mx[0].name == "send.gastos" && hostinger_dns_record.correo_mx[0].value == "10 feedback-smtp.eu-west-1.amazonses.com"
    error_message = "MX de rebotes en send.gastos"
  }
  assert {
    condition     = hostinger_dns_record.correo_dmarc[0].name == "_dmarc.gastos" && startswith(hostinger_dns_record.correo_dmarc[0].value, "v=DMARC1; p=none")
    error_message = "DMARC en _dmarc.gastos, empezando por p=none"
  }
  assert {
    condition     = !contains([for r in concat(hostinger_dns_record.correo_mx, hostinger_dns_record.correo_spf, hostinger_dns_record.correo_dkim, hostinger_dns_record.correo_dmarc) : r.name], "gastos")
    error_message = "Ningún registro de correo en 'gastos' (es un CNAME a Vercel: no admite más registros)"
  }
}
