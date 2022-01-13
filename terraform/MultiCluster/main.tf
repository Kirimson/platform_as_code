module "apl96917i2" {
  source = /home/kirimson/Documents/interviewtask/platform_as_code/terraform/modules/base
  hostname = "apl96917i2"
  username = "kirimson"
  memoryMB = 1024
  cpu = 1
  ip_type = "static"
  subnet = "192.168.100"
  subnet_ip = "131"
}
module "apl06649i2" {
  source = /home/kirimson/Documents/interviewtask/platform_as_code/terraform/modules/base
  hostname = "apl06649i2"
  username = "kirimson"
  memoryMB = 1024
  cpu = 1
  ip_type = "static"
  subnet = "192.168.100"
  subnet_ip = "132"
}
