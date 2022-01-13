# fetch the latest ubuntu release image from their mirrors
resource "libvirt_volume" "os_image" {
  name = "${var.hostname}-os_image"
  pool = "default"
  source = "https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img"
  format = "qcow2"
}

resource "libvirt_volume" "disk_ubuntu_resized" {
  name           = "${var.hostname}-disk"
  base_volume_id = libvirt_volume.os_image.id
  pool           = "default"
  size           = 5361393152
}

# Setup Cloud Init ISO
resource "libvirt_cloudinit_disk" "commoninit" {
  name = "${var.hostname}-commoninit.iso"
  pool = "default"
  user_data = data.template_file.user_data.rendered
  network_config = data.template_file.network_config.rendered
}

# Template the Cloud Init config file
data "template_file" "user_data" {
  template = file("${path.module}/config/cloud_init.cfg")
  vars = {
    username = var.username
    hostname = var.hostname
    fqdn = "${var.hostname}.${var.domain}"
    base_path = "${path.module}"
    install_puppet = var.install_puppet
  }
}

# Template the network configuration with static IP
data "template_file" "network_config" {
  template = file("${path.module}/config/netconfig-${var.ip_type}.cfg")
  vars = {
    domain = var.domain
    subnet = var.subnet
    subnet_ip = var.subnet_ip
  }
}

# Create the machine
resource "libvirt_domain" "domain_ubuntu_base" {
  name = "${var.hostname}"
  memory = var.memoryMB
  vcpu = var.cpu

  disk {
    volume_id = libvirt_volume.disk_ubuntu_resized.id
  }
  network_interface {
    network_name = "virt_lan"
  }

  cloudinit = libvirt_cloudinit_disk.commoninit.id

}
