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
module: cloud_manager
short_description: Manages resources in Hyperstack Cloud.
version_added: "1.0.0"
description:
    - This is a module for managing Hyperstack Cloud resources like environments,
      firewalls, and virtual machines.
options:
    name:
        description:
            - The name of the cloud environment to manage.
        type: str
        required: true
    state:
        description:
            - The desired state of the environment.
        type: str
        default: present
        choices:
            - present
            - absent
    firewall_rules:
        description:
            - A list of firewall rules to apply to the environment.
            - Any rules not in this list will be removed.
        type: list
        elements: dict
        suboptions:
            protocol:
                description: The network protocol.
                type: str
                choices: [ tcp, udp ]
                required: true
            port:
                description: The port number.
                type: int
                required: true
    vms:
        description:
            - A list of virtual machines to manage within the environment.
        type: list
        elements: dict
        suboptions:
            name:
                description: The name of the virtual machine.
                type: str
                required: true
            size:
                description: The size of the VM (e.g., small, medium, large).
                type: str
                required: true
            image:
                description: The OS image to use for the VM.
                type: str
                required: true
            state:
                description: The desired state of the VM.
                type: str
                default: running
                choices: [ present, running, stopped, absent ]
author:
    - Your Name (@yourgithubhandle)
"""

EXAMPLES = r"""
- name: Ensure the 'staging' environment exists
  hyperstack.cloud.cloud_manager:
    name: staging
    state: present

- name: Ensure the 'dev' environment is removed
  hyperstack.cloud.cloud_manager:
    name: dev
    state: absent

- name: Create environment with firewall rules
  hyperstack.cloud.cloud_manager:
    name: web-server
    state: present
    firewall_rules:
      - protocol: tcp
        port: 80
      - protocol: tcp
        port: 443
      - protocol: udp
        port: 53

- name: Update firewall rules (remove HTTP, keep HTTPS and DNS)
  hyperstack.cloud.cloud_manager:
    name: web-server
    state: present
    firewall_rules:
      - protocol: tcp
        port: 443
      - protocol: udp
        port: 53

- name: Clear all firewall rules
  hyperstack.cloud.cloud_manager:
    name: web-server
    state: present
    firewall_rules: []

- name: Create environment with VMs
  hyperstack.cloud.cloud_manager:
    name: production
    state: present
    vms:
      - name: web-01
        size: small
        image: ubuntu-22.04
        state: running
      - name: web-02
        size: small
        image: ubuntu-22.04
        state: running
      - name: db-01
        size: large
        image: rhel-9
        state: running

- name: Stop a specific VM
  hyperstack.cloud.cloud_manager:
    name: production
    state: present
    vms:
      - name: web-02
        size: small
        image: ubuntu-22.04
        state: stopped

- name: Remove a VM
  hyperstack.cloud.cloud_manager:
    name: production
    state: present
    vms:
      - name: web-02
        size: small
        image: ubuntu-22.04
        state: absent

- name: Complex environment with firewall and VMs
  hyperstack.cloud.cloud_manager:
    name: full-stack
    state: present
    firewall_rules:
      - protocol: tcp
        port: 80
      - protocol: tcp
        port: 443
      - protocol: tcp
        port: 22
    vms:
      - name: load-balancer
        size: medium
        image: ubuntu-22.04
        state: running
      - name: app-server-01
        size: small
        image: ubuntu-22.04
        state: running
      - name: app-server-02
        size: small
        image: ubuntu-22.04
        state: running
      - name: database
        size: large
        image: rhel-9
        state: running
"""

RETURN = r"""
changed:
    description: Whether the module made any changes
    type: bool
    returned: always
name:
    description: The name of the environment
    type: str
    returned: always
state:
    description: The state of the environment
    type: str
    returned: always
msg:
    description: A message describing what happened
    type: str
    returned: always
diff:
    description: Difference between current and desired firewall rules
    type: dict
    returned: when changes are made to firewall rules
    contains:
        before:
            description: Current firewall rules before changes
            type: str
            returned: when firewall rules change
        after:
            description: Desired firewall rules after changes
            type: str
            returned: when firewall rules change
failed:
    description: Indicates if the module failed
    type: bool
    returned: when module encounters an error
"""

import os
import json
import tempfile
from ansible.module_utils.basic import AnsibleModule

# Set of valid images to simulate an API constraint
_VALID_IMAGES = {"ubuntu-22.04", "rhel-9"}

# File-based persistence for mock state (needed for idempotency testing)
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


def _save_state(state):
    """Save mock state to file."""
    try:
        with open(_STATE_FILE, 'w') as f:
            json.dump(state, f)
    except IOError:
        pass


def get_environment(name):
    """Simulates fetching an environment from the cloud API."""
    state = _load_state()
    return state.get(name)


def create_environment(name):
    """Simulates creating a new environment."""
    # In a real module, this would be an API call
    state = _load_state()
    state[name] = {"id": f"env-{hash(name)}", "status": "active"}
    _save_state(state)


def delete_environment(name):
    """Simulates deleting an environment."""
    # In a real module, this would be an API call
    state = _load_state()
    if name in state:
        del state[name]
    _save_state(state)


def _normalize_rules(rules):
    """Sorts a list of rule dictionaries to allow for consistent comparison."""
    if not rules:
        return []
    # Sort by a tuple of values to ensure a deterministic order
    return sorted(rules, key=lambda r: (r["protocol"], r["port"]))


def format_rules_for_display(rules):
    """Format rules for display in diff output."""
    if not rules:
        return ""
    return ", ".join([f"{rule['protocol']}:{rule['port']}" for rule in rules])


def create_vm(env_name, vm_spec):
    """Simulates creating a VM, with potential for failure."""
    if vm_spec["image"] not in _VALID_IMAGES:
        raise ValueError(f"Image '{vm_spec['image']}' not found.")

    state = _load_state()
    if env_name in state:
        if "vms" not in state[env_name]:
            state[env_name]["vms"] = {}
        state[env_name]["vms"][vm_spec["name"]] = {
            "name": vm_spec["name"],
            "size": vm_spec["size"],
            "image": vm_spec["image"],
            "status": "running"
        }
        _save_state(state)


def delete_vm(env_name, vm_name):
    """Simulates deleting a VM."""

    state = _load_state()
    if env_name in state and "vms" in state[env_name] and vm_name in state[env_name]["vms"]:
        del state[env_name]["vms"][vm_name]
        _save_state(state)


def start_vm(env_name, vm_name):
    """Simulates starting a VM."""

    state = _load_state()
    if env_name in state and "vms" in state[env_name] and vm_name in state[env_name]["vms"]:
        state[env_name]["vms"][vm_name]["status"] = "running"
        _save_state(state)


def stop_vm(env_name, vm_name):
    """Simulates stopping a VM."""

    state = _load_state()
    if env_name in state and "vms" in state[env_name] and vm_name in state[env_name]["vms"]:
        state[env_name]["vms"][vm_name]["status"] = "stopped"
        _save_state(state)


def main():
    """Main execution path of the module."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            firewall_rules=dict(
                type="list",
                elements="dict",
                options=dict(
                    protocol=dict(type="str", required=True, choices=["tcp", "udp"]),
                    port=dict(type="int", required=True),
                ),
                default=None,
            ),
            vms=dict(
                type="list",
                elements="dict",
                options=dict(
                    name=dict(type="str", required=True),
                    size=dict(type="str", required=True),
                    image=dict(type="str", required=True),
                    state=dict(
                        type="str",
                        default="running",
                        choices=["present", "running", "stopped", "absent"],
                    ),
                ),
                default=None,
            ),
        ),
        supports_check_mode=True,
    )

    name = module.params["name"]
    state = module.params["state"]
    desired_rules = module.params["firewall_rules"]
    desired_vms = module.params["vms"]

    result = dict(changed=False, name=name, state=state)

    # Environment State Management (from Mission 2)
    current_env = get_environment(name)
    if state == "present" and current_env is None:
        if not module.check_mode:
            create_environment(name)
        result["changed"] = True
        result["msg"] = f"Environment '{name}' created successfully."
    elif state == "present" and current_env is not None:
        # Environment already exists, no change needed
        pass
    elif state == "absent" and current_env is not None:
        if not module.check_mode:
            delete_environment(name)
        result["changed"] = True
        result["msg"] = f"Environment '{name}' deleted successfully."
        module.exit_json(**result)  # Exit early if deleting

    # If we are ensuring presence, check firewall rules
    if state == "present" and desired_rules is not None:
        # In a real module, this would be another API call
        current_rules = current_env.get("rules", []) if current_env else []

        # Normalize for comparison
        norm_current = _normalize_rules(current_rules)
        norm_desired = _normalize_rules(desired_rules)

        if norm_current != norm_desired:
            result["changed"] = True
            result["diff"] = {
                "before": "\n".join([f"{r['protocol']}:{r['port']}" for r in norm_current]),
                "after": "\n".join([f"{r['protocol']}:{r['port']}" for r in norm_desired]),
            }
            if not module.check_mode:
                # In a real module, this would be an API call to set the rules
                state = _load_state()
                if name in state:
                    state[name]["rules"] = desired_rules
                    _save_state(state)
            if not result.get("msg"):
                result["msg"] = f"Firewall rules updated for environment '{name}'."

    # VM Management (Mission 4)
    if state == "present" and desired_vms is not None:
        # In a real module, get the current list of VMs via an API call
        current_vms = current_env.get("vms", {}) if current_env else {}

        for vm_spec in desired_vms:
            vm_name = vm_spec["name"]
            vm_state = vm_spec.get("state", "running")
            current_vm = current_vms.get(vm_name)

            try:
                if vm_state in ["present", "running"] and current_vm is None:
                    # Create new VM
                    if not module.check_mode:
                        create_vm(name, vm_spec)
                    result["changed"] = True
                    if not result.get("msg"):
                        result["msg"] = f"VM '{vm_name}' created in environment '{name}'."

                elif vm_state == "running" and current_vm and current_vm.get("status") != "running":
                    # Start existing VM
                    if not module.check_mode:
                        start_vm(name, vm_name)
                    result["changed"] = True
                    if not result.get("msg"):
                        result["msg"] = f"VM '{vm_name}' started in environment '{name}'."

                elif vm_state == "stopped" and current_vm and current_vm.get("status") != "stopped":
                    # Stop existing VM
                    if not module.check_mode:
                        stop_vm(name, vm_name)
                    result["changed"] = True
                    if not result.get("msg"):
                        result["msg"] = f"VM '{vm_name}' stopped in environment '{name}'."

                elif vm_state == "absent" and current_vm is not None:
                    # Delete VM
                    if not module.check_mode:
                        delete_vm(name, vm_name)
                    result["changed"] = True
                    if not result.get("msg"):
                        result["msg"] = f"VM '{vm_name}' deleted from environment '{name}'."

            except ValueError as e:
                # Catch specific expected errors and provide tailored messages
                module.fail_json(msg=f"Failed to manage VM '{vm_name}': {e}")
            except Exception as e:
                # Generic catch-all for unexpected errors
                module.fail_json(msg=f"An unexpected error occurred while managing VM '{vm_name}': {e}")

    if not result.get("msg"):
        result["msg"] = f"Environment '{name}' is in desired state."

    module.exit_json(**result)


if __name__ == "__main__":
    main()
