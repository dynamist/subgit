# -*- coding: utf-8 -*-

# python std lib
import os

# sgit imports
from sgit.constants import *
from sgit.core import Sgit
from sgit.exceptions import SgitConfigException

# 3rd party imports
import pytest
from git import Repo
from ruamel import yaml


def user_data():
    working_gitname = "working"
    working_giturl = "git+https://github.com/dynamist/sgit.git"
    working_gitrev = "master"

    branch_gitname = "broken-branch"
    branch_giturl = "git+https://github.com/dynamist/sgit.git"
    branch_gitrev = "branch-doesnt-exist"

    non_working_gitname = "broken-url"
    non_working_giturl = "git+https://github.com/dynamist/sgit-nonworking.git"
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


def test_class_create(sgit):
    assert sgit.sgit_config_file_name is not None
    assert sgit.sgit_config_file_path is not None


def test_class_create_custom_tmp_file(tmp_path):
    s = Sgit(config_file_path=tmp_path)
    assert s.sgit_config_file_name is not None
    assert s.sgit_config_file_name == os.path.basename(tmp_path)

    assert s.sgit_config_file_path is not None
    assert s.sgit_config_file_path == tmp_path


def test_init_repo(sgit):
    """
    Assumes that the fixtures sets a file path but that the file do not exists yet
    """
    retcode = sgit.init_repo()
    assert retcode is None

    with open(sgit.sgit_config_file_path, "r") as stream:
        content = yaml.load(stream)

    assert content == DEFAULT_REPO_DICT


def test_init_repo_file_exists(sgit):
    sgit.sgit_config_file_path.write("foobar")

    retcode = sgit.init_repo()

    assert retcode == 1


def test_get_config_file(sgit):
    retcode = sgit.init_repo()
    assert retcode is None

    loaded_config = sgit._get_config_file()
    assert loaded_config == {"repos": {}}

    # If no .sgit config file exists we should get system exit call
    os.remove(sgit.sgit_config_file_path)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        sgit._get_config_file()

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_dump_config_file(sgit):
    retcode = sgit.init_repo()
    assert retcode is None

    mock_config_data = {"foo": "bar"}
    sgit._dump_config_file(mock_config_data)

    with open(sgit.sgit_config_file_path, "r") as stream:
        file_content = yaml.load(stream, Loader=yaml.Loader)

    assert file_content == mock_config_data


def test_repo_status(sgit):
    retcode = sgit.init_repo()
    assert retcode is None

    # Assume that if no repo has been added we should get an error
    # The default configfile after init_repo is empty and usable here
    retcode = sgit.repo_status()
    assert retcode == 1


def test_repo_pull(sgit, mocker):
    retcode = sgit.init_repo()
    assert retcode is None

    # Update with no arguments should raise TypeError
    with pytest.raises(TypeError) as pytest_wrapped_e:
        sgit.pull()
    assert pytest_wrapped_e.type == TypeError

    # Update with no answer should return 1
    mocker.patch("builtins.input", return_value="no")
    retcode = sgit.pull("all")
    assert retcode == 1


def test_repo_pull_all(sgit, mocker, monkeypatch):
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

    retcode = sgit.init_repo()
    assert retcode is None

    # Patch input to yes further on
    mocker.patch("builtins.input", return_value="yes")

    # If no config is present or a repo is enabled it should return code 1
    retcode = sgit.pull("all")
    assert retcode == 1

    mocker.patch("builtins.input", return_value="yes")
    monkeypatch.setattr(Repo, "clone_from", mock_clone)

    # Update 'all' should return SgitException with faulty input
    data = {"repos": {"broken-url": user_data().get("broken-url")}}
    sgit.sgit_config_file_path.write(data)

    with pytest.raises(SgitConfigException) as pytest_wrapped_e:
        sgit.pull("all")
    assert pytest_wrapped_e.type == SgitConfigException
    del data

    # Update 'all' should return xx with correct input
    # TODO: more pull all tests


def test_repo_pull_named(sgit, mocker):
    retcode = sgit.init_repo()
    assert retcode is None

    # Update with 'test' should return 1
    retcode = sgit.pull("test")
    assert retcode == 1

    # TODO: more named pull tests


def test_repo_pull_list(sgit, mocker):
    retcode = sgit.init_repo()
    assert retcode is None

    # Update with list should return 1
    data = list(user_data().keys())
    retcode = sgit.pull(data)
    assert retcode == 1
    del data

    # TODO: more pull list() tests


def test_repo_pull_dict(sgit, mocker):
    retcode = sgit.init_repo()
    assert retcode is None

    # TODO: Fix broken code block
    # # Update with dict should raise TypeError
    # data = user_data().keys()
    # with pytest.raises(TypeError) as pytest_wrapped_e:
    #     sgit.pull(data)
    # assert pytest_wrapped_e.type == TypeError
    # del data

    # TODO: more pull dict() tests
