# -*- coding: utf-8 -*-

# python std lib
import mock

# subgit imports
from subgit.core import SubGit

# 3rd party imports
import pytest


@pytest.fixture()
def subgit(tmpdir, *args, **kwargs):
    """ """
    conf_file = tmpdir.join(".subgit.yml")

    return SubGit(config_file_path=conf_file, *args, **kwargs)


@pytest.fixture(scope='function', autouse=True)
def universal_fixture(tmpdir):
    """
    Currently all tests require that we init an empty repos config
    """
    PATCHED_DEFAULT_REPO_DICT = {"repos": []}

    with mock.patch('subgit.core.DEFAULT_REPO_DICT', PATCHED_DEFAULT_REPO_DICT):
        yield
