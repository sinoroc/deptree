..


.. contents::

.. sectnum::


Introduction
============

Display installed Python projects as a tree of dependencies.


Features
========

* Output compatible with ``requirements.txt``

* Show dependencies or dependents

* Detect circular dependencies

* Detect missing dependencies


Usage
=====

.. code::

    usage: deptree [-h] [--version] [-r] [-f] [project [project ...]]

    positional arguments:
      project        name of project whose dependencies (or dependents) to show

    optional arguments:
      -h, --help     show this help message and exit
      --version      show program's version number and exit
      -r, --reverse  show dependent projects instead of dependencies
      -f, --flat     show flat list instead of tree


Examples
--------

.. code::

    $ deptree cryptography
    cryptography==2.8  # cryptography
      cffi==1.13.2  # cffi!=1.11.3,>=1.8
        pycparser==2.19  # pycparser
      six==1.13.0  # six>=1.4.1


.. code::

    $ deptree --reverse cryptography
    cryptography==2.8  #
      SecretStorage==3.1.1  # cryptography
        keyring==21.0.0  # secretstorage; sys_platform == "linux"
          twine==3.1.1  # keyring>=15.1


.. code::

    $ deptree --flat cryptography
    cryptography==2.8
    # cffi!=1.11.3,>=1.8
    # six>=1.4.1


.. code::

    $ deptree --flat --reverse cryptography
    # secretstorage cryptography
    cryptography==2.8


Repositories
============

Distributions
-------------

* https://pypi.org/project/deptree/


Source code
-----------

* https://gitlab.com/sinoroc/deptree
* https://github.com/sinoroc/deptree


Details
=======

Similar projects
----------------

* `johnnydep`_
* `pipdeptree`_


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
.. _`johnnydep`: https://pypi.org/project/johnnydep/
.. _`pipdeptree`: https://pypi.org/project/pipdeptree/
.. _`pytest`: https://pytest.org/
.. _`tox`: https://tox.readthedocs.io/


.. EOF
