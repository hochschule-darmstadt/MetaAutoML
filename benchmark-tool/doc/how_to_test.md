# How to test (unit tests)

This document explains, how the unit testing framework [pytest](https://docs.pytest.org/en/7.3.x/getting-started.html) is used and which conventions were defined for the tests.

## Add a new test

1. Create a file in the `test` folder prefixed with `test_` (e.g. `test_sample.py`)
2. Define a function prefixed with `test_` and use `assert` inside it. Example:

    ```python
        def test_plus_should_return_6_when_given_2_and_4():
        assert 2 + 4 == 6
    ```

### async tests

To let pytest accept async tests, the asyncio pytest plugin has to be activated at the top of the test file:

```python
pytest_plugins = ["pytest_asyncio"]
```

Then all async tests have to be attributed:

```python
@pytest.mark.asyncio
async def test_should_do_stuff_when_something_is_given():
    # test code using await
```

## Run tests

Use the vscode test explorer to run the tests. If no tests are shown, verify the following:

1. The correct folder is opened in vscode. (Correct folder is /benchmark-tool)
2. All requirements were installed (in case of doubt delete the .venv folder and rerun setupvenv.cmd (or setupvenv.sh))

## Naming convention for tests

`test_<method_name>_should_<do_expected_thing>_when_<something_is_given>`

## Mocking

Mocking is done on a module level. This means that what the import statements in the module under test resolve to is altered before the test.

### Preparation

Add the following code to the test file. It makes sure that all mocks are reset after each test.

```python
from unittest.mock import MagicMock
from mocking_helpers.mocking_helper import MockingHelper, async_lambda

__mocker = MockingHelper()

@pytest.fixture(autouse=True)
def setup_function():
    """resets all mocks after each test"""
    yield
    __mocker.reset_mocks()
```

So that the resetting of the mocks works, the mocker needs to know which module is the module under test.

Explanation: Python caches already imported modules and since we want to modify the module under test in each test, we need to clear the cached import. The mocker takes care of that.

Before calling the module under test:

```python
def call_tested_function():
    from mdoule.under.test import tested_function
    __mocker.add_main_module("module.under.test")
    return tested_function()
```

### Mocking module elements

#### Mocking a function

```python
__mocker.mock_import("module.to.be.mocked", MagicMock(functionName=lambda par1: "return value"))

# multiple functions
__mocker.mock_import("module.to.be.mocked", MagicMock(functionName=lambda par1: "return value", functionName2=lambda par1: "return value"))

# async function
__mocker.mock_import("module.to.be.mocked", MagicMock(functionName=async_lambda(lambda par1: "return value")))
```

#### Stubbing the whole module

```python
__mocker.mock_import("module.to.be.stubbed")
```

#### Mocking a function with spying capability

```python
mockedFunction = MagicMock()
__mocker.mock_import("module.to.be.mocked", MagicMock(functionName=mockedFunction))
assert mockedFunction.call_count == 1
assert mockedFunction.call_args == call(par1="", par2="") # must supply all parameters
assert mockedFunction.call_args["par1"] == ""

# async function
mockedAsyncFunction = MagicMock()
__mocker.mock_import("module.to.be.mocked", MagicMock(functionName=async_lambda(mockedAsyncFunction)))
```
