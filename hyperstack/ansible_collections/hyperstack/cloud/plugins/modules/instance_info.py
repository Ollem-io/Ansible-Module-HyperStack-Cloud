#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
module: instance_info
short_description: Retrieves information about VM instances in Hyperstack Cloud
version_added: "1.0.0"
description:
    - Retrieves detailed information about virtual machine instances in Hyperstack Cloud.
    - Can query instances by name, IP address, or retrieve all instances in an environment.
    - Useful for dynamic infrastructure discovery and instance state validation.
options:
    name:
        description:
            - The name of the specific instance to query.
            - Mutually exclusive with ip_address and environment.
        type: str
        required: false
    ip_address:
        description:
            - The public or private IP address of the instance to query.
            - Mutually exclusive with name and environment.
        type: str
        required: false
    environment:
        description:
            - The environment name to query all instances from.
            - Mutually exclusive with name and ip_address.
        type: str
        required: false
    instance_states:
        description:
            - Filter instances by their current state.
            - Can be used with environment parameter.
        type: list
        elements: str
        choices: [ running, stopped, hibernated, pending, terminated ]
        default: []
author:
    - Your Name (@yourgithubhandle)
"""

EXAMPLES = r"""
- name: Get information about a specific instance by name
  dsmello.cloud.instance_info:
    name: "web-server-01"
  register: instance_details

- name: Get information about an instance by IP address
  dsmello.cloud.instance_info:
    ip_address: "192.168.1.100"
  register: instance_by_ip

- name: Get all instances in an environment
  dsmello.cloud.instance_info:
    environment: "production"
  register: all_instances

- name: Get only running instances in an environment
  dsmello.cloud.instance_info:
    environment: "production"
    instance_states: ["running"]
  register: running_instances

- name: Get hibernated instances across all environments
  dsmello.cloud.instance_info:
    instance_states: ["hibernated"]
  register: hibernated_instances

- name: Use instance info for conditional operations
  dsmello.cloud.instance:
    name: "{{ item.name }}"
    state: running
  loop: "{{ hibernated_instances.instances }}"
  when: hibernated_instances.instances | length > 0
"""

RETURN = r"""
instances:
    description: List of instances matching the query criteria
    type: list
    returned: always
    elements: dict
    contains:
        name:
            description: The name of the instance
            type: str
            returned: always
        state:
            description: Current state of the instance
            type: str
            returned: always
        public_ip:
            description: Public IP address of the instance
            type: str
            returned: when available
        private_ip:
            description: Private IP address of the instance
            type: str
            returned: when available
        size:
            description: Instance size/flavor
            type: str
            returned: always
        image:
            description: Operating system image
            type: str
            returned: always
        environment:
            description: Environment the instance belongs to
            type: str
            returned: always
        created_at:
            description: Instance creation timestamp
            type: str
            returned: always
        last_seen:
            description: Last activity timestamp
            type: str
            returned: always
count:
    description: Number of instances returned
    type: int
    returned: always
query:
    description: The query parameters used
    type: dict
    returned: always
"""

import os
import json
import tempfile
import ipaddress
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule

_STATE_FILE = os.path.join(tempfile.gettempdir(), "hyperstack_mock_state.json")


def _load_state():
    """Load mock state from file."""
    if os.path.exists(_STATE_FILE):
        try:
            with open(_STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"production": {"id": "env-123", "status": "active"}}


def _generate_mock_ip():
    """Generate a mock IP address for demonstration."""
    import random
    return f"192.168.{random.randint(1, 255)}.{random.randint(1, 254)}"


def _generate_instance_details(env_name, vm_name, vm_data):
    """Generate detailed instance information."""
    return {
        "name": vm_name,
        "state": vm_data.get("status", "unknown"),
        "public_ip": vm_data.get("public_ip", _generate_mock_ip()),
        "private_ip": vm_data.get("private_ip", f"10.0.{hash(vm_name) % 255}.{hash(env_name) % 254}"),
        "size": vm_data.get("size", "unknown"),
        "image": vm_data.get("image", "unknown"),
        "environment": env_name,
        "created_at": vm_data.get("created_at", "2024-01-01T00:00:00Z"),
        "last_seen": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def get_instance_by_name(name):
    """Find instance by name across all environments."""
    state = _load_state()
    for env_name, env_data in state.items():
        if "vms" in env_data:
            for vm_name, vm_data in env_data["vms"].items():
                if vm_name == name:
                    return _generate_instance_details(env_name, vm_name, vm_data)
    return None


def get_instance_by_ip(ip_address):
    """Find instance by IP address across all environments."""
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return None
    
    state = _load_state()
    for env_name, env_data in state.items():
        if "vms" in env_data:
            for vm_name, vm_data in env_data["vms"].items():
                instance_details = _generate_instance_details(env_name, vm_name, vm_data)
                if instance_details["public_ip"] == ip_address or instance_details["private_ip"] == ip_address:
                    return instance_details
    return None


def get_instances_in_environment(env_name):
    """Get all instances in a specific environment."""
    state = _load_state()
    instances = []
    
    if env_name in state and "vms" in state[env_name]:
        for vm_name, vm_data in state[env_name]["vms"].items():
            instances.append(_generate_instance_details(env_name, vm_name, vm_data))
    
    return instances


def get_all_instances():
    """Get all instances across all environments."""
    state = _load_state()
    instances = []
    
    for env_name, env_data in state.items():
        if "vms" in env_data:
            for vm_name, vm_data in env_data["vms"].items():
                instances.append(_generate_instance_details(env_name, vm_name, vm_data))
    
    return instances


def filter_instances_by_state(instances, desired_states):
    """Filter instances by their current state."""
    if not desired_states:
        return instances
    
    return [instance for instance in instances if instance["state"] in desired_states]


def main():
    """Main execution path of the module."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=False),
            ip_address=dict(type="str", required=False),
            environment=dict(type="str", required=False),
            instance_states=dict(
                type="list",
                elements="str",
                choices=["running", "stopped", "hibernated", "pending", "terminated"],
                default=[]
            ),
        ),
        mutually_exclusive=[
            ["name", "ip_address", "environment"]
        ],
        supports_check_mode=True,
    )

    name = module.params["name"]
    ip_address = module.params["ip_address"]
    environment = module.params["environment"]
    instance_states = module.params["instance_states"]

    instances = []
    query_params = {
        "name": name,
        "ip_address": ip_address,
        "environment": environment,
        "instance_states": instance_states
    }

    try:
        if name:
            instance = get_instance_by_name(name)
            if instance:
                instances = [instance]
        elif ip_address:
            instance = get_instance_by_ip(ip_address)
            if instance:
                instances = [instance]
        elif environment:
            instances = get_instances_in_environment(environment)
        else:
            instances = get_all_instances()

        instances = filter_instances_by_state(instances, instance_states)

        result = {
            "changed": False,
            "instances": instances,
            "count": len(instances),
            "query": {k: v for k, v in query_params.items() if v is not None}
        }

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve instance information: {str(e)}")


if __name__ == "__main__":
    main()