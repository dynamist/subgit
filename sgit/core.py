# -*- coding: utf-8 -*-

# python std lib
import copy
import logging
import os
import re

import ruamel
from ruamel import yaml

from sgit.exceptions import SgitConfigException


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
            # TODO: Minimal required data should be 'repos:'
            #       Raise error if missing from loaded config

    def _dump_config_file(self, config_data):
        """
        Writes the entire config file to the given disk path set
        in the method constructor.
        """
        with open(self.sgit_config_file_path, 'w') as stream:
            yaml.dump(config_data, stream, indent=2, default_flow_style=False)

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

    def repo_add(self, name, url, revision):
        if not name or not url or not revision:
            raise SgitConfigException(f'Name "{name}, url "{url}" or revision "{revision}" must be set')

        config = self._get_config_file()

        if name in config['repos']:
            raise SgitConfigException(f'Repo with name "{name}" already exists in config file')

        config['repos'][name] = {
            'clone-url': url,
            'revision': revision,
        }

        self._dump_config_file(config)

    def repo_remove(self, name):
        if not name:
            raise SgitConfigException(f'Name "{name}" must be set to sometihng')

        config = self._get_config_file()

        if name not in config['repos']:
            raise SgitConfigException(f'No repo with name "{name}" found in config file')

        del config['repos'][name]

        self._dump_config_file(config)

        print(f'Removed repo "{name}" from config file')

    def repo_set(self):
        pass
