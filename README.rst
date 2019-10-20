..


.. contents::

.. sectnum::


Introduction
============

Display installed Python projects as a tree of dependencies.


Usage
=====

.. code::

    usage: deptree [-h] [--version] [project [project ...]]

    positional arguments:
      project

    optional arguments:
      -h, --help  show this help message and exit
      --version   show program's version number and exit


Repositories
============

Distributions
-------------

* https://pypi.org/project/deptree/


Source code
-----------

* https://gitlab.com/sinoroc/deptree
* https://github.com/sinoroc/deptree


Hacking
=======

This project makes extensive use of `tox`_, `pytest`_, and `GNU Make`_.


Development environment
-----------------------

Use following command to create a Python virtual environment with all
necessary dependencies::

    tox --recreate -e develop

This creates a Python virtual environment in the ``.tox/develop`` directory. It
can be activated with the following command::

    . .tox/develop/bin/activate


Run test suite
--------------

In a Python virtual environment run the following command::

    make review

Outside of a Python virtual environment run the following command::

    tox --recreate


Build and package
-----------------

In a Python virtual environment run the following command::

    make package

Outside of a Python virtual environment run the following command::

    tox --recreate -e package


.. Links

.. _`GNU Make`: https://www.gnu.org/software/make/
.. _`pytest`: https://pytest.org/
.. _`tox`: https://tox.readthedocs.io/


.. EOF
