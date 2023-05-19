"""Adapter for file system operations. This is needed to mock file system operations in unit tests"""

import os
from shutil import copy


def is_dir(path: str):
    return os.path.isdir(path)


def move_file_to_folder(file_location: str, target_folder: str):
    target_path = os.path.join(target_folder, os.path.basename(file_location))
    copy(file_location, target_path)


def get_filename_from_path(path: str):
    return os.path.basename(path)
