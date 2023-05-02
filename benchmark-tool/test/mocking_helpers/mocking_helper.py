from types import ModuleType
from unittest.mock import MagicMock
from sys import modules


class MockingHelper:
    """Class that makes the mocking tools from python easier to use"""

    __module_backup: dict[str, ModuleType] = {}

    def mock_import(self, module_name: str, mock: MagicMock | None):
        """Mocks an import statement.
        Instead of the normally imported module, the passed object is imported.
        If no object is passed, the import is stubbed instead.

        Args:
            moduleName (str): The name of the module to be mocked.
            mock (object | None): The object to be imported instead of the module
        """
        actual_mock = mock
        if mock is None:
            actual_mock = MagicMock()

        self.__module_backup[module_name] = modules[module_name]
        modules[module_name] = actual_mock

    def reset_mocks(self):
        # for each module that was mocked, restore the original module
        for module_name, module in self.__module_backup.items():
            modules[module_name] = module
        self.__module_backup.clear()
