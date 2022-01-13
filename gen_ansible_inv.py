#!/usr/bin/env python
import click
import os

import jinja2
import pynetbox

@click.command()
@click.option('-c', '--cmdb-url', help='CMDB URL')
@click.option('-t', '--token', help='CMDB Token')
@click.option('--verify', default=None, help='CMDB Token')
@click.option('-s', '--service', default=None, help='Service name')
@click.option('-r', '--role', default="test", help='Role name')
def run(cmdb_url, token, verify, service, role):
    # Setup the netbox api interface
    netbox = pynetbox.api(cmdb_url, token=token)
    # If SSL verify file provided, set the netbox Session object to use it
    if verify:
        netbox.http_session.verify = verify

    cluster_group = netbox.virtualization.cluster_groups.get(name=service)

    # Get all clusters within this service
    clusters = list()
    nb_clusters = netbox.virtualization.clusters.filter(group_id=cluster_group.id)
    vms = dict()
    for cluster in nb_clusters:
        clusters.append(cluster)
        cluster_vms = netbox.virtualization.virtual_machines.filter(cluster_id=cluster.id)
        vms[cluster.name] = list()
        for vm in cluster_vms:
            vms[cluster.name].append(vm)
    print(vms)

    inv = generate_inventory(clusters, vms, role)
    print(inv)

def generate_inventory(clusters, vms, role_folder):
    base_path = os.path.dirname(os.path.realpath(__file__))

    template_folder = os.path.join(base_path, 'templates')
    templateLoader = jinja2.FileSystemLoader(searchpath=template_folder)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "pac_inventory.yaml"

    template = templateEnv.get_template(TEMPLATE_FILE)

    service_folder = os.path.join(base_path, 'ansible', role_folder)
    if not os.path.isdir(service_folder):
        try:
            os.mkdir(service_folder)
        except OSError as e:
            print(e)

    inventory_file = template.render(clusters=clusters, vms=vms)

    # tf_filepath = os.path.join(service_folder, F'main.tf')
    # with open(tf_filepath, 'w') as f:
    #     f.write(inventory_file)

    return inventory_file

if __name__ == "__main__":
    run()