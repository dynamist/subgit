# -*- coding: utf-8 -*-

# python std lib
import os

# sgit imports
from sgit.core import Sgit


def test_class_create(sgit):
    assert sgit.sgit_config_file_name is not None
    assert sgit.sgit_config_file_path is not None

def test_class_create_custom_tmp_file(tmp_path):
    s = Sgit(config_file_path=tmp_path)
    assert s.sgit_config_file_name is not None
    assert s.sgit_config_file_name == os.path.basename(tmp_path)

    assert s.sgit_config_file_path is not None
    assert s.sgit_config_file_path == tmp_path
