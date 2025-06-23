# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-06-23

### Added
- Initial release of Hyperstack Cloud Ansible Collection
- `cloud_manager` module for managing Hyperstack Cloud resources
- Support for environment management (create, list, delete)
- Support for virtual machine management (create, list, delete, start, stop, restart)
- Support for firewall rule management
- Comprehensive error handling and input validation
- Unit tests for all core functionality
- Integration tests for environment and VM operations
- Documentation and code style guidelines

### Features
- **Environment Management**: Create, list, and delete cloud environments
- **Virtual Machine Operations**: Full lifecycle management of VMs including creation, power operations, and deletion
- **Firewall Rules**: Create and manage firewall rules for network security
- **Idempotency**: All operations support Ansible's idempotent behavior
- **Check Mode**: Support for dry-run operations without making actual changes
- **Comprehensive Logging**: Detailed logging for troubleshooting and monitoring

### Technical Details
- Python 3.8+ compatibility
- Ansible 2.9+ compatibility
- RESTful API integration with Hyperstack Cloud
- Secure credential management
- Input validation and sanitization
- Error handling with meaningful messages

[Unreleased]: https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/releases/tag/v0.1.0