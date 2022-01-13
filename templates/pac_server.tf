{%- for vm in vms -%}
module "{{ vm.name }}" {
  source = {{ module_base }}
  hostname = "{{ vm.name }}"
  username = "kirimson"
  memoryMB = {{ vm.memory }}
  cpu = {{ vm.vcpus|int }}

  {%- if vm.primary_ip %}
  ip_type = "static"
  {%- set ip_address = vm.primary_ip.address.split('/')[0] %}
  {%- set octets = ip_address.split('.') %}
  subnet = "{{ octets[0:3]|join('.') }}"
  subnet_ip = "{{ octets[3] }}"
  {%- endif %}
}
{% endfor -%}