#


""" Command line interface
"""


import argparse

from . import _i18n
from . import _meta
from . import _pkg_resources


_ = _i18n._


def main():
    """ CLI main function
    """
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
    )
    parser.add_argument('--version', action='version', version=_meta.VERSION)
    parser.add_argument(
        '-r', '--reverse',
        action='store_true',
        help=_("show dependent projects instead of dependencies"),
    )
    parser.add_argument(
        'selected_projects',
        help=_("name of project whose dependencies (or dependents) to show"),
        metavar='project',
        nargs='*',
    )
    args = parser.parse_args()
    _pkg_resources.main(args.selected_projects, args.reverse)


# EOF
