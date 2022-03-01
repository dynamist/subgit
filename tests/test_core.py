# -*- coding: utf-8 -*-

# python std lib
import os

# subgit imports
from subgit.constants import *
from subgit.core import SubGit
from subgit.exceptions import SubGitConfigException

# 3rd party imports
import pytest
from git import Repo
from ruamel import yaml


def user_data():
    working_gitname = "working"
    working_giturl = "git+https://github.com/dynamist/subgit.git"
    working_gitrev = "master"

    branch_gitname = "broken-branch"
    branch_giturl = "git+https://github.com/dynamist/subgit.git"
    branch_gitrev = "branch-doesnt-exist"

    non_working_gitname = "broken-url"
    non_working_giturl = "git+https://github.com/dynamist/subgit-nonworking.git"
    non_working_gitrev = "master"

    repository_test_data = {
        working_gitname: {
            "url": working_giturl,
            "revision": {"branch": working_gitrev},
        },
        branch_gitname: {
            "url": branch_giturl,
            "revision": {"branch": branch_gitrev},
        },
        non_working_gitname: {
            "url": non_working_giturl,
            "revision": {"branch": non_working_gitrev},
        },
    }
    return repository_test_data


def test_class_create(subgit):
    assert subgit.subgit_config_file_name is not None
    assert subgit.subgit_config_file_path is not None


def test_class_create_custom_tmp_file(tmp_path):
    s = SubGit(config_file_path=tmp_path)
    assert s.subgit_config_file_name is not None
    assert s.subgit_config_file_name == os.path.basename(tmp_path)

    assert s.subgit_config_file_path is not None
    assert s.subgit_config_file_path == tmp_path


def test_init_repo(subgit):
    """
    Assumes that the fixtures sets a file path but that the file do not exists yet
    """
    retcode = subgit.init_repo()
    assert retcode is None

    with open(subgit.subgit_config_file_path, "r") as stream:
        content = yaml.load(stream)

    assert content == DEFAULT_REPO_DICT


def test_init_repo_file_exists(subgit):
    subgit.subgit_config_file_path.write("foobar")

    retcode = subgit.init_repo()

    assert retcode == 1


def test_get_config_file(subgit):
    retcode = subgit.init_repo()
    assert retcode is None

    loaded_config = subgit._get_config_file()
    assert loaded_config == {"repos": {}}

    # If no .subgit config file exists we should get system exit call
    os.remove(subgit.subgit_config_file_path)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        subgit._get_config_file()

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_dump_config_file(subgit):
    retcode = subgit.init_repo()
    assert retcode is None

    mock_config_data = {"foo": "bar"}
    subgit._dump_config_file(mock_config_data)

    with open(subgit.subgit_config_file_path, "r") as stream:
        file_content = yaml.load(stream, Loader=yaml.Loader)

    assert file_content == mock_config_data


def test_repo_status(subgit):
    retcode = subgit.init_repo()
    assert retcode is None

    # Assume that if no repo has been added we should get an error
    # The default configfile after init_repo is empty and usable here
    retcode = subgit.repo_status()
    assert retcode == 1


def test_repo_pull(subgit, mocker):
    retcode = subgit.init_repo()
    assert retcode is None

    # Update with no arguments should raise TypeError
    with pytest.raises(TypeError) as pytest_wrapped_e:
        subgit.pull()
    assert pytest_wrapped_e.type == TypeError

    # Update with no answer should return 1
    mocker.patch("builtins.input", return_value="no")
    retcode = subgit.pull("all")
    assert retcode == 1


def test_repo_pull_all(subgit, mocker, monkeypatch):
    def mock_clone(*args, **kwargs):
        switcher = {
            "working": True,
            "broken-url": Exception("Broken url"),
            "broken-branch": Exception("Broken branch"),
        }
        ret = switcher.get(os.path.basename(args[1]), Exception("mock_clone exception"))

        if isinstance(ret, Exception):
            raise ret
        else:
            return ret

    retcode = subgit.init_repo()
    assert retcode is None

    # Patch input to yes further on
    mocker.patch("builtins.input", return_value="yes")

    # If no config is present or a repo is enabled it should return code 1
    retcode = subgit.pull("all")
    assert retcode == 1

    mocker.patch("builtins.input", return_value="yes")
    monkeypatch.setattr(Repo, "clone_from", mock_clone)

    # Update 'all' should return SubGitException with faulty input
    data = {"repos": {"broken-url": user_data().get("broken-url")}}
    subgit.subgit_config_file_path.write(data)

    with pytest.raises(SubGitConfigException) as pytest_wrapped_e:
        subgit.pull("all")
    assert pytest_wrapped_e.type == SubGitConfigException
    del data

    # Update 'all' should return xx with correct input
    # TODO: more pull all tests


def test_repo_pull_named(subgit, mocker):
    retcode = subgit.init_repo()
    assert retcode is None

    # Update with 'test' should return 1
    retcode = subgit.pull("test")
    assert retcode == 1

    # TODO: more named pull tests


def test_repo_pull_list(subgit, mocker):
    retcode = subgit.init_repo()
    assert retcode is None

    # Update with list should return 1
    data = list(user_data().keys())
    retcode = subgit.pull(data)
    assert retcode == 1
    del data

    # TODO: more pull list() tests


def test_repo_pull_dict(subgit, mocker):
    retcode = subgit.init_repo()
    assert retcode is None

    # TODO: Fix broken code block
    # # Update with dict should raise TypeError
    # data = user_data().keys()
    # with pytest.raises(TypeError) as pytest_wrapped_e:
    #     subgit.pull(data)
    # assert pytest_wrapped_e.type == TypeError
    # del data

    # TODO: more pull dict() tests
