# -*- coding: utf-8 -*-

# python std lib
import os

# sgit imports
from sgit.core import Sgit, DEFAULT_REPO_CONTENT

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
