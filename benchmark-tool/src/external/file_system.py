import os


def move_file_to_folder(file_location: str, target_folder: str):
    target_path = os.path.join(target_folder, os.path.basename(file_location))
    os.rename(file_location, target_path)


def get_filename_from_path(path: str):
    return os.path.basename(path)
