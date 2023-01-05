# -*- coding: utf-8 -*-

# python std lib
import json
import logging
import os
import subprocess

# subgit imports
from subgit.core import SubGit

# 3rd party imports
from ruamel import yaml


log = logging.getLogger(__name__)


class GitImport(SubGit):
    def __init__(self, config_file_name=None, answer_yes=None, is_archived=False):
        self.answer_yes = answer_yes
        self.is_archived = is_archived

        # Defaults config file to '.subgit-github.yml' if nothing is specified
        if not config_file_name:
            self.subgit_config_file_name = ".subgit.yml"

            if self.is_archived:
                self.subgit_config_file_name = ".subgit-archived.yml"
        else:
            self.subgit_config_file_name = config_file_name

        self.subgit_config_file_path = os.path.join(os.getcwd(), self.subgit_config_file_name)

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
            out = subprocess.run([
                    shell_command,
                    "--help"
                ],
                shell=False,
                capture_output=True,
            )
        except FileNotFoundError:
            return False

        return True

    def import_github(self, owner):
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

        if os.path.exists(self.subgit_config_file_path):
            answer = self.yes_no(f"File: {self.subgit_config_file_path} already exists on disk, do you want to overwrite the file?")

            if not answer:
                log.error("Aborting import")
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

        yml = yaml.YAML()
        yml.indent(mapping=2, sequence=4, offset=2)
        with open(self.subgit_config_file_path, "w") as stream:
            yml.dump({"repos": repos}, stream)

        log.info(f"Successfully wrote to file: {self.subgit_config_file_name}")
        return 0

    def import_gitlab(self, owner):
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
                "--get-all",
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

        if os.path.exists(self.subgit_config_file_path):
            answer = self.yes_no(f"File: {self.subgit_config_file_path} already exists on disk, do you want to overwrite the file?")

            if not answer:
                log.error("Aborting import")
                return 1

        for repo_name in sorted_names:
            repo_data = mapped_data[repo_name]

            repos[repo_name] = {
                "revision": {
                    "branch": repo_data["default_branch"],
                },
                "url": repo_data["ssh_url_to_repo"],
            }

        yml = yaml.YAML()
        yml.indent(mapping=2, sequence=4, offset=2)
        with open(self.subgit_config_file_path, "w") as stream:
            yml.dump({"repos": repos}, stream)

        log.info(f"Successfully wrote to file: {self.subgit_config_file_name}")
        return 0
