# Mission 011 - VM Instance Management Enhancement

## Mission Number
011

## Mission Title
Enhancement: VM Instance Management - Missing Instance Query and Direct VM Control

## Mission Description
The current `dsmello.cloud.cloud_manager` module provides environment-level VM management but lacks individual instance control capabilities needed for dynamic infrastructure automation. This mission aims to implement:

1. **Instance Discovery**: Query existing instances by IP/name
2. **Response Data**: Return VM details (IPs, status, etc.) from operations
3. **Direct Instance Control**: Start/stop specific hibernated instances by name

## Mission Plan

### Phase 1: Analysis and Design ✅
- [x] Analyze current `cloud_manager.py` module structure
- [x] Review HyperStack API endpoints for instance management
- [x] Design new module interfaces for instance operations
- [x] Plan backward compatibility for existing `cloud_manager` module

### Phase 2: Implementation ✅
- [x] Create `instance_info` module for querying specific instances
- [x] Create `instance` module for direct instance state management
- [x] Enhance `cloud_manager` module to return VM details in responses
- [x] Implement proper error handling and validation

### Phase 3: Documentation and Examples ✅
- [x] Add DOCUMENTATION, EXAMPLES, and RETURN sections for new modules
- [x] Create usage examples for dynamic instance revival workflows
- [x] Update collection README with new capabilities

### Phase 4: Testing ✅
- [x] Write unit tests for new modules
- [x] Create integration tests for instance management scenarios
- [x] Test hibernated instance revival workflows
- [x] Validate response data structure and accuracy

### Phase 5: Validation
- [ ] Run lint and typecheck commands
- [ ] Validate with real HyperStack environment
- [ ] Performance testing for instance queries
- [ ] Security review for API interaction

## Mission Status
**Status**: Implementation Complete - Ready for Validation
**Priority**: Medium-High
**GitHub Issue**: #3
**Started**: 2025-06-25
**Implementation Completed**: 2025-06-25

## Mission Notes

### Key Requirements from Issue:
1. **Instance Query Capability**:
   ```yaml
   - name: Get instance information
     dsmello.cloud.instance_info:
       name: "specific-instance-name"
     register: instance_details
   ```

2. **Enhanced Response Data**:
   ```yaml
   - name: Create/update VMs
     dsmello.cloud.cloud_manager:
       name: "environment"
       vms: [...]
     register: result
   # result should include VM details like IPs, current states
   ```

3. **Direct Instance Management**:
   ```yaml
   - name: Start hibernated instance
     dsmello.cloud.instance:
       name: "hibernated-instance"
       state: running
   ```

### Use Case Priority:
**Dynamic Instance Revival**: In automated deployments, need to:
1. Check if specific instances are hibernated by IP/name
2. Start hibernated instances before deployment
3. Get instance details for connection validation

### Technical Considerations:
- Follow existing code style guide at `hyperstack/ansible_collections/hyperstack/cloud/docs/code-style-and-guide.md`
- Maintain idempotency and check mode support
- Implement comprehensive error handling
- Use `no_log=True` for sensitive parameters
- Follow PEP 8 with 120-character line limit

### Testing Scenarios:
✅ **Working**: Environment management, VM creation/updates
❌ **Missing**: Instance discovery, hibernated instance revival, IP-based lookups

### Implementation Notes:
- Consider API rate limiting for instance queries
- Implement caching for frequently accessed instance data
- Ensure proper authentication handling across all new modules
- Validate instance name/IP formats before API calls