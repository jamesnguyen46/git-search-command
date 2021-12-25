import argparse
from os import environ as env
from git_search.gitlab.gitlab_command import SearchCommand


def search_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("keyword", help="something that you want to find.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-p", "--project_id", type=int, help="the project id.")
    group.add_argument("-g", "--group", help="the group name.")
    args = parser.parse_args()

    if not env["GITLAB_API_TOKEN"]:
        raise ValueError('"GITLAB_API_TOKEN" field cannot be empty.')

    command = SearchCommand()
    if args.group:
        command.search_in_group(args.keyword, args.group)
    elif args.project_id:
        command.search_in_project(args.keyword, args.project_id)
    else:
        args.print_usage()


if __name__ == "__main__":
    search_main()
