variable "hostname" {
  type = string
  default = "base"
}

variable "domain" {
  type = string
  default = "internal.local"
}

variable "memoryMB" {
  type = number
  default = 1024*1
}

variable "cpu" {
  default = 1
}

variable "subnet" {
  type = string
  default = "192.168.100"
}

variable "subnet_ip" {
  type = string
  default = null
}

variable "username" {
  type = string
  default = "base"
}

variable "ip_type" {
  type = string
  default = "dhcp"
}

variable "install_puppet" {
  type = bool
  default = true
}
