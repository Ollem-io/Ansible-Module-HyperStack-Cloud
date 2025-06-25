# Ansible Collection - hyperstack.cloud

[![CI](https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/workflows/CI/badge.svg)](https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/actions)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-hyperstack.cloud-660198.svg)](https://galaxy.ansible.com/hyperstack/cloud)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

An Ansible collection for managing Hyperstack Cloud resources including environments, virtual machines, and network configurations.

## Description

The `hyperstack.cloud` collection provides comprehensive automation capabilities for Hyperstack Cloud infrastructure. It enables you to:

- Manage cloud environments and their lifecycle
- Deploy and configure virtual machines
- Handle complex object relationships with robust error handling
- Implement firewall rules and network security
- Automate infrastructure provisioning and deprovisioning

## Installation

### From Ansible Galaxy

```bash
ansible-galaxy collection install hyperstack.cloud
```

### From Source

```bash
git clone https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud.git
cd hyperstack-cloud-ansible
ansible-galaxy collection build hyperstack/ansible_collections/hyperstack/cloud --force
ansible-galaxy collection install hyperstack-cloud-*.tar.gz --force
```

## Quick Start

```yaml
---
- name: Manage Hyperstack Cloud Resources
  hosts: localhost
  gather_facts: false
  collections:
    - hyperstack.cloud
  
  tasks:
    - name: Create development environment
      cloud_manager:
        name: "dev-environment"
        state: present
        description: "Development environment for testing"
        
    - name: Deploy virtual machines
      cloud_manager:
        name: "dev-environment"
        state: present
        vms:
          - name: "web-server"
            size: "medium"
            image: "ubuntu-20.04"
            state: "running"
          - name: "database"
            size: "large"
            image: "ubuntu-20.04"
            state: "running"
```

## Modules

### cloud_manager

The main module for managing Hyperstack Cloud resources with support for:

- **Environment Management**: Create, update, and delete cloud environments
- **Virtual Machine Operations**: Deploy, start, stop, and remove VMs
- **Complex Object Handling**: Manage lists of VMs with comprehensive validation
- **Error Handling**: Robust error reporting and recovery mechanisms
- **Idempotent Operations**: Safe to run multiple times with consistent results
- **Enhanced Responses**: Returns detailed VM information including IPs and status

### instance_info

A specialized module for querying VM instance information:

- **Instance Discovery**: Find instances by name, IP address, or environment
- **State Filtering**: Query instances by their current state (running, stopped, hibernated)
- **Detailed Information**: Returns comprehensive instance details including network configuration
- **Multi-Environment Support**: Query across multiple environments or focus on specific ones

### instance

A direct instance management module for individual VM control:

- **Lifecycle Management**: Start, stop, restart, and terminate individual instances
- **Hibernated Instance Revival**: Wake up hibernated instances for dynamic scaling
- **Force Operations**: Override safety checks for emergency operations
- **Wait Control**: Configurable waiting for operation completion
- **Check Mode Support**: Preview changes before applying them

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | - | Name of the environment |
| `state` | str | no | present | Desired state (present/absent) |
| `description` | str | no | - | Environment description |
| `vms` | list | no | [] | List of virtual machines to manage |

#### VM Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | str | yes | - | VM name |
| `size` | str | yes | - | VM size (small/medium/large) |
| `image` | str | yes | - | OS image |
| `state` | str | no | running | VM state (present/running/stopped/absent) |

## Examples

### Basic Environment Management

```yaml
- name: Create simple environment
  hyperstack.cloud.cloud_manager:
    name: "production"
    state: present
    description: "Production environment"
```

### Complex VM Deployment

```yaml
- name: Deploy multi-tier application
  hyperstack.cloud.cloud_manager:
    name: "app-stack"
    state: present
    vms:
      - name: "load-balancer"
        size: "small"
        image: "nginx-alpine"
        state: "running"
      - name: "app-server-1"
        size: "medium"
        image: "ubuntu-20.04"
        state: "running"
      - name: "app-server-2"
        size: "medium"
        image: "ubuntu-20.04"
        state: "running"
      - name: "database"
        size: "large"
        image: "postgres-13"
        state: "running"
```

### Instance Discovery and Management

```yaml
- name: Dynamic hibernated instance revival
  block:
    - name: Find hibernated instances
      hyperstack.cloud.instance_info:
        instance_states: ["hibernated"]
      register: hibernated_vms

    - name: Start hibernated instances for deployment
      hyperstack.cloud.instance:
        name: "{{ item.name }}"
        state: running
        wait: true
        wait_timeout: 300
      loop: "{{ hibernated_vms.instances }}"
      when: hibernated_vms.count > 0

    - name: Get instance details by IP
      hyperstack.cloud.instance_info:
        ip_address: "192.168.1.100"
      register: instance_by_ip

    - name: Query all instances in production environment
      hyperstack.cloud.instance_info:
        environment: "production"
        instance_states: ["running", "stopped"]
      register: prod_instances
```

### Enhanced Response Information

```yaml
- name: Deploy VMs and get detailed information
  hyperstack.cloud.cloud_manager:
    name: "web-tier"
    state: present
    vms:
      - name: "web-01"
        size: "medium"
        image: "ubuntu-22.04"
        state: "running"
  register: deployment_result

- name: Display VM network information
  debug:
    msg: |
      VM {{ item.name }} is {{ item.state }}
      Public IP: {{ item.public_ip }}
      Private IP: {{ item.private_ip }}
      Created: {{ item.created_at }}
  loop: "{{ deployment_result.vms }}"
```

### Error Handling Example

```yaml
- name: Deploy with error handling
  block:
    - name: Create environment with VMs
      hyperstack.cloud.cloud_manager:
        name: "test-env"
        state: present
        vms:
          - name: "test-vm"
            size: "small"
            image: "ubuntu-20.04"
            state: "running"
  rescue:
    - name: Handle deployment errors
      debug:
        msg: "Deployment failed: {{ ansible_failed_result.msg }}"
```

## Testing

The collection includes comprehensive test coverage:

```bash
# Run unit tests
cd hyperstack/ansible_collections/hyperstack/cloud
python -m pytest tests/unit/

# Run integration tests
ansible-test integration --python 3.11

# Run sanity tests
ansible-test sanity --python 3.11
```

## Development

### Prerequisites

- Python 3.9+
- ansible-core >= 2.14.0
- uv (for dependency management)

### Setup Development Environment

```bash
git clone https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud.git
cd hyperstack-cloud-ansible
uv sync --all-extras
source .venv/bin/activate
```

### Code Style

This project follows PEP 8 with 120-character line limits. Use the included development tools:

```bash
# Format code
black hyperstack/

# Lint code
pylint hyperstack/
flake8 hyperstack/

# Type checking
mypy hyperstack/

# Security scanning
bandit -r hyperstack/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the code style guide
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Requirements

- **ansible-core**: >= 2.14.0
- **Python**: >= 3.9
- **Dependencies**: ansible.posix >= 1.0.0

## Supported Platforms

- Linux (all distributions)
- macOS
- Windows (with WSL)

## License

GNU General Public License v3.0 or later

See [LICENSE](LICENSE) for the full license text.

## Author

**Davi Mello** - [davi@ollem.io](mailto:davi@ollem.io)

## Links

- **GitHub Repository**: https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud
- **Documentation**: https://hyperstack-cloud-ansible.readthedocs.io
- **Issue Tracker**: https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/issues
- **Ansible Galaxy**: https://galaxy.ansible.com/hyperstack/cloud
