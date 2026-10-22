# infra/terraform/oci.tf — la red y la VM Always Free de Oracle (módulos 68 y 86)
# ¿Ya tienes la VM del módulo 68? No la crees otra vez: impórtala (importar.tf.example).

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_ocid
}

# La última Ubuntu 24.04 para ARM. Cambia con el tiempo: por eso la VM ignora source_id (abajo).
data "oci_core_images" "ubuntu" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "24.04"
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_vcn" "gastos" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "gastos"
  dns_label      = "gastos"
}

resource "oci_core_internet_gateway" "gastos" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.gastos.id
  display_name   = "gastos"
}

resource "oci_core_route_table" "publica" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.gastos.id
  display_name   = "publica"
  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.gastos.id
  }
}

# El cortafuegos de la nube (el primero de los tres sitios del módulo 68; el segundo, iptables, en cloud-init)
resource "oci_core_security_list" "publica" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.gastos.id
  display_name   = "publica"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
  ingress_security_rules {
    description = "SSH (solo con clave; fail2ban, módulo 67)"
    protocol    = "6" # TCP
    source      = var.ssh_desde
    tcp_options {
      min = 22
      max = 22
    }
  }
  dynamic "ingress_security_rules" {
    for_each = [80, 443]
    content {
      description = "Caddy: HTTP (certificados) y HTTPS"
      protocol    = "6"
      source      = "0.0.0.0/0"
      tcp_options {
        min = ingress_security_rules.value
        max = ingress_security_rules.value
      }
    }
  }
  ingress_security_rules {
    description = "HTTP/3 (QUIC)"
    protocol    = "17" # UDP
    source      = "0.0.0.0/0"
    udp_options {
      min = 443
      max = 443
    }
  }
}

resource "oci_core_subnet" "publica" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.gastos.id
  cidr_block        = "10.0.0.0/24"
  display_name      = "publica"
  dns_label         = "publica"
  route_table_id    = oci_core_route_table.publica.id
  security_list_ids = [oci_core_security_list.publica.id]
}

resource "oci_core_instance" "gastos" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "gastos"
  shape               = "VM.Standard.A1.Flex"

  shape_config { # Always Free: hasta 4 OCPU y 24 GB en total; aquí, lo del módulo 68
    ocpus         = 2
    memory_in_gbs = 12
  }

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.ubuntu.images[0].id
    boot_volume_size_in_gbs = "100"
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.publica.id
    assign_public_ip = "false" # la pública es la RESERVADA de abajo: no cambia aunque pares la VM
    hostname_label   = "gastos"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_clave_publica
    user_data           = base64encode(file("${path.module}/cloud-init.yaml"))
  }

  lifecycle {
    prevent_destroy = true # aquí viven las bases de datos: un "apply" nunca debe poder borrarla
    # Una imagen más nueva o un cloud-init distinto obligarían a RECREAR la VM (con sus datos dentro)
    ignore_changes = [source_details[0].source_id, metadata["user_data"]]
  }
}

# La IP pública RESERVADA (módulo 68): es la que apuntan los registros A de api.gastos y api.staging.gastos
data "oci_core_vnic_attachments" "gastos" {
  compartment_id = var.compartment_ocid
  instance_id    = oci_core_instance.gastos.id
}

data "oci_core_private_ips" "gastos" {
  vnic_id = data.oci_core_vnic_attachments.gastos.vnic_attachments[0].vnic_id
}

resource "oci_core_public_ip" "gastos" {
  compartment_id = var.compartment_ocid
  lifetime       = "RESERVED"
  display_name   = "gastos"
  private_ip_id  = data.oci_core_private_ips.gastos.private_ips[0].id
  lifecycle {
    prevent_destroy = true # perderla = cambiar el DNS y esperar a que se propague
  }
}
