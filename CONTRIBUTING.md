# Submitting a PR

## Install the Checked Out FYeah Version
1. run `python -m pip install .` from the project's root directory

## Run All Tests
1. if it is not already avalible, `python pip -m pip install nox`
2. run `nox unittest` from the project's root directory

# Release Steps

## Final Testing
* verify all nox sessions pass

## Publishing Wheels
* make sure that the version in `pyproject.toml` has been incremented
* do a dryrun to TestPyPI
    * `python -m twine upload --repository-url=https://test.pypi.org/legacy/ dist/*`
* publish to PyPI
    * `python -m twine upload dist/*`
* test by pip installing the new version in a separate virtualenv
