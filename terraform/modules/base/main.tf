# Setup the provider
terraform {
  required_providers {
    libvirt = {
      source = "dmacvicar/libvirt"
    }
  }
}

provider "libvirt" {
  uri = "qemu+ssh://kirimson@192.168.122.1/system?keyfile=/opt/rundeck/id_rsa"
}
