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
import instance_info


class TestInstanceInfoModule:
    """Test cases for the instance_info module."""

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
                    "web-02": {
                        "name": "web-02",
                        "size": "small",
                        "image": "ubuntu-22.04",
                        "status": "stopped",
                        "public_ip": "192.168.1.101",
                        "private_ip": "10.0.1.101",
                        "created_at": "2024-01-01T01:00:00Z"
                    }
                }
            },
            "staging": {
                "id": "env-staging",
                "status": "active",
                "vms": {
                    "test-vm": {
                        "name": "test-vm",
                        "size": "medium",
                        "image": "rhel-9",
                        "status": "hibernated",
                        "public_ip": "192.168.2.100",
                        "private_ip": "10.0.2.100",
                        "created_at": "2024-01-01T02:00:00Z"
                    }
                }
            }
        }

    @patch('instance_info._load_state')
    def test_get_instance_by_name_found(self, mock_load_state, mock_state):
        """Test finding an instance by name."""
        mock_load_state.return_value = mock_state
        
        result = instance_info.get_instance_by_name("web-01")
        
        assert result is not None
        assert result["name"] == "web-01"
        assert result["state"] == "running"
        assert result["environment"] == "production"
        assert result["public_ip"] == "192.168.1.100"

    @patch('instance_info._load_state')
    def test_get_instance_by_name_not_found(self, mock_load_state, mock_state):
        """Test searching for non-existent instance."""
        mock_load_state.return_value = mock_state
        
        result = instance_info.get_instance_by_name("non-existent")
        
        assert result is None

    @patch('instance_info._load_state')
    def test_get_instance_by_ip(self, mock_load_state, mock_state):
        """Test finding an instance by IP address."""
        mock_load_state.return_value = mock_state
        
        result = instance_info.get_instance_by_ip("192.168.1.100")
        
        assert result is not None
        assert result["name"] == "web-01"
        assert result["public_ip"] == "192.168.1.100"

    @patch('instance_info._load_state')
    def test_get_instance_by_invalid_ip(self, mock_load_state, mock_state):
        """Test searching with invalid IP address."""
        mock_load_state.return_value = mock_state
        
        result = instance_info.get_instance_by_ip("invalid-ip")
        
        assert result is None

    @patch('instance_info._load_state')
    def test_get_instances_in_environment(self, mock_load_state, mock_state):
        """Test getting all instances in an environment."""
        mock_load_state.return_value = mock_state
        
        result = instance_info.get_instances_in_environment("production")
        
        assert len(result) == 2
        assert any(vm["name"] == "web-01" for vm in result)
        assert any(vm["name"] == "web-02" for vm in result)

    @patch('instance_info._load_state')
    def test_get_instances_in_empty_environment(self, mock_load_state, mock_state):
        """Test getting instances from environment without VMs."""
        mock_load_state.return_value = {"empty": {"id": "env-empty", "status": "active"}}
        
        result = instance_info.get_instances_in_environment("empty")
        
        assert len(result) == 0

    @patch('instance_info._load_state')
    def test_get_all_instances(self, mock_load_state, mock_state):
        """Test getting all instances across environments."""
        mock_load_state.return_value = mock_state
        
        result = instance_info.get_all_instances()
        
        assert len(result) == 3
        environments = {vm["environment"] for vm in result}
        assert "production" in environments
        assert "staging" in environments

    def test_filter_instances_by_state(self):
        """Test filtering instances by state."""
        instances = [
            {"name": "vm1", "state": "running"},
            {"name": "vm2", "state": "stopped"},
            {"name": "vm3", "state": "hibernated"},
            {"name": "vm4", "state": "running"}
        ]
        
        running_instances = instance_info.filter_instances_by_state(instances, ["running"])
        assert len(running_instances) == 2
        
        stopped_instances = instance_info.filter_instances_by_state(instances, ["stopped", "hibernated"])
        assert len(stopped_instances) == 2
        
        all_instances = instance_info.filter_instances_by_state(instances, [])
        assert len(all_instances) == 4

    @patch('instance_info._load_state')
    @patch.object(AnsibleModule, 'exit_json')
    def test_main_query_by_name(self, mock_exit_json, mock_load_state, mock_state):
        """Test main function with name query."""
        mock_load_state.return_value = mock_state
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": "web-01",
                "ip_address": None,
                "environment": None,
                "instance_states": []
            }
            
            instance_info.main.__globals__['module'] = module
            instance_info.main()
            
            mock_exit_json.assert_called_once()
            call_args = mock_exit_json.call_args[1]
            assert call_args["changed"] is False
            assert call_args["count"] == 1
            assert len(call_args["instances"]) == 1
            assert call_args["instances"][0]["name"] == "web-01"

    @patch('instance_info._load_state')
    @patch.object(AnsibleModule, 'exit_json')
    def test_main_query_by_environment(self, mock_exit_json, mock_load_state, mock_state):
        """Test main function with environment query."""
        mock_load_state.return_value = mock_state
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": None,
                "ip_address": None,
                "environment": "production",
                "instance_states": []
            }
            
            instance_info.main.__globals__['module'] = module
            instance_info.main()
            
            mock_exit_json.assert_called_once()
            call_args = mock_exit_json.call_args[1]
            assert call_args["changed"] is False
            assert call_args["count"] == 2
            assert len(call_args["instances"]) == 2

    @patch('instance_info._load_state')
    @patch.object(AnsibleModule, 'exit_json')
    def test_main_query_with_state_filter(self, mock_exit_json, mock_load_state, mock_state):
        """Test main function with state filtering."""
        mock_load_state.return_value = mock_state
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": None,
                "ip_address": None,
                "environment": None,
                "instance_states": ["hibernated"]
            }
            
            instance_info.main.__globals__['module'] = module
            instance_info.main()
            
            mock_exit_json.assert_called_once()
            call_args = mock_exit_json.call_args[1]
            assert call_args["changed"] is False
            assert call_args["count"] == 1
            assert call_args["instances"][0]["state"] == "hibernated"

    @patch('instance_info._load_state')
    @patch.object(AnsibleModule, 'fail_json')
    def test_main_with_exception(self, mock_fail_json, mock_load_state):
        """Test main function error handling."""
        mock_load_state.side_effect = Exception("Test error")
        
        with patch.object(AnsibleModule, '__init__', return_value=None):
            module = AnsibleModule(argument_spec={}, supports_check_mode=True)
            module.params = {
                "name": "test-vm",
                "ip_address": None,
                "environment": None,
                "instance_states": []
            }
            
            instance_info.main.__globals__['module'] = module
            instance_info.main()
            
            mock_fail_json.assert_called_once()
            call_args = mock_fail_json.call_args[1]
            assert "Failed to retrieve instance information" in call_args["msg"]