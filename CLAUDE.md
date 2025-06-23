# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Ansible module repository which will allows the ansible to interacts with Hyperstack.cloud provider. It's a Open Source project.

# Workflow

## Ask if has a Jira Ticket or GH issue associated with the task

* Till the first relase, we will use the main branch.
* After the first release, we will use the release branch. And will requires new branch for new features.

## 1. Create a new branch

```bash
git checkout -b <GH Issue Number> or <GH Issue Number>/<GH Issue Title> or feature/<GH Issue Title>
```

## 2. Create a Mission file

- Create the folder missions/ if it doesn't exist
- Create the file missions/<mission number>-<GH Issue Title>.md, increment the mission number for each new mission
- The mission number is the number of the mission in the order of the missions.
- Write the mission in the file

### Mission file structure

- Mission Number
- Mission Title
- Mission Description
- Mission Plan
- Mission Status
- Mission Notes

## Ask for approval

## 3. Start working

- Create the file missions/<mission number>-<GH Issue Title>.md, increment the mission number for each new mission
- Write the mission in the file

## 4. Commit changes, must be incremental, for each major step finalized of the plan, commit.

commit msg structure:

get the user name and email from the git config, them add to the commit msg

```
verb(object): <description> 120 chars max

details: [list of details]

Author: $(git config user.name) <$(git config user.email)>

AI Assistant:
- Claude Code
```

## Feature Development Memories

- After a new feature must check if the logs are consistent and working with a valid config.

## Code Style and Standards

- Follow the comprehensive code style guide located at `hyperstack/ansible_collections/hyperstack/cloud/docs/code-style-and-guide.md`
- All Python code must follow PEP 8 with 120-character line limit
- Use proper Ansible module structure with DOCUMENTATION, EXAMPLES, and RETURN sections
- Implement comprehensive error handling and input validation
- Ensure idempotency and check mode support for all modules
- Write unit tests for all new modules and functions
- Use meaningful commit messages following the established format
- Validate all sensitive parameters with `no_log=True`
- Follow security best practices for API integration 