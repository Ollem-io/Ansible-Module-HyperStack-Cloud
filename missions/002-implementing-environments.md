# Mission 002: Implementing and Testing the 'Environments' Feature

## Mission Number
002

## Mission Title
Implementing and Testing the 'Environments' Feature

## Mission Description
Implement the first core feature of the cloud_manager module: creating and deleting named "environments." This mission introduces fundamental Ansible concepts of state management (present, absent), idempotency, and the changed status. Both unit and integration tests will be written to validate this behavior.

## Mission Plan

### Phase 1: Feature Implementation
1. **Update Module Documentation** ✅
   - Add `name` parameter documentation for environment name
   - Add `state` parameter documentation with choices (present, absent)
   - Update DOCUMENTATION block in `plugins/modules/cloud_manager.py`

2. **Define Argument Specification** ✅
   - Mirror DOCUMENTATION block in argument_spec
   - Add name (str, required=True)
   - Add state (str, default='present', choices=['present', 'absent'])
   - Enable check_mode support

3. **Implement Core Python Logic** ✅
   - Add mock environment database (_CLOUD_ENVIRONMENTS)
   - Create helper functions:
     - `get_environment(name)` - Fetch environment from simulated API
     - `create_environment(name)` - Simulate environment creation
     - `delete_environment(name)` - Simulate environment deletion

4. **Implement Idempotent State Management** ✅
   - Handle state='present' scenarios:
     - Environment doesn't exist → Create it (changed=True)
     - Environment exists → No action (changed=False)
   - Handle state='absent' scenarios:
     - Environment exists → Delete it (changed=True)
     - Environment doesn't exist → No action (changed=False)
   - Respect check_mode for all write operations

### Phase 2: Unit Testing
1. **Create Test Helper Function** ✅
   - Implement `run_module()` helper with proper mocking
   - Mock get_environment, create_environment, delete_environment
   - Mock AnsibleModule and capture exit_json results

2. **Write Unit Tests** ✅
   - Test environment creation when absent
   - Test idempotency when environment already present
   - Test environment deletion when present
   - Test idempotency when environment already absent
   - Verify changed status and function calls in all scenarios

### Phase 3: Integration Testing
1. **Create Integration Test Target** ✅
   - Create directory structure: `tests/integration/targets/cloud_manager_env/tasks`
   - Create `main.yml` test playbook

2. **Implement Idempotency Test Pattern** ✅
   - Step 1: Create environment 'testing' → Assert changed=True
   - Step 2: Re-run creation → Assert changed=False (idempotency)
   - Step 3: Delete environment 'testing' → Assert changed=True
   - Step 4: Re-run deletion → Assert changed=False (idempotency)

### Phase 4: Documentation and Testing
1. **Update Module Examples** ✅
   - Add practical examples to EXAMPLES block
   - Show both 'present' and 'absent' states

2. **Run Full Test Suite** ✅
   - Execute unit tests: `ansible-test units --docker`
   - Execute integration tests: `ansible-test integration --docker cloud_manager_env`

3. **Update README** ✅
   - Document new environment management capability
   - Add usage examples

### Phase 5: Git Workflow
1. **Commit Feature Implementation** ✅
   - Stage module and test changes
   - Commit message: "feat(env): Implement state management for environments"

2. **Commit Documentation Updates** ✅
   - Stage documentation changes
   - Commit message: "docs(env): Add examples and update README for environment feature"

## Mission Status
**In Progress** - Currently implementing

## Mission Notes

### Key Implementation Details:
- The module must be idempotent - running the same task multiple times should only result in changes on the first run
- The `changed` status must accurately reflect whether any actual changes were made
- Check mode support allows users to preview changes without making them
- Mock functions simulate cloud API interactions for testing purposes

### Testing Strategy:
- **Unit tests** validate internal logic in isolation using mocks
- **Integration tests** verify the module works correctly when invoked by Ansible
- Both test types are essential for ensuring module quality and reliability

### Documentation Requirements:
- Use standard Ansible documentation macros (M(), O(), V(), etc.)
- Provide clear, copy-paste-ready examples
- Document all parameters with descriptions and constraints

### Success Criteria:
- All unit tests pass
- All integration tests pass
- Module correctly handles all four state scenarios
- Documentation is complete and accurate
- Code follows established style guidelines