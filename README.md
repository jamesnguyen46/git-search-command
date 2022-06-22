# GIT SEARCH COMMAND

[![PyPI](https://img.shields.io/pypi/v/git-search-command?label=PyPi&logo=pypi&logoColor=white)](https://pypi.org/project/git-search-command/)
[![Last commit](https://img.shields.io/github/last-commit/jamesnguyen46/git-search-command?label=Last%20Commit&logo=github&logoColor=white&color=yellow)](https://github.com/jamesnguyen46/git-search-command/commits/)
[![Coverage](https://img.shields.io/codecov/c/github/jamesnguyen46/git-search-command/feature/code_coverage?token=HO0BAT95VI&label=Coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/jamesnguyen46/git-search-command)
[![Github Action](https://img.shields.io/github/workflow/status/jamesnguyen46/git-search-command/Push%20&%20Pull%20Request?label=CI&logo=github-actions&logoColor=white)](https://github.com/jamesnguyen46/git-search-command/actions/workflows/push_pull_request.yml)
[![License](https://img.shields.io/badge/license-Apache-orange?label=License&logo=apache&logoColor=white)](https://github.com/jamesnguyen46/git-search-command/blob/main/LICENSE)

A simple tool to search the content in files for your GitLab and GitHub repositories.

> This project has been implemented for PERSONAL USE. If you want more advanced features like creating issue, pull request ... may be refer to use [GLab](https://github.com/profclems/glab) or [GitHub CLI](https://github.com/cli/cli)

## Prerequisites

1. Install [Python3.7+](https://www.python.org/downloads/).
2. Create a personal access token on [GitLab](https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html) or [GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

## Installation

```
python -m pip install --upgrade pip
python -m pip install git-search-command
```

## Usage

### Environment

After finishing the installation you need to create new environment for searching

```
gsc gl env --new <environment_name>
```

Then input your host name and personal token as following

![](./resources/gsc_setup_env.gif)

### Search in GitLab

```
gsc gl search <keywork> --project <project_id>
```

![](./resources/gsc_gl_search_project.gif)

```
gsc gl search <keywork> --group <group_id_or_group_path>
```

![](./resources/gsc_gl_search_group.gif)

### Search in GitHub

Default is to search all repositories that you owned, not fork repository.

```
gsc gh search <keywork>
```

![](./resources/gsc_gh_search_all.gif)

```
gsc gh search <keywork> --repository <repository_full_name>
```

![](./resources/gsc_gh_search_repo.gif)

### See more

Read the [wiki](https://github.com/jamesnguyen46/git-search-command/wiki) for the detail of `gsc` commands.

## License

[Apache](https://github.com/jamesnguyen46/git-search-command/blob/main/LICENSE)
