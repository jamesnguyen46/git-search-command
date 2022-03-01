# GITLAB SEARCH COMMAND TOOLS

[![PyPI](https://img.shields.io/pypi/v/git-search-command?color=green&label=gsc)](https://pypi.org/project/git-search-command/)
[![Last commit](https://img.shields.io/github/last-commit/nguyen-ngoc-thach/git-search-command?color=yellow)](https://github.com/nguyen-ngoc-thach/git-search-command/commits/main)
[![Code style](https://img.shields.io/badge/code%20style-black-blue)](https://github.com/psf/black)
[![Code Quality](https://img.shields.io/github/workflow/status/nguyen-ngoc-thach/git-search-command/Code%20Quality?label=pylint)](https://github.com/nguyen-ngoc-thach/git-search-command/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License](https://img.shields.io/badge/license-Apache-orange)](https://github.com/nguyen-ngoc-thach/git-search-command/blob/main/LICENSE)

A simple tool to search the expression in the project scope for GitLab and GitHub repositories.

## Prerequisites

1.Install [Python3](https://www.python.org/downloads/)
2.Create a [personal GitLab access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#creating-a-personal-access-token) and store it in a secure place.

## Installation

```
python3 -m pip install git-search-command
```

After finishing the installation you need to configure the personal access token and host name :

```
gsc gl config --token <gitlab_personal_token>
gsc gl config --url <gitlab_host_name>
```

See more details :

```
gsc gl config --help
```

## Usage

```
$ gsc gl search --help

Usage: gsc gl search [OPTIONS] <keyword>

  Search the content in GitLab repositories

Options:
  -g, --group <string>  Search in the specified group
  -p, --project <int>   Search in the specified project
  -h, --help            Show this message and exit.
```

## License

[Apache](https://github.com/nguyen-ngoc-thach/git-search-command/blob/main/LICENSE)

## Reference documents

- <https://docs.github.com/en/rest/reference/search#search-code--code-samples>
- <https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories>