# Code Style and Development Guide

## Overview

This document outlines the coding standards, best practices, and development guidelines for the Hyperstack Cloud Ansible Collection. Following these guidelines ensures consistency, maintainability, and professional quality across all collection components.

## Python Code Style

### General Guidelines

- Follow PEP 8 Python style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 120 characters
- Use meaningful variable and function names
- Add docstrings to all modules, classes, and functions

### Imports

```python
# Standard library imports first
import os
import sys
from collections import defaultdict

# Third-party imports
import requests
from ansible.module_utils.basic import AnsibleModule

# Local imports last
from ansible_collections.hyperstack.cloud.plugins.module_utils.common import HyperstackAPI
```

### Module Structure

All Ansible modules must follow this structure:

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Author Name <email@domain.com>
# GNU General Public License v3.0+

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: module_name
short_description: Brief description
version_added: "1.0.0"
description:
    - Detailed description of what the module does
    - Multiple lines if needed
options:
    parameter_name:
        description:
            - Description of the parameter
        required: true/false
        type: str/int/bool/list/dict
        choices: [option1, option2]
        default: default_value
author:
    - Author Name (@github_handle)
'''

EXAMPLES = r'''
- name: Example usage
  hyperstack.cloud.module_name:
    parameter: value
    
- name: Another example
  hyperstack.cloud.module_name:
    parameter: different_value
    state: present
'''

RETURN = r'''
result:
    description: Description of return value
    type: dict
    returned: always
    sample: {
        "key": "value"
    }
'''

from ansible.module_utils.basic import AnsibleModule

def main():
    """Main execution function."""
    module = AnsibleModule(
        argument_spec=dict(
            # Define parameters here
        ),
        supports_check_mode=True
    )
    
    # Module logic here
    
    module.exit_json(changed=False, result={})

if __name__ == '__main__':
    main()
```

## Documentation Standards

### Module Documentation

- **DOCUMENTATION**: YAML format describing the module
- **EXAMPLES**: Real-world usage examples
- **RETURN**: Document all return values with types and descriptions
- Use consistent formatting and proper indentation

### Code Comments

```python
# Single-line comments for brief explanations
def process_data(data):
    """
    Multi-line docstring for functions.
    
    Args:
        data (dict): Input data to process
        
    Returns:
        dict: Processed data with additional fields
        
    Raises:
        ValueError: If data is invalid
    """
    # Process the data here
    return processed_data
```

## Testing Standards

### Unit Tests

- Place tests in `tests/unit/plugins/modules/`
- Use pytest framework
- Test file naming: `test_<module_name>.py`
- Mock external API calls

```python
import pytest
from unittest.mock import patch, MagicMock

def test_module_import():
    """Test that module can be imported."""
    import ansible_collections.hyperstack.cloud.plugins.modules.module_name as module
    assert hasattr(module, 'main')

@patch('requests.get')
def test_api_call(mock_get):
    """Test API interaction."""
    mock_get.return_value.json.return_value = {'status': 'success'}
    # Test logic here
```

### Integration Tests

- Place in `tests/integration/targets/`
- Use Ansible playbook format
- Test real-world scenarios

## Error Handling

### Standard Error Patterns

```python
try:
    # Risky operation
    result = api_call()
except requests.exceptions.RequestException as e:
    module.fail_json(msg=f"API request failed: {str(e)}")
except Exception as e:
    module.fail_json(msg=f"Unexpected error: {str(e)}")
```

### Validation

```python
def validate_parameters(module):
    """Validate module parameters."""
    if not module.params.get('required_param'):
        module.fail_json(msg="required_param is mandatory")
    
    if module.params.get('choice_param') not in ['option1', 'option2']:
        module.fail_json(msg="Invalid choice for choice_param")
```

## Git Workflow

### Commit Message Format

```
type(scope): brief description (max 120 chars)

details:
- Detailed explanation of changes
- Multiple bullet points if needed
- Reference to issues or PRs

Author: Full Name <email@domain.com>

AI Assistant:
- Claude Code
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or modifying tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

### Branch Naming

- `feature/<feature-name>`
- `fix/<bug-description>`
- `docs/<documentation-update>`

## API Integration Patterns

### HTTP Client Setup

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_http_session():
    """Create HTTP session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
```

### API Response Handling

```python
def handle_api_response(response, module):
    """Handle API response consistently."""
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return None  # Resource not found
        elif response.status_code == 401:
            module.fail_json(msg="Authentication failed")
        else:
            module.fail_json(msg=f"API error: {e}")
    except ValueError:
        module.fail_json(msg="Invalid JSON response from API")
```

## Security Guidelines

### Sensitive Data Handling

- Never log sensitive information (passwords, tokens, keys)
- Use `no_log=True` for sensitive parameters
- Sanitize error messages

```python
argument_spec = dict(
    api_token=dict(type='str', required=True, no_log=True),
    password=dict(type='str', no_log=True)
)
```

### Input Validation

- Validate all user inputs
- Sanitize data before API calls
- Use parameterized queries

## Performance Guidelines

### Efficient Operations

- Use bulk operations when available
- Implement proper pagination
- Cache expensive operations
- Use connection pooling

### Resource Management

```python
def cleanup_resources():
    """Clean up resources properly."""
    try:
        # Cleanup code
        pass
    except Exception:
        # Log cleanup errors but don't fail
        pass
```

## Ansible-Specific Guidelines

### Check Mode Support

```python
if module.check_mode:
    # Return what would be changed without making changes
    module.exit_json(changed=True, msg="Would create resource")
```

### Idempotency

- Ensure operations are idempotent
- Check current state before making changes
- Return appropriate `changed` status

```python
current_state = get_current_state()
desired_state = get_desired_state()

if current_state == desired_state:
    module.exit_json(changed=False, msg="No changes needed")
else:
    apply_changes()
    module.exit_json(changed=True, msg="Resource updated")
```

## File Organization

```
plugins/
├── modules/
│   ├── __init__.py
│   ├── environment.py
│   ├── firewall.py
│   └── virtual_machine.py
├── module_utils/
│   ├── __init__.py
│   ├── common.py
│   └── api_client.py
└── README.md

tests/
├── unit/
│   └── plugins/
│       ├── modules/
│       └── module_utils/
└── integration/
    └── targets/
```

## Code Review Checklist

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is complete and accurate
- [ ] No sensitive data exposed
- [ ] Error handling is comprehensive
- [ ] Code is idempotent
- [ ] Check mode is supported

### Review Criteria

- Code quality and readability
- Test coverage
- Documentation completeness
- Security considerations
- Performance implications
- Ansible best practices compliance

## Tools and Automation

### Recommended Tools

- **Linting**: `flake8`, `pylint`
- **Formatting**: `black`
- **Testing**: `pytest`, `ansible-test`
- **Documentation**: `sphinx`

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## Continuous Integration

### Test Matrix

- Multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
- Multiple Ansible versions
- Unit and integration tests
- Linting and style checks

This guide ensures consistent, maintainable, and high-quality code across the Hyperstack Cloud Ansible Collection. Regular updates to this document reflect evolving best practices and project requirements.