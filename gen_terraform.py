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

    print(cluster_group)

    

    # tf_file = generate_terraform(None)
    # print(tf_file)

def generate_terraform(vms):
    base_path = os.path.dirname(os.path.realpath(__file__))
    base_module_path = os.path.join(base_path, 'terraform/modules/base')

    template_folder = os.path.join(base_path, 'templates')
    templateLoader = jinja2.FileSystemLoader(searchpath=template_folder)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "pac_server.tf"
    template = templateEnv.get_template(TEMPLATE_FILE)
    return template.render(module_base=base_module_path)

if __name__ == "__main__":
    run()