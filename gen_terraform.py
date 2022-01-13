#!/usr/bin/env python
import click
import os

import jinja2
from python_terraform import Terraform
import pynetbox

@click.command()
@click.option('-c', '--cmdb-url', help='CMDB URL')
@click.option('-t', '--token', help='CMDB Token')
@click.option('--verify', default=None, help='CMDB Token')
@click.option('-s', '--service', default=None, help='Service name')
def run(cmdb_url, token, verify, service):
    # Setup the netbox api interface
    netbox = pynetbox.api(cmdb_url, token=token)
    # If SSL verify file provided, set the netbox Session object to use it
    if verify:
        netbox.http_session.verify = verify

    cluster_group = netbox.virtualization.cluster_groups.get(name=service)

    # Get all clusters within this service
    clusters = netbox.virtualization.clusters.filter(group_id=cluster_group.id)
    vms = list()
    for cluster in clusters:
        cluster_vms = netbox.virtualization.virtual_machines.filter(cluster_id=cluster.id)
        for vm in cluster_vms:
            vms.append(vm)

    tf_file = generate_terraform(vms, service)

    

    print(tf_file)

def generate_terraform(vms, service_name):
    base_path = os.path.dirname(os.path.realpath(__file__))
    base_module_path = os.path.join(base_path, 'terraform/modules/base')

    template_folder = os.path.join(base_path, 'templates')
    templateLoader = jinja2.FileSystemLoader(searchpath=template_folder)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "pac_server.tf"
    template = templateEnv.get_template(TEMPLATE_FILE)

    service_folder = os.path.join(base_path, 'terraform', service_name)
    if not os.path.isdir(service_folder):
        try:
            os.mkdir(service_folder)
        except OSError as e:
            print(e)

    tf_file = template.render(module_base=base_module_path, vms=vms)

    tf_filepath = os.path.join(service_folder, F'main.tf')
    with open(tf_filepath, 'w') as f:
        f.write(tf_file)

    return tf_file

if __name__ == "__main__":
    run()