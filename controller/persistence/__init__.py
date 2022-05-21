import os, os.path
from typing import Iterator


class Dataset:
    def __init__(self, name: str, path: str, mtime: float):
        self.name = name
        self.path = path
        self.mtime = mtime

    def __repr__(self) -> str:
        return f"Dataset: \"{self.name}\"  -->  \"{self.path}\")"


class DataStorage:
    def __init__(self, data_storage_dir):
        # ensure folder exists
        os.makedirs(data_storage_dir, exist_ok=True)

        self.__storage_dir = data_storage_dir


    def save_dataset(self, name: str, content: bytes):
        filename_dest = os.path.join(self.__storage_dir, name)
        save_file = open(filename_dest, 'wb')
        save_file.write(content)


    # TODO: what to do in case of error
    def get_dataset(self, name: str) -> Dataset:
        path = os.path.join(self.__storage_dir, name)
        if not os.path.exists(path):
            # dataset path does not exist
            raise FileNotFoundError

        mtime = os.path.getmtime(os.path.join(self.__storage_dir, name))

        return Dataset(name, path, mtime)


    def get_datasets(self) -> 'Iterator[Dataset]':
        files = [f for f in os.listdir(self.__storage_dir)]
        # ignore dotfiles, eg. ".gitkeep"
        files = filter(lambda f: not f.startswith("."), files)

        return [self.get_dataset(file) for file in files]
