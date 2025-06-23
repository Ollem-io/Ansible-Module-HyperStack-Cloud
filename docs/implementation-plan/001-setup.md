# Mission 1: Project Scaffolding and Environment Setup

## Mission Number: 1

## Mission Title: Project Scaffolding and Environment Setup

Mission Description: In this foundational mission, the complete project structure for the Ansible Collection will be established using standard tooling. The initial placeholder module file will be created, and a basic "smoke test" will be written to confirm that the development environment is correctly configured and ready for development.

Mission Plan:

1. Understanding the Ansible Collection Structure

Before writing any code, it is essential to understand the standardized layout of an Ansible Collection. This structure is not arbitrary; it provides a predictable location for every type of content, which is crucial for both the Ansible engine and human collaborators. The ansible-galaxy tool generates a skeleton that adheres to this standard. The key components are outlined in the table below.   

Directory / File

Purpose

galaxy.yml

Required. The collection's metadata file. It contains the namespace, name, version, author, dependencies, and other information needed to build and publish the collection.   

README.md

Required. The main documentation for the collection. It should provide an overview, installation instructions, and usage examples. This is the first file a new user will read.   

plugins/

The directory for all Ansible plugins. It contains subdirectories for each plugin type.

plugins/modules/

The location for all custom modules written in Python or another language. The cloud_manager.py file will reside here.   

plugins/module_utils/

Contains shared code (libraries) that can be imported and used by multiple modules within the collection, promoting code reuse.   

tests/

The root directory for all tests. ansible-test expects tests to be located here.   

tests/units/

Contains unit tests. The directory structure within tests/units/ must mirror the structure of the plugins/ directory for test discovery to work.   

tests/integration/

Contains integration tests. These are structured as Ansible roles (called "targets") that are executed by ansible-playbook via ansible-test.   

docs/

A directory for extended documentation, such as a roadmap, guides, or other supplementary materials.   

roles/

A directory where full-fledged Ansible roles included with the collection are stored.   

meta/runtime.yml

An optional file that provides runtime metadata to the Ansible engine, such as the minimum required version of ansible-core.   

This clear separation of concerns—module code, collection metadata, unit tests, integration tests, and documentation—is a hallmark of a professional project and is fundamental to the collection architecture.

### 2. Scaffolding with `ansible-galaxy`
The first practical step is to generate the collection skeleton. The `ansible-galaxy` command-line tool, which is part of `ansible-core`, provides an `init` subcommand for this purpose.[3, 4] This ensures the project starts with the correct, community-standard structure.

Execute the following command in a development workspace. The name `my_cloud.manager` follows the `<namespace>.<collection_name>` convention.[4]

```bash
ansible-galaxy collection init my_cloud.manager
```

This command creates a directory named `my_cloud/manager/` containing the skeleton files and subdirectories as described in the table above.[4]

### 3. Configuring the Development Environment
To ensure a clean and reproducible development process, it is a critical best practice to isolate project dependencies from the system's global Python environment. This is achieved using a Python virtual environment.[15]

1.  **Navigate into the new collection directory:**
    ```bash
    cd my_cloud/manager/
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv.venv
    ```
    This creates a `.venv` directory containing a private copy of the Python interpreter and `pip`.

3.  **Activate the virtual environment:**
    ```bash
    source.venv/bin/activate
    ```
    The shell prompt will change to indicate that the virtual environment is active. All subsequent `pip` installations will be confined to this environment.

4.  **Install development dependencies:**
    For module development, a minimal set of dependencies is preferred. `ansible-core` contains the Ansible engine, `ansible-galaxy`, and `ansible-test`. `pytest` is the testing framework that `ansible-test` uses to execute unit tests.[8, 12]
    ```bash
    pip install "ansible-core>=2.15" "pytest"
    ```

### 4. Creating the Initial Module Stub
With the structure in place, the next step is to create a placeholder for the module itself.

1.  **Create the module file:**
    ```bash
    touch plugins/modules/cloud_manager.py
    ```

2.  **Populate the file with boilerplate:**
    A valid Ansible module requires several key components, even in its simplest form. This boilerplate establishes the required structure for documentation and execution.[15, 16]

    ```python
    #!/usr/bin/python
    # -*- coding: utf-8 -*-

    # Copyright: (c) 2024, Your Name <your.email@example.com>
    # GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

    from __future__ import absolute_import, division, print_function
    __metaclass__ = type

    ANSIBLE_METADATA = {
        'metadata_version': '1.1',
        'status': ['preview'],
        'supported_by': 'community'
    }

    DOCUMENTATION = r'''
    ---
    module: cloud_manager
    short_description: Manages resources in MyCloud.
    version_added: "1.0.0"
    description:
        - This is a sample module for managing MyCloud resources like environments,
          firewalls, and virtual machines.
    author:
        - Your Name (@yourgithubhandle)
    '''

    EXAMPLES = r'''
    # Examples will be added in subsequent missions.
    '''

    RETURN = r'''
    # Return values will be documented as they are implemented.
    '''

    from ansible.module_utils.basic import AnsibleModule

    def main():
        """Main execution path of the module."""
        module = AnsibleModule(
            argument_spec=dict(),
            supports_check_mode=True
        )

        result = dict(
            changed=False,
            message='Module is under development.'
        )

        module.exit_json(**result)

    if __name__ == '__main__':
        main()
    ```

### 5. Writing the First Unit Test
The goal of this first test is not to validate complex logic but to confirm that the testing framework can find and execute tests for the new module. This is often called a "smoke test."

1.  **Create the test directory and file:**
    The path to the test file must mirror the path to the module file within the collection structure.[11]
    ```bash
    mkdir -p tests/units/plugins/modules/
    touch tests/units/plugins/modules/test_cloud_manager.py
    ```

2.  **Write the import test:**
    This simple `pytest` test function attempts to import the module. If the import succeeds, it confirms that the Python path is configured correctly by `ansible-test`.

    ```python
    # tests/units/plugins/modules/test_cloud_manager.py

    import pytest

    # Import the module that is being tested
    try:
        import ansible_collections.my_cloud.manager.plugins.modules.cloud_manager as cloud_manager
    except ImportError:
        # This is a fallback for older ansible-test versions or different test setups
        import cloud_manager

    def test_module_import():
        """
        A simple smoke test to ensure the module can be imported.
        """
        assert hasattr(cloud_manager, 'main')
    ```

### 6. The Development Workflow in Action
A disciplined workflow using version control is non-negotiable for professional development.[17]

1.  **Initialize a Git repository:**
    ```bash
    git init
    git add.
    # Add.venv to.gitignore to avoid committing the virtual environment
    echo ".venv/" >>.gitignore
    git add.gitignore
    ```

2.  **Make the first commit:**
    A descriptive commit message establishes a clear history.
    ```bash
    git commit -m "Initial scaffold of my_cloud.manager collection"
    ```

3.  **Run the tests:**
    The `ansible-test` command is the canonical tool for testing Ansible content. Using the `--docker` flag is highly recommended as it runs tests inside a clean, consistent, and isolated container environment, preventing issues related to the host system's configuration.[12, 14]
    ```bash
    ansible-test units --docker -v
    ```
    The `-v` flag provides verbose output. The test should run and report `1 passed`. This confirms the entire development and testing toolchain is functional.

4.  **Update documentation and commit:**
    Good practice dictates that every functional change is accompanied by a documentation update.
    *   Edit the main `README.md` file to provide a brief description of the collection's purpose.
    *   Edit the `galaxy.yml` file to fill in the `description`, `authors`, and `repository` fields.
    ```bash
    git add README.md galaxy.yml
    git commit -m "docs: Update README and galaxy.yml with initial project info"
    ```
Mission Status: Complete

Mission Notes: This mission has established the disciplined "code, test, commit, document" rhythm that will be followed throughout the guide. The project now has a solid foundation, a working test harness, and a clear version history. This methodical approach, which front-loads best practices, is crucial for building reliable and maintainable automation.