# GIT SEARCH COMMAND

[![PyPI](https://img.shields.io/pypi/v/git-search-command?label=PyPi&logo=pypi&logoColor=white)](https://pypi.org/project/git-search-command/)
[![Last commit](https://img.shields.io/github/last-commit/jamesnguyen46/git-search-command?label=Last%20Commit&logo=github&logoColor=white&color=yellow)](https://github.com/jamesnguyen46/git-search-command/commits/)
[![Coverage](https://img.shields.io/codecov/c/github/jamesnguyen46/git-search-command?token=HO0BAT95VI&label=Coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/jamesnguyen46/git-search-command)
[![Github Action](https://img.shields.io/github/actions/workflow/status/jamesnguyen46/git-search-command/push_pull_request.yml?label=CI&logo=github-actions&logoColor=white)](https://github.com/jamesnguyen46/git-search-command/actions/workflows/push_pull_request.yml)
[![License](https://img.shields.io/badge/license-Apache-orange?label=License&logo=apache&logoColor=white)](https://github.com/jamesnguyen46/git-search-command/blob/main/LICENSE)

A simple tool to search the content in your GitLab project or GitHub repositories.

> This project has been implemented for PERSONAL USE. If you want more advanced features like creating issue, pull request ... may be refer to use [GLab](https://gitlab.com/gitlab-org/cli) or [GitHub CLI](https://github.com/cli/cli)
>
> ## If this project is helpful for you, show your love ❤️ by putting a ⭐ on this project 😉.

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

![gsc_setup_env](https://user-images.githubusercontent.com/9126025/205210447-517c3fcc-6b5b-4d39-8c4d-aa89e1dc7ecc.gif)

### Search in GitLab

Default is to search all projects that you owned.

```
gsc gl search <keywork>
```

![gsc_gl_search](https://user-images.githubusercontent.com/9126025/205210438-274af890-4dc3-498b-8cc0-a01621d275ab.gif)

Search in a specific project

```
gsc gl search <keywork> --project <project_id>
```

Search in a specific group

```
gsc gl search <keywork> --group <group_id_or_group_path>
```

### Search in GitHub

Default is to search all repositories that you owned, not fork repository.

```
gsc gh search <keywork>
```

![gsc_gh_search](https://user-images.githubusercontent.com/9126025/205210430-1d495ebf-1538-413e-b3af-a60aeb144603.gif)

Search in a specific repository

```
gsc gh search <keywork> --repository <repository_full_name>
```

### See more

Read the [wiki](https://github.com/jamesnguyen46/git-search-command/wiki) for the detail of `gsc` commands.

## License

```
Copyright (C) 2022 James Nguyen

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
