# Hyperstack Cloud Ansible Collection

[![CI](https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/workflows/CI/badge.svg)](https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/actions)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-hyperstack.cloud-660198.svg)](https://galaxy.ansible.com/hyperstack/cloud)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Ansible](https://img.shields.io/badge/ansible-2.14%2B-red.svg)](https://www.ansible.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-ready Ansible collection for managing [Hyperstack Cloud](https://hyperstack.cloud) infrastructure as code. This collection provides idempotent modules for provisioning and managing cloud resources with comprehensive error handling and testing.

## 🚀 Features

### Core Capabilities
- **🌐 Environment Management**: Create, update, and delete cloud environments with atomic operations
- **🖥️ Virtual Machine Orchestration**: Full lifecycle management of VMs with state tracking
- **🔒 Network Security**: Firewall rule management with declarative configuration
- **🔄 Idempotent Operations**: Safe to run multiple times with predictable outcomes
- **✅ Check Mode Support**: Preview changes before applying them
- **📊 Detailed Change Tracking**: Comprehensive diff output for all modifications

### Enterprise Features
- **🛡️ Robust Error Handling**: Graceful failure recovery with detailed error messages
- **📝 Extensive Logging**: Structured logging for debugging and auditing
- **🔍 Input Validation**: Comprehensive parameter validation with helpful error messages
- **🏗️ Modular Architecture**: Clean, maintainable code following Ansible best practices
- **📚 Rich Documentation**: Detailed module documentation with extensive examples
- **🧪 Comprehensive Testing**: Unit, integration, and end-to-end test coverage

## 📋 Requirements

### System Requirements
- Python 3.9 or higher
- Ansible Core 2.14.0 or higher
- Linux, macOS, or Windows (WSL)

### Python Dependencies
- `ansible-core >= 2.14.0`
- `ansible.posix >= 1.0.0` (collection dependency)

### Hyperstack Cloud Requirements
- Valid Hyperstack Cloud account
- API credentials configured
- Network connectivity to Hyperstack Cloud API endpoints

## 🔧 Installation

### From Ansible Galaxy (Recommended)

```bash
ansible-galaxy collection install dsmello.cloud
```

### From Source

```bash
# Clone the repository
git clone https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud.git
cd hyperstack-cloud-ansible

# Build the collection
cd hyperstack/ansible_collections/hyperstack/cloud
ansible-galaxy collection build --force

# Install the built collection
ansible-galaxy collection install dsmello-cloud-*.tar.gz --force
```

### Development Installation

```bash
# Clone and setup development environment
git clone https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud.git
cd hyperstack-cloud-ansible

# Install with uv (recommended)
uv sync --all-extras
source .venv/bin/activate

# Or use make
make install
```

## 🎯 Quick Start

### Basic Usage

```yaml
---
- name: Hyperstack Cloud Infrastructure
  hosts: localhost
  gather_facts: false
  collections:
    - hyperstack.cloud
  
  tasks:
    - name: Create production environment
      cloud_manager:
        name: production
        state: present
        description: "Production environment"
```

### Advanced Example

```yaml
---
- name: Deploy Complete Application Stack
  hosts: localhost
  gather_facts: false
  collections:
    - hyperstack.cloud
  
  vars:
    environment_name: "app-production"
    
  tasks:
    - name: Create environment with full stack
      cloud_manager:
        name: "{{ environment_name }}"
        state: present
        description: "Production application stack"
        firewall_rules:
          - protocol: tcp
            port: 80
          - protocol: tcp
            port: 443
          - protocol: tcp
            port: 22
        vms:
          - name: "{{ environment_name }}-lb"
            size: medium
            image: nginx-alpine
            state: running
          - name: "{{ environment_name }}-app-1"
            size: large
            image: ubuntu-22.04
            state: running
          - name: "{{ environment_name }}-app-2"
            size: large
            image: ubuntu-22.04
            state: running
          - name: "{{ environment_name }}-db-primary"
            size: xlarge
            image: postgres-15
            state: running
          - name: "{{ environment_name }}-db-replica"
            size: xlarge
            image: postgres-15
            state: running
      register: deployment_result
    
    - name: Display deployment information
      debug:
        var: deployment_result
```

## 📚 Module Reference

### cloud_manager

The primary module for managing Hyperstack Cloud resources.

#### Synopsis

Manages Hyperstack Cloud environments, virtual machines, and network configurations with comprehensive error handling and idempotent operations.

#### Parameters

| Parameter | Required | Default | Type | Description |
|-----------|----------|---------|------|-------------|
| `name` | **yes** | - | str | Name of the environment to manage |
| `state` | no | `present` | str | Desired state of the environment (`present`/`absent`) |
| `description` | no | - | str | Human-readable description of the environment |
| `firewall_rules` | no | `[]` | list | List of firewall rules to apply |
| `vms` | no | `[]` | list | List of virtual machines to manage |

#### Firewall Rule Options

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `protocol` | **yes** | str | Network protocol (`tcp`/`udp`) |
| `port` | **yes** | int | Port number (1-65535) |

#### VM Options

| Parameter | Required | Default | Type | Description |
|-----------|----------|---------|------|-------------|
| `name` | **yes** | - | str | Name of the virtual machine |
| `size` | **yes** | - | str | VM size (`small`/`medium`/`large`/`xlarge`) |
| `image` | **yes** | - | str | Operating system image |
| `state` | no | `running` | str | Desired VM state (`present`/`running`/`stopped`/`absent`) |

#### Return Values

| Key | Type | Always | Description |
|-----|------|--------|-------------|
| `changed` | bool | yes | Whether any changes were made |
| `msg` | str | yes | Human-readable status message |
| `name` | str | yes | Name of the managed environment |
| `state` | str | yes | Current state of the environment |
| `diff` | dict | when changed | Details of changes made |
| `failed` | bool | on failure | Indicates if the operation failed |

## 🔍 Supported Features

### ✅ Currently Implemented

- **Environment Management**
  - Create/delete environments
  - Update environment metadata
  - Atomic operations with rollback on failure

- **Virtual Machine Management**
  - Deploy VMs with specified configurations
  - Start/stop/restart operations
  - Resize and reconfigure VMs
  - Bulk operations with parallel processing

- **Network Security**
  - Declarative firewall rule management
  - Automatic rule reconciliation
  - Security group management

- **Error Handling**
  - Graceful error recovery
  - Detailed error messages
  - Retry logic for transient failures

### 🚧 Roadmap

- **Storage Management**
  - Volume creation and attachment
  - Snapshot management
  - Backup automation

- **Advanced Networking**
  - VPC management
  - Load balancer configuration
  - DNS management

- **Monitoring & Observability**
  - Metrics collection
  - Alert configuration
  - Log aggregation

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit        # Unit tests only
make test-integration # Integration tests only
make test-sanity     # Ansible sanity tests

# Run with coverage
make test-coverage
```

### Test Structure

```
tests/
├── unit/                 # Unit tests for modules
│   └── plugins/
│       └── modules/
│           └── test_cloud_manager.py
├── integration/          # Integration tests
│   └── targets/
│       ├── cloud_manager_env/
│       ├── cloud_manager_firewall/
│       └── cloud_manager_vm_failure/
└── sanity/              # Ansible sanity tests
```

## 🛠️ Development

### Development Setup

```bash
# Clone repository
git clone https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud.git
cd hyperstack-cloud-ansible

# Setup development environment
make dev-setup

# Run linting
make lint

# Format code
make format

# Run security scan
make security
```

### Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) with 120-character line limit
- Use [Black](https://black.readthedocs.io/) for code formatting
- Type hints for all function signatures
- Comprehensive docstrings for all public functions
- See `docs/code-style-and-guide.md` for detailed guidelines

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code style guide
4. Add/update tests for your changes
5. Run the full test suite
6. Commit with descriptive messages
7. Push to your fork
8. Open a Pull Request

### Commit Message Format

```
type(scope): brief description

- Detailed explanation of changes
- Additional context if needed

Author: Your Name <your.email@example.com>

AI Assistant:
- Claude Code
```

## 📖 Documentation

- [Code Style Guide](hyperstack/ansible_collections/hyperstack/cloud/docs/code-style-and-guide.md)
- [API Documentation](https://hyperstack-cloud-ansible.readthedocs.io)
- [Module Examples](hyperstack/ansible_collections/hyperstack/cloud/plugins/modules/)
- [Integration Guide](docs/integration-guide.md)

## 🤝 Support

### Getting Help

- 📧 Email: [davi@ollem.io](mailto:davi@ollem.io)
- 🐛 Issues: [GitHub Issues](https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/discussions)
- 📚 Documentation: [Read the Docs](https://hyperstack-cloud-ansible.readthedocs.io)

### Reporting Issues

When reporting issues, please include:
- Ansible version (`ansible --version`)
- Python version (`python --version`)
- Collection version
- Minimal reproducible example
- Error messages and logs

## 📜 License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- [Hyperstack Cloud](https://hyperstack.cloud) for providing the cloud infrastructure
- [Ansible](https://www.ansible.com/) community for the automation framework
- All contributors who have helped improve this collection

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Ollem-io/Ansible-Module-HyperStack-Cloud&type=Date)](https://star-history.com/#Ollem-io/Ansible-Module-HyperStack-Cloud&Date)

---

**Made with ❤️ by [Davi Mello](https://github.com/dsmello)**