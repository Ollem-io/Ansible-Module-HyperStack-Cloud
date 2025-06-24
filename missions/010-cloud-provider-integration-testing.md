# Mission 010: Cloud Provider Integration Testing

## Mission Title
Create Integration Test Playbook for Real Cloud Provider Testing

## Mission Description
Create a comprehensive Ansible playbook to test the cloud_manager module against the real Hyperstack cloud provider. This playbook will validate environment operations, firewall management, and VM label management using real API calls.

## Mission Plan
1. Create a test playbook that runs on localhost
2. Configure API key from .env file (API_KEY_HYPER_STACK)
3. Implement test scenarios:
   - Environment validation tests
     - Check if "ansible-test" environment exists (expect success)
     - Check if "bad-ansible-test" environment doesn't exist (expect failure)
   - Firewall management tests
     - Create new firewall "ansible-integration-test" with port 443
     - Add port 22 to the firewall
     - Delete port 443 from the firewall
     - Get all firewall rules
   - VM label management tests
     - Get state of instance "inventive-hawking"
     - Add label "Ansible-Label-Test"
     - Get all labels and verify the new label is present
     - Remove the label

## Mission Status
- [ ] Create tests/ folder structure
- [ ] Create integration test playbook
- [ ] Implement environment validation tests
- [ ] Implement firewall management tests
- [ ] Implement VM label management tests
- [ ] Test playbook execution with real API

## Mission Notes
- Using API key from .env file with variable name API_KEY_HYPER_STACK
- Playbook will use localhost as target runner
- All tests will interact with real cloud provider API
- Proper error handling for expected failures (e.g., non-existent environment)