..


Introduction
============

Display installed Python projects as a tree of dependencies.


Features
--------

* Output compatible with ``requirements.txt``

* Show dependencies or dependents

* Detect circular dependencies

* Detect missing dependencies


Repositories
------------

Distributions:

* https://pypi.org/project/deptree/


Source code:

* https://gitlab.com/sinoroc/deptree
* https://github.com/sinoroc/deptree


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


Installation
------------

For better comfort, use as a single-file isolated *zipapp*:

* https://www.python.org/dev/peps/pep-0441/
* https://docs.python.org/3/library/zipapp.html


For example:

.. code::

    $ python3 -m pip install --target ./deptree/ deptree
    $ python3 -m zipapp --python '/usr/bin/env python3' --main 'deptree.cli:main' ./deptree/
    $ mv ./deptree.pyz ~/.local/bin/deptree


Or use `zapp`_, or `toolmaker`_.

This way the tool can be used in virtual environments without installing it in
the virtual environments. The tool can then see the projects installed in the
virtual environment but without seeing itself.


Details
=======

Similar projects
----------------

* `johnnydep`_
* `pipdeptree`_


.. Links

.. _`johnnydep`: https://pypi.org/project/johnnydep/
.. _`pipdeptree`: https://pypi.org/project/pipdeptree/
.. _`toolmaker`: https://pypi.org/project/toolmaker/
.. _`zapp`: https://pypi.org/project/zapp/


.. EOF
