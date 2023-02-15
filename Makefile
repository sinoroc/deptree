#


source_dir := ./src
tests_dir := ./test


.DEFAULT_GOAL := editable


.PHONY: editable
editable:
	python -m pip install --editable .


.PHONY: package
package: sdist wheel zapp


.PHONY: sdist
sdist:
	python -m build --sdist
	python -m twine check dist/*.tar.gz


.PHONY: wheel
wheel:
	python -m build --wheel
	python -m twine check dist/*.whl


.PHONY: zapp
zapp:
	python setup.py bdist_zapp


.PHONY: format
format:
	python -m yapf --in-place --parallel --recursive setup.py $(source_dir) $(tests_dir)


.PHONY: lint
lint:
	python -m pytest --pycodestyle --pylint --yapf -m 'pycodestyle or pylint or yapf'


.PHONY: pycodestyle
pycodestyle:
	python -m pytest --pycodestyle -m pycodestyle


.PHONY: pylint
pylint:
	python -m pytest --pylint -m pylint


.PHONY: yapf
yapf:
	python -m pytest --yapf -m yapf


.PHONY: test
test: pytest


.PHONY: pytest
pytest:
	python -m pytest


.PHONY: review
review:
	python -m pytest --pycodestyle --pylint --yapf


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
MAKEFLAGS := --no-builtin-rules --warn-undefined-variables
.SUFFIXES:


# EOF
