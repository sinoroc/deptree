#


""" Command line interface
"""


import argparse

from . import _meta
from . import _pkg_resources


def main():
    """ CLI main function
    """
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
    )
    parser.add_argument('--version', action='version', version=_meta.VERSION)
    parser.parse_args()
    _pkg_resources.main()


# EOF
