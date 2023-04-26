# Explanation for chosen dependencies

This document explains why specific dependencies were chosen. Considered technologies were generally taken from the [awesome python list](https://github.com/vinta/awesome-python)

## Code style

- Autoformatting: [black](https://github.com/psf/black) was chosen mainly, because it is supported, by the python vscode extension and recommended by [pylint](https://github.com/pylint-dev/pylint).
- Linting: [pylint](https://github.com/pylint-dev/pylint). Pylint because it is very powerful. If the project becomes big enough to a point where pylint is too slow, flake8 could also be added to achieve fast feedback while writing code.

## Libraries that may be useful in the future

- YAML (for reading config files): <https://pyyaml.org/wiki/PyYAMLDocumentation>
