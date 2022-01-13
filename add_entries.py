#!/usr/bin/env python3
import yaml
import string
import random
import click

import pynetbox

@click.command()
@click.option('-c', '--cmdb-url', help='CMDB URL')
@click.option('-t', '--token', help='CMDB Token')
@click.option('--verify', default=None, help='CMDB Token')
@click.option('-f', '--file', default=None, help='Contract File')
def run(cmdb_url, token, verify, file):
    # Setup the netbox api interface
    netbox = pynetbox.api(cmdb_url, token=token)
    # If SSL verify file provided, set the netbox Session object to use it
    if verify:
        netbox.http_session.verify = verify

    # Load the contract, and load in from the near pointless "service_contract" key
    contract_data = yaml.safe_load(open(file, 'r').read())
    contract = contract_data['service_contract']

    # Get the tag object based on the coi. coi_tag.id is used to set the tag of objects
    coi_tag = netbox.extras.tags.get(slug=contract['coi'])

    # Set the description and slug name for the cluster group
    cluster_group_description = F"Service contract for {contract['name']}"
    cluster_group_slug = contract['name'].lower().replace(' ', '_')

    # Try and get the cluster group if it exists
    cluster_group = netbox.virtualization.cluster_groups.get(slug=cluster_group_slug)
    # If no cluster group exists with that slug make it
    if not cluster_group:
        metadata = {"automation": {
            "pod": contract['pod'],
            "coi": contract['coi'],
            "vdc": contract['vdc']
            }
        }

        # Create the cluster group. this will be the top level cluster for the service
        cluster_group = netbox.virtualization.cluster_groups.create(name=contract['name'],
            slug=cluster_group_slug, description=cluster_group_description,
            custom_fields={"metadata":metadata}, tags=[coi_tag.id])
        print(F"Created Cluster Group: {cluster_group}")
    else:
        print(F"Cluster Group: {cluster_group} Already Exists. Continuing...")

    for cluster in contract['clusters']:
        create_cluster(netbox, contract['clusters'][cluster], cluster_group, cluster, coi_tag)

def create_cluster(netbox, cluster_data, cluster_group, base_name, coi_tag):
    # Try and get the cluster if it exists
    cluster_name = F"{cluster_group.name}-{base_name}"

    nb_cluster = netbox.virtualization.clusters.get(group_id=cluster_group.id, name=cluster_name)
    if not nb_cluster:
        # Setup metadata custom field dict if metadata is present
        metadata = {"automation": {
            "networks": cluster_data['networks'],
            }
        }
        if cluster_data.get("vips"):
            metadata["automation"]["vips"] = cluster_data['vips']
        if cluster_data.get("metadata"):
            metadata.update(cluster_data['metadata'])
        
        # Create the cluster, within the cluster group (main service)
        nb_cluster = netbox.virtualization.clusters.create(name=cluster_name,
                type=1, group=cluster_group.id, custom_fields={"metadata":metadata},
                tags=[coi_tag.id])
        print(F"Created Cluster: {nb_cluster}")
    else:
        print(F"Cluster: {nb_cluster} Already Exists. Continuing...")

    for vm in cluster_data['vms']:
        create_vm(netbox, cluster_data['vms'][vm], nb_cluster, vm, coi_tag)

def create_vm(netbox, vm_data, nb_cluster, base_name, coi_tag):

    # Check if the cluster contains this vm already, based on server comment name
    existing_vms = netbox.virtualization.virtual_machines.filter(cluster_id=nb_cluster.id)
    for existing_vm in existing_vms:
        if existing_vm.comments == base_name:
            print(F"VM: {base_name} Already Exists. Continuing...")
            return

    # Setup metadata custom field dict if metadata is present
    metadata = {"automation": {
        "networks": vm_data['networks'],
        "os": vm_data['os']
        }
    }
    if vm_data.get("metadata"):
        metadata.update(vm_data['metadata'])

    # Set the suffix based on coi name
    vm_name = str()
    il = "i2" if coi_tag.slug == "assured" else "i3" if coi_tag.slug == "elevated" else "ix" 
    # Generate a random UID for the VM. If already taken, give it another go
    while True:
        vm_id = ''.join(random.choices(string.digits, k=5))
        vm_name = F"{vm_data['trigram']}{vm_id}{il}"
        existing_vm = netbox.virtualization.virtual_machines.get(name=vm_name)
        if existing_vm == None:
            break

    # Netbox stores RAM in mb, so need to convert first
    ram_mb = 1024*int(vm_data['ram'])
    # Create the VM and add to the cluster
    nb_vm = netbox.virtualization.virtual_machines.create(name=vm_name,
        cluster=nb_cluster.id, status="active", tags=[coi_tag.id], comments=base_name,
        memory=ram_mb, vcpus=vm_data['cores'], custom_fields={"metadata":metadata})
    vm_interface = netbox.virtualization.interfaces.create(virtual_machine=nb_vm.id, name="mgmt")
    print(F"Created VM: {vm_name} ({nb_vm})")
    print(F"Added interface {vm_interface} to {nb_vm}")

    available_ip = None
    # If vm is using cmdb for IP assignment, get a free IP
    if vm_data['ip_source'] == "cmdb":
        subnet = get_subnet(netbox, vm_data['networks'][0])
        available_ip = subnet.available_ips.create()
        # Add the IP address to the interface
        update_data = {
            "id": available_ip.id,
            "assigned_object_type": "virtualization.vminterface",
            "assigned_object_id": vm_interface.id
            }
        netbox.ipam.ip_addresses.update([update_data])
        
        # Set the primary IP address to the newly added IP address
        update_data = {
            "id": nb_vm.id,
            "primary_ip4": available_ip.id
            }
        netbox.virtualization.virtual_machines.update([update_data])

def get_subnet(netbox, subnet_description):
    subnets = netbox.ipam.prefixes.all()
    for subnet in subnets:
        if subnet.description == subnet_description:
            return subnet
    return None

if __name__ == "__main__":
    run()