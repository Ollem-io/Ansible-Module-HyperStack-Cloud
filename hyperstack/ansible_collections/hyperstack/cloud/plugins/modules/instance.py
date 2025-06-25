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
module: instance
short_description: Manages individual VM instances in Hyperstack Cloud
version_added: "1.0.0"
description:
    - Manages the state of individual virtual machine instances in Hyperstack Cloud.
    - Provides direct instance control for start, stop, restart, and termination operations.
    - Useful for dynamic instance lifecycle management and hibernated instance revival.
options:
    name:
        description:
            - The name of the instance to manage.
        type: str
        required: true
    state:
        description:
            - The desired state of the instance.
        type: str
        default: running
        choices:
            - running
            - stopped
            - restarted
            - terminated
    wait:
        description:
            - Whether to wait for the operation to complete.
        type: bool
        default: true
    wait_timeout:
        description:
            - Maximum time to wait for the operation to complete (in seconds).
        type: int
        default: 300
    force:
        description:
            - Force the operation even if the instance is in an unexpected state.
            - Use with caution as this may cause data loss.
        type: bool
        default: false
author:
    - Your Name (@yourgithubhandle)
"""

EXAMPLES = r"""
- name: Start a hibernated instance
  dsmello.cloud.instance:
    name: "web-server-01"
    state: running

- name: Stop a running instance
  dsmello.cloud.instance:
    name: "web-server-01"
    state: stopped

- name: Restart an instance
  dsmello.cloud.instance:
    name: "web-server-01"
    state: restarted

- name: Terminate an instance (permanent deletion)
  dsmello.cloud.instance:
    name: "web-server-01"
    state: terminated
    force: true

- name: Start instance without waiting for completion
  dsmello.cloud.instance:
    name: "web-server-01"
    state: running
    wait: false

- name: Start instance with custom timeout
  dsmello.cloud.instance:
    name: "web-server-01"
    state: running
    wait: true
    wait_timeout: 600

- name: Dynamic hibernated instance revival
  block:
    - name: Find hibernated instances
      dsmello.cloud.instance_info:
        instance_states: ["hibernated"]
      register: hibernated_vms

    - name: Start hibernated instances
      dsmello.cloud.instance:
        name: "{{ item.name }}"
        state: running
      loop: "{{ hibernated_vms.instances }}"
      when: hibernated_vms.count > 0
"""

RETURN = r"""
changed:
    description: Whether the module made any changes
    type: bool
    returned: always
instance:
    description: Instance information after the operation
    type: dict
    returned: always
    contains:
        name:
            description: The name of the instance
            type: str
            returned: always
        state:
            description: Current state of the instance
            type: str
            returned: always
        previous_state:
            description: Previous state before the operation
            type: str
            returned: when state changed
        public_ip:
            description: Public IP address of the instance
            type: str
            returned: when available
        private_ip:
            description: Private IP address of the instance
            type: str
            returned: when available
        environment:
            description: Environment the instance belongs to
            type: str
            returned: always
operation:
    description: The operation that was performed
    type: str
    returned: always
duration:
    description: Time taken for the operation in seconds
    type: float
    returned: when wait is true
msg:
    description: A message describing what happened
    type: str
    returned: always
"""

import os
import json
import time
import tempfile
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


def _save_state(state):
    """Save mock state to file."""
    try:
        with open(_STATE_FILE, 'w') as f:
            json.dump(state, f)
    except IOError:
        pass


def _generate_mock_ip():
    """Generate a mock IP address for demonstration."""
    import random
    return f"192.168.{random.randint(1, 255)}.{random.randint(1, 254)}"


def find_instance_by_name(name):
    """Find instance by name across all environments."""
    state = _load_state()
    for env_name, env_data in state.items():
        if "vms" in env_data:
            for vm_name, vm_data in env_data["vms"].items():
                if vm_name == name:
                    return env_name, vm_name, vm_data
    return None, None, None


def get_instance_details(env_name, vm_name, vm_data):
    """Get detailed instance information."""
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


def start_instance(env_name, vm_name):
    """Start an instance."""
    state = _load_state()
    if env_name in state and "vms" in state[env_name] and vm_name in state[env_name]["vms"]:
        current_status = state[env_name]["vms"][vm_name]["status"]
        if current_status != "running":
            state[env_name]["vms"][vm_name]["status"] = "running"
            _save_state(state)
            return True, current_status
    return False, None


def stop_instance(env_name, vm_name):
    """Stop an instance."""
    state = _load_state()
    if env_name in state and "vms" in state[env_name] and vm_name in state[env_name]["vms"]:
        current_status = state[env_name]["vms"][vm_name]["status"]
        if current_status != "stopped":
            state[env_name]["vms"][vm_name]["status"] = "stopped"
            _save_state(state)
            return True, current_status
    return False, None


def restart_instance(env_name, vm_name):
    """Restart an instance."""
    state = _load_state()
    if env_name in state and "vms" in state[env_name] and vm_name in state[env_name]["vms"]:
        current_status = state[env_name]["vms"][vm_name]["status"]
        state[env_name]["vms"][vm_name]["status"] = "running"
        _save_state(state)
        return True, current_status
    return False, None


def terminate_instance(env_name, vm_name):
    """Terminate (delete) an instance."""
    state = _load_state()
    if env_name in state and "vms" in state[env_name] and vm_name in state[env_name]["vms"]:
        current_status = state[env_name]["vms"][vm_name]["status"]
        del state[env_name]["vms"][vm_name]
        _save_state(state)
        return True, current_status
    return False, None


def wait_for_state(env_name, vm_name, desired_state, timeout):
    """Wait for instance to reach desired state."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        env, vm, vm_data = find_instance_by_name(vm_name)
        if not vm_data:
            if desired_state == "terminated":
                return True
            return False
        
        current_state = vm_data.get("status")
        if current_state == desired_state:
            return True
        
        time.sleep(2)
    
    return False


def main():
    """Main execution path of the module."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(
                type="str",
                default="running",
                choices=["running", "stopped", "restarted", "terminated"]
            ),
            wait=dict(type="bool", default=True),
            wait_timeout=dict(type="int", default=300),
            force=dict(type="bool", default=False),
        ),
        supports_check_mode=True,
    )

    name = module.params["name"]
    desired_state = module.params["state"]
    wait = module.params["wait"]
    wait_timeout = module.params["wait_timeout"]
    force = module.params["force"]

    start_time = time.time()

    try:
        env_name, vm_name, vm_data = find_instance_by_name(name)
        
        if not vm_data:
            module.fail_json(msg=f"Instance '{name}' not found")

        current_state = vm_data.get("status", "unknown")
        previous_state = current_state
        changed = False
        operation = "none"

        if module.check_mode:
            if desired_state == "terminated" or current_state != desired_state:
                changed = True
            result = {
                "changed": changed,
                "instance": get_instance_details(env_name, vm_name, vm_data),
                "operation": f"would_{desired_state}",
                "msg": f"Would change instance '{name}' from '{current_state}' to '{desired_state}'"
            }
            module.exit_json(**result)

        if desired_state == "running":
            if current_state in ["stopped", "hibernated"]:
                changed, previous_state = start_instance(env_name, vm_name)
                operation = "start"
            elif current_state == "running":
                operation = "already_running"
            else:
                if not force:
                    module.fail_json(
                        msg=f"Cannot start instance in state '{current_state}'. Use force=true to override."
                    )
                changed, previous_state = start_instance(env_name, vm_name)
                operation = "force_start"

        elif desired_state == "stopped":
            if current_state == "running":
                changed, previous_state = stop_instance(env_name, vm_name)
                operation = "stop"
            elif current_state == "stopped":
                operation = "already_stopped"
            else:
                if not force:
                    module.fail_json(
                        msg=f"Cannot stop instance in state '{current_state}'. Use force=true to override."
                    )
                changed, previous_state = stop_instance(env_name, vm_name)
                operation = "force_stop"

        elif desired_state == "restarted":
            changed, previous_state = restart_instance(env_name, vm_name)
            operation = "restart"
            changed = True

        elif desired_state == "terminated":
            if current_state == "terminated":
                module.fail_json(msg=f"Instance '{name}' is already terminated")
            
            if not force and current_state == "running":
                module.fail_json(
                    msg="Cannot terminate running instance without force=true. This will cause data loss."
                )
            
            changed, previous_state = terminate_instance(env_name, vm_name)
            operation = "terminate"

        if wait and changed and desired_state != "terminated":
            if not wait_for_state(env_name, vm_name, desired_state, wait_timeout):
                module.fail_json(
                    msg=f"Timeout waiting for instance '{name}' to reach state '{desired_state}'"
                )

        duration = time.time() - start_time

        env_name, vm_name, vm_data = find_instance_by_name(name)
        instance_info = {}
        if vm_data:
            instance_info = get_instance_details(env_name, vm_name, vm_data)
            if previous_state and previous_state != instance_info["state"]:
                instance_info["previous_state"] = previous_state
        elif desired_state == "terminated":
            instance_info = {
                "name": name,
                "state": "terminated",
                "previous_state": previous_state
            }

        result = {
            "changed": changed,
            "instance": instance_info,
            "operation": operation,
            "msg": f"Instance '{name}' {operation} operation completed successfully"
        }

        if wait:
            result["duration"] = round(duration, 2)

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Failed to manage instance '{name}': {str(e)}")


if __name__ == "__main__":
    main()