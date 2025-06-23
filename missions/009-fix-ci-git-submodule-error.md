# Mission 009: Fix CI Git Submodule Error

## Mission Title
Fix GitHub Actions CI failure due to git submodule mapping error

## Mission Description
The CI pipeline is failing with error "fatal: no submodule mapping found in .gitmodules for path 'hyperstack/ansible_collections/hyperstack/cloud'" when running integration tests. This is caused by a .git directory existing in the subdirectory.

## Mission Plan
1. Remove the .git directory from hyperstack/ansible_collections/hyperstack/cloud
2. Add the path to .gitignore to prevent future issues
3. Verify the fix works locally
4. Commit and push the changes

## Mission Status
In Progress

## Mission Notes
- GitHub Actions run: https://github.com/Ollem-io/Ansible-Module-HyperStack-Cloud/actions/runs/15837409711/job/44643700284
- Error occurs during `ansible-test integration` command
- Root cause: nested .git directory causing git to treat subdirectory as submodule