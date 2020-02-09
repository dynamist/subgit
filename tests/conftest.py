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
def sgit(tmp_path, *args, **kwargs):
    """
    """
    return Sgit(config_file_path=tmp_path ,*args, **kwargs)
