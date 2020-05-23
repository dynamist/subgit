# -*- coding: utf-8 -*-

# python std lib
import os
import sys
import json

# rediscluster imports
from sgit.core import Sgit

# 3rd party imports
import pytest


@pytest.fixture()
def sgit(tmpdir, *args, **kwargs):
    """
    """
    conf_file = tmpdir.join(".sgit.yml")

    return Sgit(config_file_path=conf_file, *args, **kwargs)
