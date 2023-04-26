# How to test (unit tests)

This document explains, how the unit testing framework [pytest](https://docs.pytest.org/en/7.3.x/getting-started.html) is used and which conventions were defined for the tests.

## Add a new test

1. Create a file in the `test` folder prefixed with `test_` (e.g. `test_sample.py`)
2. Define a function prefixed with `test_` and use `assert` inside it. Example:

    ```python
        def test_given_2_and_4_when_adding_then_returns_6():
        assert 2 + 4 == 6
    ```

## Run tests

Use the vscode test explorer to run the tests. If no tests are shown, verify the following:

1. The correct folder is opened in vscode. (Correct folder is /benchmark-tool)
2. All requirements were installed (in case of doubt delete the .venv folder and rerun setupvenv.cmd (or setupvenv.sh))
