# Explanation for chosen dependencies

This document explains why specific dependencies were chosen. Considered technologies were generally taken from the [awesome python list](https://github.com/vinta/awesome-python)

## Testing

The framework [Pytest](https://docs.pytest.org/en/7.3.x/getting-started.html) was chosen over the existing unittest functionality of the standard library, because it reduces the amount of syntax that developers have to get used to (always use assert) and it is also fully supported by the VS-Code python extension.

The framework [mamba](https://nestorsalceda.com/mamba/) was also considered, but was not chosen due to the fact, that its last release was 3 years ago which means that its probably discontinued.

### Code coverage

[coverage](https://pypi.org/project/coverage/) seems pretty straightforward.

## Code style

- Autoformatting: [black](https://github.com/psf/black) was chosen mainly, because it is supported, by the python vscode extension and recommended by [pylint](https://github.com/pylint-dev/pylint).
- Linting: [pylint](https://github.com/pylint-dev/pylint). Pylint because it is very powerful. If the project becomes big enough to a point where pylint is too slow, flake8 could also be added to achieve fast feedback while writing code.

## Libraries that may be useful in the future

- YAML (for reading config files): <https://pyyaml.org/wiki/PyYAMLDocumentation>
