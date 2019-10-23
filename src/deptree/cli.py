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
    parser.add_argument('-r', '--reverse', action='store_true')
    parser.add_argument('selected_projects', metavar='project', nargs='*')
    args = parser.parse_args()
    _pkg_resources.main(args.selected_projects, args.reverse)


# EOF
