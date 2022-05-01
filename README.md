# GIT SEARCH COMMAND

[![PyPI](https://img.shields.io/pypi/v/git-search-command)](https://pypi.org/project/git-search-command/)
[![Last commit](https://img.shields.io/github/last-commit/jamesnguyen46/git-search-command?color=yellow)](https://github.com/jamesnguyen46/git-search-command/commits/)
[![Code style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/github/workflow/status/jamesnguyen46/git-search-command/code-clean/master?label=pre-commit)](https://github.com/jamesnguyen46/git-search-command/actions/workflows/code_clean.yml)
[![License](https://img.shields.io/badge/license-Apache-orange)](https://github.com/jamesnguyen46/git-search-command/blob/main/LICENSE)

A simple tool to search the expression in files for your GitLab and GitHub repositories.

## Prerequisites

1. Install [Python3+](https://www.python.org/downloads/).
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