#


source_dir := ./src
tests_dir := ./test


.DEFAULT_GOAL := develop


.PHONY: develop
develop:
	python3 setup.py develop


.PHONY: package
package: sdist wheel zapp


.PHONY: sdist
sdist:
	python3 setup.py sdist
	python3 -m twine check dist/*.tar.gz


.PHONY: wheel
wheel:
	python3 setup.py bdist_wheel
	python3 -m twine check dist/*.whl


.PHONY: zapp
zapp:
	python3 setup.py bdist_zapp


.PHONY: check
check:
	python3 setup.py check


.PHONY: lint
lint:
	python3 -m pytest --pycodestyle --pylint -m 'pycodestyle or pylint'


.PHONY: pycodestyle
pycodestyle:
	python3 -m pytest --pycodestyle -m pycodestyle


.PHONY: pylint
pylint:
	python3 -m pytest --pylint -m pylint


.PHONY: test
test: pytest


.PHONY: pytest
pytest:
	python3 -m pytest


.PHONY: review
review: check
	python3 -m pytest --pycodestyle --pylint


.PHONY: clean
clean:
	$(RM) --recursive ./.eggs/
	$(RM) --recursive ./.pytest_cache/
	$(RM) --recursive ./build/
	$(RM) --recursive ./dist/
	$(RM) --recursive ./__pycache__/
	find $(source_dir) -name '*.dist-info' -type d -exec $(RM) --recursive {} +
	find $(source_dir) -name '*.egg-info' -type d -exec $(RM) --recursive {} +
	find $(source_dir) -name '*.pyc' -type f -exec $(RM) {} +
	find $(tests_dir) -name '*.pyc' -type f -exec $(RM) {} +
	find $(source_dir) -name '__pycache__' -type d -exec $(RM) --recursive {} +
	find $(tests_dir) -name '__pycache__' -type d -exec $(RM) --recursive {} +


#
# Options
#

# Disable default rules and suffixes (improve speed and avoid unexpected behaviour)
MAKEFLAGS := --no-builtin-rules
.SUFFIXES:


# EOF
