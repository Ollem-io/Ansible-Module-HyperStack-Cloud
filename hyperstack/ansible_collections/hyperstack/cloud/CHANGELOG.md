# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-06-25

### Added
- **New Module: `instance_info`** - Query VM instances by name, IP address, or environment (#3)
  - Find instances across multiple environments
  - Filter by instance states (running, stopped, hibernated, pending, terminated)
  - Returns comprehensive instance details including network configuration
  - Support for IP-based instance discovery
- **New Module: `instance`** - Direct VM instance lifecycle management (#3)
  - Start, stop, restart, and terminate individual instances
  - Hibernated instance revival for dynamic scaling
  - Force operations with safety overrides
  - Configurable wait timeouts and check mode support
- **Enhanced Response Data** - `cloud_manager` module now returns detailed VM information
  - VM details include public/private IPs, creation timestamps, and current status
  - Backward compatible - existing playbooks continue to work unchanged

### Enhanced
- **Dynamic Infrastructure Automation** - Enable automated hibernated instance discovery and revival
  - Query hibernated instances across environments
  - Start instances on-demand for deployment workflows
  - Get instance connection details for validation
- **Improved Error Handling** - Enhanced error messages and validation
- **Comprehensive Testing** - Added unit and integration tests for new modules
- **Documentation Updates** - Updated README with new module capabilities and usage examples

### Technical Improvements
- Mock implementation extended to support instance-level operations
- Enhanced state management with IP address tracking
- Improved test coverage for instance management scenarios
- Added comprehensive examples for dynamic infrastructure workflows

### Breaking Changes
- None - all changes are backward compatible

### Migration Notes
- Existing `cloud_manager` usage remains unchanged
- New `vms` field in `cloud_manager` responses provides additional VM details
- New modules (`instance_info`, `instance`) are additive and don't affect existing functionality

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

[Unreleased]: https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/compare/v0.1.0...v0.3.0
[0.1.0]: https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/releases/tag/v0.1.0