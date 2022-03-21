VPATH = fyeah:build
FYEAH_MAKE := $(lastword $(MAKEFILE_LIST))

PY = python3
LONG_PYVER = $(shell $(PY) -V | grep -oE '[0-9.]+')
SHORT_PYVER = $(basename $(LONG_PYVER))

.PHONY: install package install_wheel audit manylinux all ensure clean test

ML_PYTHONS:=$(foreach py,cp36-cp36m cp37-cp37m cp38-cp38 cp39-cp39 cp310-cp310,/opt/python/$(py)/bin/python)
PYTHONS:=python3.6 python3.7 python3.8 python3.9 python3.10

install: ast.c
	$(PY) -m pip install .[dev]

package: ast.c
	$(PY) -m build

install_wheel: package
	$(PY) -m pip install `$(PY) ./test/utils/find_wheel.py ./dist/`

audit: package
	auditwheel repair ./dist/*$(subst .,,$(SHORT_PYVER))*-linux_*.whl -w ./dist/
	rm ./dist/*$(subst .,,$(SHORT_PYVER))*-linux_*.whl

manylinux:
	$(foreach py, $(ML_PYTHONS), $(MAKE) -f $(FYEAH_MAKE) audit PY=$(py);)

all:
	$(foreach py, $(PYTHONS), $(MAKE) -f $(FYEAH_MAKE) package PY=$(py);)

build:
	mkdir ./build

ifeq ($(strip $(shell file -b ${HOME}/.pyenv/sources/$(LONG_PYVER))), directory)
# then pyenv built this python and source is avalible

ast.c: build
	if ! file -bh ./build/cpython | grep -q "$(LONG_PYVER)"; then \
		rm -f ./build/cpython; \
	fi
	if [ ! -e ./build/cpython ]; then  \
		ln -s "${HOME}/.pyenv/sources/$(LONG_PYVER)/Python-$(LONG_PYVER)" ./build/cpython; \
	fi

else ifneq ($(strip $(shell git --version)),)
# then use git to get python source

ast.c: build cpython
	if [ $(SHORT_PYVER) != "`git symbolic-ref --short HEAD`" ]; then \
		git -C ./build/cpython/ fetch --all; \
		git -C ./build/cpython/ checkout $(SHORT_PYVER); \
	fi

cpython:
	git clone https://github.com/python/cpython.git --branch $(SHORT_PYVER) ./build/cpython/

else

ast.c:
	# Can't find python source files. Extension module won't be built

endif

ensure:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install --upgrade setuptools wheel twine tox

clean:
	$(PY) setup.py clean --all
	rm -rf *.egg-info **/__pycache__/ .tox/ .pytest_cache/ build/ dist/

test:
	$(PY) -m tox --skip-missing-interpreters --discover /opt/python/*/bin/python
