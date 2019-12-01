# -*- coding: utf-8 -*-

# python std lib
import copy
import logging
import os
import re

import ruamel
from ruamel import yaml

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Sgit(object):
    def __init__(self):
        self.sgit_config_file_name = '.sgit.yaml'

        self.sgit_config_file_path = os.path.join(
            os.getcwd(),
            self.sgit_config_file_name,
        )

    def init_repo(self):
        """
        Algorithm:
            - Check if .sgit.yaml exists
                - If exists:
                    - Exit out from script
                - If do not exists
                    - Write new initial empty file to disk
        """
        default_repo_content = "repos:\n"

        if os.path.exists(self.sgit_config_file_path):
            print(f"File '{self.sgit_config_file_name}' already exists on disk")
        else:
            with open(self.sgit_config_file_path, 'w') as stream:
                stream.write(default_repo_content)
                print(f'Successfully wrote new config file "{self.sgit_config_file_name}" to disk')

    def _get_config_file(self):
        with open(self.sgit_config_file_path, 'r') as stream:
            return yaml.load(stream, Loader=ruamel.yaml.Loader)

    def repo_list(self):
        config = self._get_config_file()
        repos = config.get('repos', {})

        print(f" ** All repos **")

        if not repos:
            print(f"  No repos found")
            return

        for repo_name, repo_data in repos.items():
            print(f"")
            print(f" - {repo_name}")
            print(f"   - URL: {repo_data.get('clone-url')}")
            print(f"   - Rev: {repo_data.get('revision')}")

    def repo_add(self):
        pass

    def repo_remove(self):
        pass

    def repo_set(self):
        pass
