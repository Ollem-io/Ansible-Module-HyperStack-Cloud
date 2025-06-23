"""
Pytest configuration for hyperstack.cloud collection tests.
"""

import os
import sys

import pytest

# Add the plugins directory to the path so we can import modules
plugins_path = os.path.join(os.path.dirname(__file__), "..", "plugins")
sys.path.insert(0, plugins_path)


@pytest.fixture
def mock_ansible_module():
    """Mock AnsibleModule for testing."""

    class MockAnsibleModule:
        def __init__(self, argument_spec, supports_check_mode=False):
            self.params = {}
            self.check_mode = False
            self.argument_spec = argument_spec
            self.supports_check_mode = supports_check_mode
            self._exit_args = None
            self._fail_args = None

        def exit_json(self, **kwargs):
            self._exit_args = kwargs

        def fail_json(self, **kwargs):
            self._fail_args = kwargs

        def set_params(self, params):
            self.params = params

    return MockAnsibleModule


@pytest.fixture
def sample_environment_data():
    """Sample environment data for testing."""
    return {
        "name": "test-environment",
        "state": "present",
        "description": "Test environment for unit tests",
    }


@pytest.fixture
def sample_vm_data():
    """Sample VM data for testing."""
    return [
        {
            "name": "web-server",
            "size": "medium",
            "image": "ubuntu-20.04",
            "state": "running",
        },
        {
            "name": "database",
            "size": "large",
            "image": "postgres-13",
            "state": "running",
        },
    ]


@pytest.fixture
def sample_full_params(sample_environment_data, sample_vm_data):
    """Complete parameter set for testing."""
    params = sample_environment_data.copy()
    params["vms"] = sample_vm_data
    return params
