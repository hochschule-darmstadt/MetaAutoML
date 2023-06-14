"""Adapter for file system operations. This is needed to mock file system operations in unit tests"""

import os
from shutil import copy


def is_dir(path: str):
    return os.path.isdir(path)


def copy_file_to_folder(file_location: str, target_folder: str):
    copy(file_location, target_folder)
