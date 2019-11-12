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

* Detects circular dependencies

* Detects missing dependencies


Usage
=====

.. code::

    usage: deptree [-h] [--version] [-r] [project [project ...]]

    positional arguments:
      project        name of project whose dependencies (or dependents) to show

    optional arguments:
      -h, --help     show this help message and exit
      --version      show program's version number and exit
      -r, --reverse  show dependent projects instead of dependencies


Examples
--------

.. code::

    $ deptree twine
    twine==2.0.0  # twine
      pkginfo==1.5.0.1  # pkginfo>=1.4.2
      readme-renderer==24.0  # readme-renderer>=21.0
        bleach==3.1.0  # bleach>=2.1.0
          six==1.13.0  # six>=1.9.0
          webencodings==0.5.1  # webencodings
        docutils==0.15.2  # docutils>=0.13.1
        Pygments==2.4.2  # Pygments
        six==1.13.0  # six
      requests==2.22.0  # requests>=2.20
        certifi==2019.9.11  # certifi>=2017.4.17
        chardet==3.0.4  # chardet<3.1.0,>=3.0.2
        idna==2.8  # idna<2.9,>=2.5
        urllib3==1.25.7  # urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1
      requests-toolbelt==0.9.1  # requests-toolbelt!=0.9.0,>=0.8.0
        requests==2.22.0  # requests<3.0.0,>=2.0.1
          certifi==2019.9.11  # certifi>=2017.4.17
          chardet==3.0.4  # chardet<3.1.0,>=3.0.2
          idna==2.8  # idna<2.9,>=2.5
          urllib3==1.25.7  # urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1
      setuptools==39.0.1  # setuptools>=0.7.0
      tqdm==4.38.0  # tqdm>=4.14

.. code::

    $ deptree -r requests
    requests==2.22.0  #
      requests-toolbelt==0.9.1  # requests<3.0.0,>=2.0.1
        twine==2.0.0  # requests-toolbelt!=0.9.0,>=0.8.0
      twine==2.0.0  # requests>=2.20


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
.. _`pipdeptree`: https://pypi.org/project/pipdeptree/
.. _`pytest`: https://pytest.org/
.. _`tox`: https://tox.readthedocs.io/


.. EOF
