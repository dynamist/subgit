# -*- coding: utf-8 -*-

# python std lib

# rediscluster imports
from subgit.core import SubGit

# 3rd party imports
import pytest


@pytest.fixture()
def subgit(tmpdir, *args, **kwargs):
    """ """
    conf_file = tmpdir.join(".subgit.yml")

    return SubGit(config_file_path=conf_file, *args, **kwargs)
