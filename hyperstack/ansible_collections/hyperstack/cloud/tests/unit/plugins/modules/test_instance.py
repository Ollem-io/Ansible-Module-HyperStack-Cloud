#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from ansible.module_utils.basic import AnsibleModule

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../plugins/modules'))
import instance


class TestInstanceModule:
    """Test cases for the instance module."""

    @pytest.fixture
    def mock_state(self):
        """Mock state data for testing."""
        return {
            "production": {
                "id": "env-prod",
                "status": "active",
                "vms": {
                    "web-01": {
                        "name": "web-01",
                        "size": "small",
                        "image": "ubuntu-22.04",
                        "status": "running",
                        "public_ip": "192.168.1.100",
                        "private_ip": "10.0.1.100",
                        "created_at": "2024-01-01T00:00:00Z"
                    },
                    "hibernated-vm": {
                        "name": "hibernated-vm",
                        "size": "medium",
                        "image": "ubuntu-22.04",
                        "status": "hibernated",
                        "public_ip": "192.168.1.102",
                        "private_ip": "10.0.1.102",
                        "created_at": "2024-01-01T02:00:00Z"
                    }
                }
            }
        }

    @patch('instance._load_state')
    def test_find_instance_by_name_found(self, mock_load_state, mock_state):
        """Test finding an instance by name."""
        mock_load_state.return_value = mock_state
        
        env_name, vm_name, vm_data = instance.find_instance_by_name("web-01")
        
        assert env_name == "production"
        assert vm_name == "web-01"
        assert vm_data["status"] == "running"

    @patch('instance._load_state')
    def test_find_instance_by_name_not_found(self, mock_load_state, mock_state):
        """Test searching for non-existent instance."""
        mock_load_state.return_value = mock_state
        
        env_name, vm_name, vm_data = instance.find_instance_by_name("non-existent")
        
        assert env_name is None
        assert vm_name is None
        assert vm_data is None

    @patch('instance._load_state')
    @patch('instance._save_state')
    def test_start_instance(self, mock_save_state, mock_load_state, mock_state):
        """Test starting a stopped/hibernated instance."""
        mock_state["production"]["vms"]["hibernated-vm"]["status"] = "hibernated"
        mock_load_state.return_value = mock_state
        
        changed, previous_state = instance.start_instance("production", "hibernated-vm")
        
        assert changed is True
        assert previous_state == "hibernated"
        mock_save_state.assert_called_once()

    @patch('instance._load_state')
    @patch('instance._save_state')
    def test_start_already_running_instance(self, mock_save_state, mock_load_state, mock_state):
        """Test starting an already running instance."""
        mock_load_state.return_value = mock_state
        
        changed, previous_state = instance.start_instance("production", "web-01")
        
        assert changed is False
        assert previous_state is None
        mock_save_state.assert_not_called()

    @patch('instance._load_state')
    @patch('instance._save_state')
    def test_stop_instance(self, mock_save_state, mock_load_state, mock_state):
        """Test stopping a running instance."""
        mock_load_state.return_value = mock_state
        
        changed, previous_state = instance.stop_instance("production", "web-01")
        
        assert changed is True
        assert previous_state == "running"
        mock_save_state.assert_called_once()

    @patch('instance._load_state')
    @patch('instance._save_state')
    def test_restart_instance(self, mock_save_state, mock_load_state, mock_state):
        """Test restarting an instance."""
        mock_load_state.return_value = mock_state
        
        changed, previous_state = instance.restart_instance("production", "web-01")
        
        assert changed is True
        assert previous_state == "running"
        mock_save_state.assert_called_once()

    @patch('instance._load_state')
    @patch('instance._save_state')
    def test_terminate_instance(self, mock_save_state, mock_load_state, mock_state):
        """Test terminating an instance."""
        mock_load_state.return_value = mock_state
        
        changed, previous_state = instance.terminate_instance("production", "web-01")
        
        assert changed is True
        assert previous_state == "running"
        mock_save_state.assert_called_once()

    @patch('instance.find_instance_by_name')
    @patch('instance.time.sleep')
    def test_wait_for_state_success(self, mock_sleep, mock_find_instance):
        """Test waiting for state change successfully."""
        mock_find_instance.side_effect = [
            ("production", "web-01", {"status": "starting"}),
            ("production", "web-01", {"status": "running"})
        ]
        
        result = instance.wait_for_state("production", "web-01", "running", 60)
        
        assert result is True

    @patch('instance.find_instance_by_name')
    @patch('instance.time.sleep')
    def test_wait_for_state_timeout(self, mock_sleep, mock_find_instance):
        """Test waiting for state change with timeout."""
        mock_find_instance.return_value = ("production", "web-01", {"status": "starting"})
        
        with patch('instance.time.time', side_effect=[0, 30, 60, 90]):
            result = instance.wait_for_state("production", "web-01", "running", 60)
        
        assert result is False

    @patch('instance.find_instance_by_name')
    def test_wait_for_terminated_state(self, mock_find_instance):
        """Test waiting for terminated state."""
        mock_find_instance.return_value = (None, None, None)
        
        result = instance.wait_for_state("production", "web-01", "terminated", 60)
        
        assert result is True

    def test_get_instance_details(self):
        """Test generating instance details."""
        vm_data = {
            "name": "test-vm",
            "status": "running",
            "size": "small",
            "image": "ubuntu-22.04",
            "public_ip": "192.168.1.100",
            "private_ip": "10.0.1.100",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        result = instance.get_instance_details("production", "test-vm", vm_data)
        
        assert result["name"] == "test-vm"
        assert result["state"] == "running"
        assert result["environment"] == "production"
        assert result["public_ip"] == "192.168.1.100"
        assert "last_seen" in result

    @patch('instance.find_instance_by_name')
    @patch('instance.start_instance')
    @patch('instance.wait_for_state')
    @patch.object(AnsibleModule, 'exit_json')
    def test_main_start_hibernated_instance(self, mock_exit_json, mock_wait, mock_start, mock_find):
        """Test main function starting a hibernated instance."""
        mock_find.side_effect = [
            ("production", "hibernated-vm", {"status": "hibernated"}),
            ("production", "hibernated-vm", {"status": "running", "size": "medium", "image": "ubuntu-22.04"})
        ]
        mock_start.return_value = (True, "hibernated")
        mock_wait.return_value = True
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": "hibernated-vm",
                "state": "running",
                "wait": True,
                "wait_timeout": 300,
                "force": False
            }
            module.check_mode = False
            
            instance.main.__globals__['module'] = module
            instance.main()
            
            mock_exit_json.assert_called_once()
            call_args = mock_exit_json.call_args[1]
            assert call_args["changed"] is True
            assert call_args["operation"] == "start"
            assert "duration" in call_args

    @patch('instance.find_instance_by_name')
    @patch.object(AnsibleModule, 'exit_json')
    def test_main_check_mode(self, mock_exit_json, mock_find):
        """Test main function in check mode."""
        mock_find.return_value = ("production", "hibernated-vm", {"status": "hibernated"})
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": "hibernated-vm",
                "state": "running",
                "wait": True,
                "wait_timeout": 300,
                "force": False
            }
            module.check_mode = True
            
            instance.main.__globals__['module'] = module
            instance.main()
            
            mock_exit_json.assert_called_once()
            call_args = mock_exit_json.call_args[1]
            assert call_args["changed"] is True
            assert call_args["operation"] == "would_running"

    @patch('instance.find_instance_by_name')
    @patch.object(AnsibleModule, 'fail_json')
    def test_main_instance_not_found(self, mock_fail_json, mock_find):
        """Test main function with non-existent instance."""
        mock_find.return_value = (None, None, None)
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": "non-existent",
                "state": "running",
                "wait": True,
                "wait_timeout": 300,
                "force": False
            }
            module.check_mode = False
            
            instance.main.__globals__['module'] = module
            instance.main()
            
            mock_fail_json.assert_called_once()
            call_args = mock_fail_json.call_args[1]
            assert "not found" in call_args["msg"]

    @patch('instance.find_instance_by_name')
    @patch.object(AnsibleModule, 'fail_json')
    def test_main_terminate_without_force(self, mock_fail_json, mock_find):
        """Test terminating running instance without force flag."""
        mock_find.return_value = ("production", "web-01", {"status": "running"})
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": "web-01",
                "state": "terminated",
                "wait": True,
                "wait_timeout": 300,
                "force": False
            }
            module.check_mode = False
            
            instance.main.__globals__['module'] = module
            instance.main()
            
            mock_fail_json.assert_called_once()
            call_args = mock_fail_json.call_args[1]
            assert "force=true" in call_args["msg"]

    @patch('instance.find_instance_by_name')
    @patch('instance.terminate_instance')
    @patch.object(AnsibleModule, 'exit_json')
    def test_main_force_terminate(self, mock_exit_json, mock_terminate, mock_find):
        """Test force terminating a running instance."""
        mock_find.side_effect = [
            ("production", "web-01", {"status": "running"}),
            (None, None, None)
        ]
        mock_terminate.return_value = (True, "running")
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": "web-01",
                "state": "terminated",
                "wait": True,
                "wait_timeout": 300,
                "force": True
            }
            module.check_mode = False
            
            instance.main.__globals__['module'] = module
            instance.main()
            
            mock_exit_json.assert_called_once()
            call_args = mock_exit_json.call_args[1]
            assert call_args["changed"] is True
            assert call_args["operation"] == "terminate"
            assert call_args["instance"]["state"] == "terminated"