# Hyperstack Cloud Provider Integration Tests

This directory contains integration tests for the Hyperstack Ansible modules that interact with the real cloud provider API.

## Prerequisites

1. Set the `API_KEY_HYPER_STACK` environment variable in the `.env` file at the project root
2. Ensure the following resources exist in your Hyperstack account:
   - Environment: `ansible-test`
   - VM: `inventive-hawking`
3. Ensure the environment `bad-ansible-test` does NOT exist (used for negative testing)

## Running the Tests

To run the integration tests:

```bash
# Load environment variables
source .env

# Run the playbook
ansible-playbook tests/integration_test_cloud_provider.yml
```

## Test Coverage

The integration test playbook covers:

1. **Environment Validation**
   - Verifies existing environment (`ansible-test`)
   - Verifies non-existing environment (`bad-ansible-test`)

2. **Firewall Management**
   - Creates firewall rule with port 443
   - Adds SSH port 22
   - Deletes port 443 rule
   - Lists all firewall rules

3. **VM Label Management**
   - Gets VM information
   - Adds a label to VM
   - Verifies label presence
   - Removes the label

## Cleanup

The playbook includes cleanup tasks to remove any resources created during testing.