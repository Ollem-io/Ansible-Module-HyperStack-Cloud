# tests/units/plugins/modules/test_cloud_manager.py

from unittest.mock import MagicMock, patch
import json
import sys
import os
import importlib.util

# Load the module directly by file path
module_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "plugins", "modules", "cloud_manager.py")
)
spec = importlib.util.spec_from_file_location("cloud_manager", module_path)
cloud_manager = importlib.util.module_from_spec(spec)
sys.modules["cloud_manager"] = cloud_manager
spec.loader.exec_module(cloud_manager)


def test_module_import():
    """
    A simple smoke test to ensure the module can be imported.
    """
    assert hasattr(cloud_manager, "main")


# Helper to run the module's main() function and catch its exit
def run_module(module_args, mock_get_env):
    # Set defaults for required parameters
    if "firewall_rules" not in module_args:
        module_args["firewall_rules"] = None
    if "vms" not in module_args:
        module_args["vms"] = None

    with patch.object(cloud_manager, "get_environment", mock_get_env):
        with patch.object(cloud_manager, "create_environment") as mock_create:
            with patch.object(cloud_manager, "delete_environment") as mock_delete:
                with patch.object(cloud_manager, "create_vm") as mock_create_vm:
                    with patch.object(cloud_manager, "delete_vm") as mock_delete_vm:
                        with patch.object(cloud_manager, "start_vm") as mock_start_vm:
                            with patch.object(cloud_manager, "stop_vm") as mock_stop_vm:
                                # Mock AnsibleModule and its methods
                                mock_module = MagicMock()
                                mock_module.params = module_args
                                mock_module.check_mode = False

                                # Store exit_json args for assertion
                                exit_json_args = {}

                                def fake_exit_json(**kwargs):
                                    exit_json_args.update(kwargs)

                                mock_module.exit_json = fake_exit_json

                                # Store fail_json args for assertion
                                fail_json_args = {}

                                def fake_fail_json(**kwargs):
                                    fail_json_args.update(kwargs)

                                mock_module.fail_json = fake_fail_json

                                # Patch the AnsibleModule constructor to return our mock
                                with patch("cloud_manager.AnsibleModule", return_value=mock_module):
                                    cloud_manager.main()

                                # Return the captured result along with mocks
                                result = exit_json_args if exit_json_args else fail_json_args
                                return (
                                    result,
                                    mock_create,
                                    mock_delete,
                                    mock_create_vm,
                                    mock_delete_vm,
                                    mock_start_vm,
                                    mock_stop_vm,
                                )


def test_env_present_when_absent():
    """Test creating an environment that does not exist."""
    args = {"name": "staging", "state": "present"}
    # Simulate that the environment does not exist
    mock_get_env = MagicMock(return_value=None)

    result, mock_create, _, _, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    mock_create.assert_called_once_with("staging")


def test_env_present_when_present():
    """Test creating an environment that already exists (idempotency)."""
    args = {"name": "production", "state": "present"}
    # Simulate that the environment already exists
    mock_get_env = MagicMock(return_value={"id": "env-123"})

    result, mock_create, mock_delete, _, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is False
    mock_create.assert_not_called()
    mock_delete.assert_not_called()


def test_env_absent_when_present():
    """Test deleting an environment that exists."""
    args = {"name": "production", "state": "absent"}
    # Simulate that the environment exists
    mock_get_env = MagicMock(return_value={"id": "env-123"})

    result, _, mock_delete, _, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    mock_delete.assert_called_once_with("production")


def test_env_absent_when_absent():
    """Test deleting an environment that does not exist (idempotency)."""
    args = {"name": "staging", "state": "absent"}
    # Simulate that the environment does not exist
    mock_get_env = MagicMock(return_value=None)

    result, mock_create, mock_delete, _, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is False
    mock_create.assert_not_called()
    mock_delete.assert_not_called()


def test_firewall_rules_normalize():
    """Test the _normalize_rules helper function."""
    # Test empty list
    assert cloud_manager._normalize_rules([]) == []
    assert cloud_manager._normalize_rules(None) == []

    # Test single rule
    rules = [{"protocol": "tcp", "port": 80}]
    assert cloud_manager._normalize_rules(rules) == rules

    # Test multiple rules - should be sorted
    rules = [
        {"protocol": "udp", "port": 53},
        {"protocol": "tcp", "port": 443},
        {"protocol": "tcp", "port": 80},
    ]
    expected = [
        {"protocol": "tcp", "port": 80},
        {"protocol": "tcp", "port": 443},
        {"protocol": "udp", "port": 53},
    ]
    assert cloud_manager._normalize_rules(rules) == expected


def test_firewall_rules_no_change():
    """Test firewall rules when no change is needed."""
    existing_rules = [{"protocol": "tcp", "port": 80}]
    args = {
        "name": "web-server",
        "state": "present",
        "firewall_rules": [{"protocol": "tcp", "port": 80}],
    }

    mock_env = {"id": "env-123", "rules": existing_rules}
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, _, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is False
    assert "diff" not in result


def test_firewall_rules_change_needed():
    """Test firewall rules when change is needed."""
    existing_rules = [{"protocol": "tcp", "port": 80}]
    new_rules = [{"protocol": "tcp", "port": 443}]
    args = {"name": "web-server", "state": "present", "firewall_rules": new_rules}

    mock_env = {"id": "env-123", "rules": existing_rules}
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, _, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    assert "diff" in result
    assert "tcp:80" in result["diff"]["before"]
    assert "tcp:443" in result["diff"]["after"]


def test_firewall_rules_new_environment():
    """Test firewall rules with a new environment."""
    args = {
        "name": "new-env",
        "state": "present",
        "firewall_rules": [{"protocol": "tcp", "port": 443}],
    }

    mock_get_env = MagicMock(return_value=None)

    result, mock_create, _, _, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    mock_create.assert_called_once_with("new-env")


def test_vm_creation():
    """Test creating a VM in an existing environment."""
    args = {
        "name": "test-env",
        "state": "present",
        "vms": [
            {
                "name": "web-01",
                "size": "small",
                "image": "ubuntu-22.04",
                "state": "running",
            }
        ],
    }

    mock_env = {"id": "env-123", "vms": {}}
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, mock_create_vm, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    mock_create_vm.assert_called_once_with(
        "test-env",
        {
            "name": "web-01",
            "size": "small",
            "image": "ubuntu-22.04",
            "state": "running",
        },
    )


def test_vm_creation_invalid_image():
    """Test VM creation with invalid image (error handling)."""
    args = {
        "name": "test-env",
        "state": "present",
        "vms": [
            {
                "name": "bad-vm",
                "size": "small",
                "image": "nonexistent-image",
                "state": "running",
            }
        ],
    }

    mock_env = {"id": "env-123", "vms": {}}
    mock_get_env = MagicMock(return_value=mock_env)

    # Set up mocks manually to allow create_vm to run and raise the error
    with patch.object(cloud_manager, "get_environment", mock_get_env):
        with patch.object(cloud_manager, "create_environment") as mock_create:
            with patch.object(cloud_manager, "delete_environment") as mock_delete:
                with patch.object(cloud_manager, "delete_vm") as mock_delete_vm:
                    with patch.object(cloud_manager, "start_vm") as mock_start_vm:
                        with patch.object(cloud_manager, "stop_vm") as mock_stop_vm:
                            # Mock AnsibleModule and its methods
                            mock_module = MagicMock()
                            mock_module.params = args
                            mock_module.check_mode = False

                            # Store exit_json args for assertion
                            exit_json_args = {}

                            def fake_exit_json(**kwargs):
                                exit_json_args.update(kwargs)

                            mock_module.exit_json = fake_exit_json

                            # Store fail_json args for assertion
                            fail_json_args = {}

                            def fake_fail_json(**kwargs):
                                fail_json_args.update(kwargs)

                            mock_module.fail_json = fake_fail_json

                            # Add required parameters
                            if "firewall_rules" not in args:
                                args["firewall_rules"] = None
                            if "vms" not in args:
                                args["vms"] = None

                            # Don't mock create_vm - let it run and raise ValueError
                            with patch("cloud_manager.AnsibleModule", return_value=mock_module):
                                cloud_manager.main()

    # Should have called fail_json
    result = fail_json_args if fail_json_args else exit_json_args
    assert "msg" in result
    assert "Failed to manage VM 'bad-vm'" in result["msg"]
    assert "not found" in result["msg"]


def test_vm_state_management():
    """Test VM state transitions (start/stop)."""
    # Test starting a stopped VM
    args = {
        "name": "test-env",
        "state": "present",
        "vms": [
            {
                "name": "web-01",
                "size": "small",
                "image": "ubuntu-22.04",
                "state": "running",
            }
        ],
    }

    mock_env = {
        "id": "env-123",
        "vms": {"web-01": {"name": "web-01", "status": "stopped"}},
    }
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, _, _, mock_start_vm, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    mock_start_vm.assert_called_once_with("test-env", "web-01")


def test_vm_deletion():
    """Test deleting a VM."""
    args = {
        "name": "test-env",
        "state": "present",
        "vms": [
            {
                "name": "web-01",
                "size": "small",
                "image": "ubuntu-22.04",
                "state": "absent",
            }
        ],
    }

    mock_env = {
        "id": "env-123",
        "vms": {"web-01": {"name": "web-01", "status": "running"}},
    }
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, _, mock_delete_vm, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    mock_delete_vm.assert_called_once_with("test-env", "web-01")


# Additional tests to increase coverage
def test_check_mode():
    """Test check mode functionality."""
    args = {"name": "staging", "state": "present", "firewall_rules": None, "vms": None}
    mock_get_env = MagicMock(return_value=None)

    # Set up mocks with check mode enabled
    with patch.object(cloud_manager, "get_environment", mock_get_env):
        with patch.object(cloud_manager, "create_environment") as mock_create:
            mock_module = MagicMock()
            mock_module.params = args
            mock_module.check_mode = True

            exit_json_args = {}

            def fake_exit_json(**kwargs):
                exit_json_args.update(kwargs)

            mock_module.exit_json = fake_exit_json

            with patch("cloud_manager.AnsibleModule", return_value=mock_module):
                cloud_manager.main()

    assert exit_json_args["changed"] is True
    mock_create.assert_not_called()  # Should not create in check mode


def test_vm_state_stopped():
    """Test stopping a running VM."""
    args = {
        "name": "test-env",
        "state": "present",
        "vms": [
            {
                "name": "web-01",
                "size": "small",
                "image": "ubuntu-22.04",
                "state": "stopped",
            }
        ],
    }

    mock_env = {
        "id": "env-123",
        "vms": {"web-01": {"name": "web-01", "status": "running"}},
    }
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, _, _, _, mock_stop_vm = run_module(args, mock_get_env)

    assert result["changed"] is True
    mock_stop_vm.assert_called_once_with("test-env", "web-01")


def test_vm_already_correct_state():
    """Test VM already in correct state (idempotency)."""
    args = {
        "name": "test-env",
        "state": "present",
        "vms": [
            {
                "name": "web-01",
                "size": "small",
                "image": "ubuntu-22.04",
                "state": "running",
            }
        ],
    }

    mock_env = {
        "id": "env-123",
        "vms": {"web-01": {"name": "web-01", "status": "running"}},
    }
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, _, _, mock_start_vm, mock_stop_vm = run_module(args, mock_get_env)

    assert result["changed"] is False
    mock_start_vm.assert_not_called()
    mock_stop_vm.assert_not_called()


def test_format_rules_for_display():
    """Test the format_rules_for_display helper function."""
    rules = [{"protocol": "tcp", "port": 80}, {"protocol": "udp", "port": 53}]
    expected = "tcp:80, udp:53"
    assert cloud_manager.format_rules_for_display(rules) == expected

    # Test empty rules
    assert cloud_manager.format_rules_for_display([]) == ""
    assert cloud_manager.format_rules_for_display(None) == ""


def test_multiple_vms():
    """Test managing multiple VMs in one environment."""
    args = {
        "name": "test-env",
        "state": "present",
        "vms": [
            {
                "name": "web-01",
                "size": "small",
                "image": "ubuntu-22.04",
                "state": "running",
            },
            {
                "name": "web-02",
                "size": "medium",
                "image": "ubuntu-22.04",
                "state": "running",
            },
        ],
    }

    mock_env = {"id": "env-123", "vms": {}}
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, mock_create_vm, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    # Should create two VMs
    assert mock_create_vm.call_count == 2


def test_environment_with_existing_firewall_rules():
    """Test environment management with existing firewall rules."""
    args = {
        "name": "test-env",
        "state": "present",
        "firewall_rules": [{"protocol": "tcp", "port": 443}],
    }

    mock_env = {"id": "env-123", "rules": [{"protocol": "tcp", "port": 80}], "vms": {}}
    mock_get_env = MagicMock(return_value=mock_env)

    result, _, _, _, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    assert "diff" in result


def test_vm_creation_in_new_environment():
    """Test creating VMs when environment doesn't exist."""
    args = {
        "name": "new-env",
        "state": "present",
        "vms": [
            {
                "name": "web-01",
                "size": "small",
                "image": "ubuntu-22.04",
                "state": "running",
            }
        ],
    }

    mock_get_env = MagicMock(return_value=None)

    result, mock_create, _, mock_create_vm, _, _, _ = run_module(args, mock_get_env)

    assert result["changed"] is True
    mock_create.assert_called_once_with("new-env")
    mock_create_vm.assert_called_once()
