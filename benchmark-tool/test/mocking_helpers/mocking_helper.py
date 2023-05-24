from unittest.mock import MagicMock
from sys import modules
from collections.abc import Callable


class MockingHelper:
    """Class that makes the mocking tools from python easier to use"""

    __main_modules: list[str] = []

    def add_main_module(self, module_name: str):
        """Adds a module to the list of modules that should be restored after each test.
        This is useful for modules that are imported in the test file itself.

        Args:
            moduleName (str): The name of the module to be restored after each test
        """
        self.__main_modules.append(module_name)

    def mock_import(self, module_name: str, mock: MagicMock | None = None):
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

        modules[module_name] = actual_mock

    def reset_mocks(self):
        # for each module that was mocked, restore the original module
        for module_name in self.__main_modules:
            del modules[module_name]
        self.__main_modules.clear()


def async_lambda(fun: Callable[[], object]):
    """Wraps a function into an async lambda function.
    This is useful for mocking async functions.
    """

    async def wrapper():
        return fun()

    return wrapper
