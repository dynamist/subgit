# -*- coding: utf-8 -*-

# python std lib
import json
import logging
import subprocess

# subgit imports
from subgit.core import SubGit

# 3rd party imports
from ruamel import yaml


log = logging.getLogger(__name__)


class GitInspect(SubGit):
    def __init__(self, is_archived=False):
        self.is_archived = is_archived

    def _cli_installed(self, source):
        """
        When passed either 'github' or 'gitlab' to this method,
        returns True if the cli for the given source is installed,
        else returns False
        """
        if source == "github":
            shell_command = "gh"
        else:
            shell_command = "gitlab"

        try:
            subprocess.run([
                    shell_command,
                    "--help"
                ],
                shell=False,
                capture_output=True,
            )
        except FileNotFoundError:
            return False

        return True

    def inspect_github(self, owner):
        """
        Given a username or organisation name, this method lists all repos connected to it
        on github and writes a subgit config file.
        """
        if not self._cli_installed("github"):
            log.error("Github cli not installed. Exiting subgit...")
            return 1

        out = subprocess.run([
                "gh", "repo", "list",
                f"{owner}",
                "--json", "id,name,defaultBranchRef,sshUrl,isArchived",
                "-L", "100"
            ],
            shell=False,
            capture_output=True,
        )
        data = json.loads(out.stdout)
        repos = {}
        mapped_data = {
            repo["name"].lower():
            repo for repo in data
            if repo["isArchived"] == self.is_archived
        }
        sorted_names = sorted([
            repo["name"].lower()
            for repo in data
            if repo["isArchived"] == self.is_archived
        ])

        if not sorted_names:
            log.warning("Either the user does not exist, or the specified user doesn't have any available repos...")
            log.warning("Please make sure the repo owner is correct and that you have the correct permissions...")
            log.warning("No repos to write to file. Exiting...")
            return 1

        for repo_name in sorted_names:
            repo_data = mapped_data[repo_name]

            if not repo_data["defaultBranchRef"]["name"]:
                repo_data["defaultBranchRef"]["name"] = None

        for repo_name in sorted_names:
            repo_data = mapped_data[repo_name]

            repos[repo_name] = {
                "revision": {
                    "branch": repo_data["defaultBranchRef"]["name"],
                },
                "url": repo_data["sshUrl"],
            }

        yaml_output = yaml.dump({"repos": repos}, default_flow_style=False, indent=2)

        print(yaml_output)

    def inspect_gitlab(self, owner):
        """
        Given a username or organisation name, this method lists all repos connected to it
        on gitlab and writes a subgit config file.
        """
        if not self._cli_installed("gitlab"):
            log.error("Gitlab cli not installed. Exiting subgit...")
            return 1

        out = subprocess.run(
            [
                "gitlab",
                "-o", "json",
                "project", "list",
                "--membership", "yes",
                "--all",
            ],
            shell=False,
            capture_output=True,
        )
        repos = {}
        data = json.loads(out.stdout)
        mapped_data = {
            repo["name"].lower():
            repo for repo in data
            if repo["namespace"]["name"] == owner and repo["archived"] == self.is_archived
        }
        sorted_names = sorted([
            repo["name"].lower()
            for repo in data
            if repo["namespace"]["name"] == owner and repo["archived"] == self.is_archived
        ])

        if not sorted_names:
            log.warning("Either the user does not exist, or the specified user doesn't have any available repos...")
            log.warning("Please make sure the repo owner is correct and that you have the correct permissions...")
            log.warning("No repos to write to file. Exiting...")
            return 1

        for repo_name in sorted_names:
            repo_data = mapped_data[repo_name]

            repos[repo_name] = {
                "revision": {
                    "branch": repo_data["default_branch"],
                },
                "url": repo_data["ssh_url_to_repo"],
            }

        yaml_output = yaml.dump({"repos": repos}, default_flow_style=False, indent=2)

        print(yaml_output)
