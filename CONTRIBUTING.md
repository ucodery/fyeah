# Submitting a PR

## Install the Checked Out FYeah Version
1. run `make` from the project's root directory

## Run All Tests
1. if it is not already avalible, `pip install tox`
2. run `make test` from the project's root directory

# Release Steps

## Final Testing
* on each platform: Linux and MacOS
    * make all supported python versions available
    * run `make test` from the project's root directory
       * note: if running tests inside the manylinux docker image, one of the pythons under `/opt/python/` will need to be used as `PY` for `make test`
* verify all tests pass in all environments

## Publishing Wheels
* make sure that the version in `setup.py` has been incremented
* on MacOS
    * make all supported python versions available
    * run `make ensure all`
* using the manylinux docker image
    * run `docker run -v ~/git/fyeah/:/fyeah -w /fyeah/ quay.io/pypa/manylinux1_x86_64 make manylinux`
* collect all produced artifacts from each platform under `dist/`
* do a dryrun to TestPyPI
    * `python -m twine upload --repository-url=https://test.pypi.org/legacy/ dist/*`
* publish to PyPI
    * `python -m twine upload dist/*`
* test by pip installing the new version in a separate virtualenv

## Add Support for a New Python Version
* update the `python_requires` in setup.py to include the new python version
* add a classifier in setup.py for the new python version
* add a python version to `all` and `manylinux` in Makefile
* add an environment to tox.ini
