# -*- coding: utf-8 -*-

# python std lib
import os

# sgit imports
from sgit.core import Sgit, DEFAULT_REPO_CONTENT
from sgit.exceptions import *

# 3rd party imports
import pytest
from ruamel import yaml


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

    with open(sgit.sgit_config_file_path, 'r') as stream:
        content = stream.read()

    assert content == DEFAULT_REPO_CONTENT


def test_init_repo_file_exists(sgit):
    """
    """
    sgit.sgit_config_file_path.write("foobar")

    retcode = sgit.init_repo()

    assert retcode == 1


def test_get_config_file(sgit):
    retcode = sgit.init_repo()
    assert retcode == None

    loaded_config = sgit._get_config_file()
    assert loaded_config == {'repos': {}}

    ## If no .sgit config file exists we should get system exit call
    os.remove(sgit.sgit_config_file_path)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        sgit._get_config_file()

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_dump_config_file(sgit):
    retcode = sgit.init_repo()
    assert retcode == None

    mock_config_data = {'foo': 'bar'}
    sgit._dump_config_file(mock_config_data)

    with open(sgit.sgit_config_file_path, 'r') as stream:
        file_content = yaml.load(stream, Loader=yaml.Loader)

    assert file_content == mock_config_data


def test_repo_list(sgit):
    retcode = sgit.init_repo()
    assert retcode == None

    ## Assume that if no repo has been added we should get an error
    ## The default configfile after init_repo is empty and usable here
    retcode = sgit.repo_list()
    assert retcode == 1


def test_repo_add(sgit):
    retcode = sgit.init_repo()
    assert retcode == None

    ## Test exception failure if we send in the wrong data
    with pytest.raises(SgitConfigException) as pytest_wrapped_e:
        sgit.repo_add(None, None, None)

    assert pytest_wrapped_e.type == SgitConfigException

    ## Do a valid add of a new repo
    name = 'foobar'
    gitrepo = 'git@github.com/sgit'
    revision = 'master'

    sgit.repo_add(name, gitrepo, revision)

    saved_data = sgit._get_config_file()
    assert saved_data == {
        'repos': {
            name: {
                'clone-url': gitrepo,
                'revision': {
                    'branch': revision,
                }
            }
        }
    }

    ## If rerunning the same config then it should cause an error
    retcode = sgit.repo_add(name, gitrepo, revision)
    assert retcode == 1


def test_repo_remove(sgit):
    retcode = sgit.init_repo()
    assert retcode == None

    config = sgit._get_config_file()
    assert 'foobar' not in config['repos']

    ## Initially there is no repo added so it shold fail out
    with pytest.raises(SgitConfigException) as pytest_wrapped_e:
        sgit.repo_remove(None)

    assert pytest_wrapped_e.type == SgitConfigException

    ## If we provide a name that do not exist in the config file
    retcode = sgit.repo_remove('foobar')
    assert retcode == 1

    ## Add a repo and try to remove it
    sgit.repo_add('foobar', 'foo@bar.com', 'master')
    retcode = sgit.repo_remove('foobar')
    assert retcode == None

    config = sgit._get_config_file()
    assert 'foobar' not in config['repos']


def test_repo_set(sgit):
    retcode = sgit.init_repo()
    assert retcode == None

    ## Test that providing bad types fail in exception
    with pytest.raises(SgitConfigException) as pytest_wrapped_e:
        sgit.repo_remove(None)

    assert pytest_wrapped_e.type == SgitConfigException

    ## When providing a repo name that do not exists it should fail out
    retcode = sgit.repo_remove('foobar')
    assert retcode == 1

    ## Add a repo with certain attributes. Update them and test they got saved
    sgit.repo_add('1a', '1a', '1c')

    retcode = sgit.repo_set('1a', 'url', '2c')
    assert retcode is None

    retcode = sgit.repo_set('1a', 'branch', '2d')
    assert retcode is None

    config = sgit._get_config_file()
    assert config['repos']['1a']['clone-url'] == '2c'
    assert config['repos']['1a']['revision']['branch'] == '2d'


def test_repo_rename(sgit):
    retcode = sgit.init_repo()
    assert retcode == None

    ## If source and destination repo name is the same, throw error
    retcode = sgit.repo_rename('foobar', 'foobar')
    assert retcode == 1

    ## If destination repo name already exists then throw error
    sgit.repo_add('qwerty', 'qwe@rty.se', 'master')
    retcode = sgit.repo_rename('foobar', 'qwerty')
    assert retcode == 2

    sgit.repo_add('foobar', 'bar@foo.se', 'master')
    retcode = sgit.repo_rename('foobar', 'barfoo')
    assert retcode is None

    config = sgit._get_config_file()
    assert 'foobar' not in config['repos']
    assert 'barfoo' in config['repos']
