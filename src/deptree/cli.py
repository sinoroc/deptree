#

"""Command line interface."""

import argparse
import typing

from . import _i18n
from . import _meta
from . import _pkg_resources

_ = _i18n._


def main() -> int:
    """CLI main function."""
    args_parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description=_meta.get_summary(),
    )
    args_parser.add_argument(
        '--version',
        action='version',
        version=_meta.get_version(),
    )
    args_parser.add_argument(
        '-r',
        '--reverse',
        action='store_true',
        help=_("show dependent projects instead of dependencies"),
    )
    args_parser.add_argument(
        '-f',
        '--flat',
        action='store_true',
        help=_("show flat list instead of tree"),
    )
    args_parser.add_argument(
        'selected_projects',
        help=_("name of project whose dependencies (or dependents) to show"),
        metavar='project',
        nargs='*',
    )
    args = args_parser.parse_args()
    #
    result = _pkg_resources.main(
        typing.cast(typing.List[str], args.selected_projects),
        typing.cast(bool, args.reverse),
        typing.cast(bool, args.flat),
    )
    #
    return result


# EOF
