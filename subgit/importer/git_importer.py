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

import pysnooper

log = logging.getLogger(__name__)


class GitImport(SubGit):
    def __init__(self, config_file_name=None, answer_yes=None):
        self.answer_yes = answer_yes

        # Defaults config file to '.subgit-github.yml' if nothing is specified
        if not config_file_name:
            self.subgit_config_file_name = ".subgit-github.yml"
            self.subgit_config_file_path = os.path.join(os.getcwd(), self.subgit_config_file_name)
        else:
            self.subgit_config_file_name = config_file_name
            self.subgit_config_file_path = os.path.join(os.getcwd(), self.subgit_config_file_name)

    @pysnooper.snoop()
    def import_github(self, owner):
        """
        Given a username or organisation name, this method lists all repos connected to it 
        and writes a subgit config file.
        """
        out = subprocess.run([
                "gh",
                "repo",
                "list",
                f"{owner}",
                "--json",
                "id,name,defaultBranchRef,sshUrl",
                "-L",
                "100"
            ],
            shell=False,
            capture_output=True,
        )
        data = json.loads(out.stdout)
        repos = {}
        mapped_data = {x["name"]: x for x in data}
        sorted_names = sorted([repo["name"] for repo in data])

        if os.path.exists(self.subgit_config_file_path):
            answer = self.yes_no(f"File: {self.subgit_config_file_path} already exists on disk, do you want to overwrite the file?")

            if not answer:
                log.error("Aborting import")
                return 1

        for repo_name in sorted_names:
            repo_data = mapped_data[repo_name]

            repos[repo_name] = {
                "revision": {
                    "branch": repo_data["defaultBranchRef"]["name"],
                },
                "url": repo_data["sshUrl"],
            }

        if not repos:
            log.warning("Please make sure the repo owner is correct and that you have the correct permissions...")

        yml = yaml.YAML()
        yml.indent(mapping=2, sequence=4, offset=2)
        with open(self.subgit_config_file_path, "w") as stream:
            yml.dump({"repos": repos}, stream)

    def import_gitlab(self, owner):
        print("Gitlab")
