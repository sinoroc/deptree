#!/usr/bin/env python3


""" Setup script """


import os

import setuptools


def _setup():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'CHANGELOG.rst')) as file_:
        changelog = file_.read()

    version = changelog.splitlines()[4]

    setuptools.setup(
        # see 'setup.cfg'
        version=version,
    )


if __name__ == '__main__':
    _setup()


# EOF
